from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import ai_service

router = APIRouter(prefix="/api/loans", tags=["Loans"])


@router.post("/", response_model=schemas.LoanOut, status_code=201)
def create_loan(payload: schemas.LoanCreate, db: Session = Depends(get_db)):
    borrower = db.query(models.Borrower).filter(models.Borrower.id == payload.borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    loan = models.Loan(**payload.model_dump())
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.get("/", response_model=list[schemas.LoanOut])
def list_loans(borrower_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Loan)
    if borrower_id is not None:
        query = query.filter(models.Loan.borrower_id == borrower_id)
    return query.order_by(models.Loan.created_at.desc()).all()


@router.get("/{loan_id}", response_model=schemas.LoanOut)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.patch("/{loan_id}", response_model=schemas.LoanOut)
def update_loan(loan_id: int, payload: schemas.LoanUpdate, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(loan, field, value)

    db.commit()
    db.refresh(loan)
    return loan


@router.delete("/{loan_id}", status_code=204)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return None


@router.post("/{loan_id}/settlement-recommendation", response_model=schemas.SettlementRecommendationOut)
def generate_settlement_recommendation(loan_id: int, db: Session = Depends(get_db)):
    """
    Scenario 1: AI-Powered Settlement Recommendation.
    Computes deterministic financial metrics, then asks Gemini for a
    plain-language narrative summary, and persists both.
    """
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    borrower = loan.borrower
    metrics = ai_service.compute_financial_metrics(
        outstanding_amount=loan.outstanding_amount,
        emi_amount=loan.emi_amount,
        overdue_months=loan.overdue_months,
        monthly_income=borrower.monthly_income,
    )

    summary = ai_service.generate_settlement_summary(
        lender_name=loan.lender_name,
        metrics=metrics,
        outstanding_amount=loan.outstanding_amount,
        emi_amount=loan.emi_amount,
        overdue_months=loan.overdue_months,
        monthly_income=borrower.monthly_income,
    )

    recommendation = models.SettlementRecommendation(
        loan_id=loan.id,
        debt_stress_level=metrics["debt_stress_level"],
        emi_to_income_ratio=metrics["emi_to_income_ratio"],
        monthly_surplus=metrics["monthly_surplus"],
        recommended_settlement_pct=metrics["recommended_settlement_pct"],
        recommended_settlement_amount=metrics["recommended_settlement_amount"],
        recommended_tenure_months=metrics["recommended_tenure_months"],
        ai_summary=summary,
    )
    db.add(recommendation)

    loan.status = "in_negotiation" if loan.status == "active" else loan.status

    db.commit()
    db.refresh(recommendation)
    return recommendation


@router.get("/{loan_id}/settlement-recommendation", response_model=list[schemas.SettlementRecommendationOut])
def get_settlement_recommendations(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return (
        db.query(models.SettlementRecommendation)
        .filter(models.SettlementRecommendation.loan_id == loan_id)
        .order_by(models.SettlementRecommendation.created_at.desc())
        .all()
    )
