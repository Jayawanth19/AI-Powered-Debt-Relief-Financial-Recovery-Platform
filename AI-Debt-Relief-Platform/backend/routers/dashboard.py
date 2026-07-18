from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import ai_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/{borrower_id}", response_model=schemas.DashboardOut)
def get_dashboard(borrower_id: int, db: Session = Depends(get_db)):
    """
    Scenario 3: Financial Health Tracking & Loan Analysis.
    Aggregates all loans for a borrower into overall financial health metrics,
    plus recent AI negotiation history.
    """
    borrower = db.query(models.Borrower).filter(models.Borrower.id == borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")

    loans = db.query(models.Loan).filter(models.Loan.borrower_id == borrower_id).all()

    total_outstanding = sum(l.outstanding_amount for l in loans)
    total_emi = sum(l.emi_amount for l in loans if l.status != "settled")
    active_loans = sum(1 for l in loans if l.status in ("active", "in_negotiation"))
    settled_loans = sum(1 for l in loans if l.status == "settled")

    overall_metrics = ai_service.compute_financial_metrics(
        outstanding_amount=total_outstanding or 0.0,
        emi_amount=total_emi or 0.0,
        overdue_months=max((l.overdue_months for l in loans), default=0),
        monthly_income=borrower.monthly_income,
    )

    all_recs = (
        db.query(models.SettlementRecommendation)
        .join(models.Loan, models.SettlementRecommendation.loan_id == models.Loan.id)
        .filter(models.Loan.borrower_id == borrower_id)
        .all()
    )
    avg_settlement_pct = (
        round(sum(r.recommended_settlement_pct for r in all_recs) / len(all_recs), 2)
        if all_recs else None
    )

    recent_negotiations = (
        db.query(models.NegotiationHistory)
        .join(models.Loan, models.NegotiationHistory.loan_id == models.Loan.id)
        .filter(models.Loan.borrower_id == borrower_id)
        .order_by(models.NegotiationHistory.created_at.desc())
        .limit(10)
        .all()
    )

    financial_health = schemas.FinancialHealthOut(
        borrower_id=borrower_id,
        total_outstanding=total_outstanding,
        total_emi=total_emi,
        monthly_income=borrower.monthly_income,
        emi_to_income_ratio=overall_metrics["emi_to_income_ratio"],
        monthly_surplus=overall_metrics["monthly_surplus"],
        debt_stress_level=overall_metrics["debt_stress_level"],
        active_loans=active_loans,
        settled_loans=settled_loans,
        average_settlement_pct=avg_settlement_pct,
    )

    return schemas.DashboardOut(
        borrower=borrower,
        financial_health=financial_health,
        loans=loans,
        recent_negotiations=recent_negotiations,
    )
