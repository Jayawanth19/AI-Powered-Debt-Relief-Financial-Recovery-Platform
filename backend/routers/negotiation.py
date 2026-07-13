from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import ai_service

router = APIRouter(prefix="/api/negotiation", tags=["Negotiation"])


@router.post("/generate", response_model=schemas.NegotiationHistoryOut, status_code=201)
def generate_negotiation(payload: schemas.NegotiationRequest, db: Session = Depends(get_db)):
    """
    Scenario 2: Intelligent Negotiation Letter Generation.
    Uses (or computes fresh) financial metrics for the loan, then asks Gemini
    to draft a lender-specific negotiation letter/email/hardship letter.
    """
    loan = db.query(models.Loan).filter(models.Loan.id == payload.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    borrower = loan.borrower

    # Reuse the most recent recommendation if one exists, else compute fresh metrics
    latest_rec = (
        db.query(models.SettlementRecommendation)
        .filter(models.SettlementRecommendation.loan_id == loan.id)
        .order_by(models.SettlementRecommendation.created_at.desc())
        .first()
    )
    if latest_rec:
        metrics = {
            "emi_to_income_ratio": latest_rec.emi_to_income_ratio,
            "monthly_surplus": latest_rec.monthly_surplus,
            "debt_stress_level": latest_rec.debt_stress_level,
            "recommended_settlement_pct": latest_rec.recommended_settlement_pct,
            "recommended_settlement_amount": latest_rec.recommended_settlement_amount,
            "recommended_tenure_months": latest_rec.recommended_tenure_months,
        }
    else:
        metrics = ai_service.compute_financial_metrics(
            outstanding_amount=loan.outstanding_amount,
            emi_amount=loan.emi_amount,
            overdue_months=loan.overdue_months,
            monthly_income=borrower.monthly_income,
        )

    content = ai_service.generate_negotiation_content(
        lender_name=loan.lender_name,
        loan_type=loan.loan_type,
        outstanding_amount=loan.outstanding_amount,
        emi_amount=loan.emi_amount,
        overdue_months=loan.overdue_months,
        monthly_income=borrower.monthly_income,
        metrics=metrics,
        negotiation_type=payload.negotiation_type,
        tone=payload.tone,
        additional_context=payload.additional_context,
        borrower_name=borrower.name,
    )

    record = models.NegotiationHistory(
        loan_id=loan.id,
        negotiation_type=payload.negotiation_type,
        tone=payload.tone,
        generated_content=content,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/history/{loan_id}", response_model=list[schemas.NegotiationHistoryOut])
def get_negotiation_history(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return (
        db.query(models.NegotiationHistory)
        .filter(models.NegotiationHistory.loan_id == loan_id)
        .order_by(models.NegotiationHistory.created_at.desc())
        .all()
    )
