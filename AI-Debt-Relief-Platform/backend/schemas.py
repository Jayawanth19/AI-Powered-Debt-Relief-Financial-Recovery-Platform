from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ---------- Borrower ----------

class BorrowerCreate(BaseModel):
    name: str
    email: EmailStr
    monthly_income: float = Field(gt=0)


class BorrowerOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    monthly_income: float
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Loan ----------

class LoanCreate(BaseModel):
    borrower_id: int
    lender_name: str
    loan_type: str = "Personal Loan"
    outstanding_amount: float = Field(gt=0)
    emi_amount: float = Field(gt=0)
    overdue_months: int = Field(ge=0, default=0)
    interest_rate: float = Field(ge=0, default=0.0)


class LoanUpdate(BaseModel):
    lender_name: Optional[str] = None
    loan_type: Optional[str] = None
    outstanding_amount: Optional[float] = None
    emi_amount: Optional[float] = None
    overdue_months: Optional[int] = None
    interest_rate: Optional[float] = None
    status: Optional[str] = None


class LoanOut(BaseModel):
    id: int
    borrower_id: int
    lender_name: str
    loan_type: str
    outstanding_amount: float
    emi_amount: float
    overdue_months: int
    interest_rate: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Settlement Recommendation ----------

class SettlementRecommendationOut(BaseModel):
    id: int
    loan_id: int
    debt_stress_level: str
    emi_to_income_ratio: float
    monthly_surplus: float
    recommended_settlement_pct: float
    recommended_settlement_amount: float
    recommended_tenure_months: int
    ai_summary: str
    created_at: datetime

    class Config:
        from_attributes = True


class SettlementRequest(BaseModel):
    loan_id: int


# ---------- Negotiation ----------

class NegotiationRequest(BaseModel):
    loan_id: int
    negotiation_type: str = "settlement_letter"  # settlement_letter, email, hardship_letter
    tone: str = "professional"                    # professional, empathetic, firm
    additional_context: Optional[str] = None


class NegotiationHistoryOut(BaseModel):
    id: int
    loan_id: int
    negotiation_type: str
    tone: str
    generated_content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard ----------

class FinancialHealthOut(BaseModel):
    borrower_id: int
    total_outstanding: float
    total_emi: float
    monthly_income: float
    emi_to_income_ratio: float
    monthly_surplus: float
    debt_stress_level: str
    active_loans: int
    settled_loans: int
    average_settlement_pct: Optional[float] = None


class DashboardOut(BaseModel):
    borrower: BorrowerOut
    financial_health: FinancialHealthOut
    loans: List[LoanOut]
    recent_negotiations: List[NegotiationHistoryOut]
