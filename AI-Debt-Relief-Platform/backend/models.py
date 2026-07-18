from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from database import Base


class Borrower(Base):
    """Represents a borrower/user of the platform."""
    __tablename__ = "borrowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    monthly_income = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="borrower", cascade="all, delete-orphan")


class Loan(Base):
    """Represents a single loan/debt account belonging to a borrower."""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.id"), nullable=False)

    lender_name = Column(String, nullable=False)
    loan_type = Column(String, default="Personal Loan")
    outstanding_amount = Column(Float, nullable=False)
    emi_amount = Column(Float, nullable=False)
    overdue_months = Column(Integer, default=0)
    interest_rate = Column(Float, default=0.0)

    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    borrower = relationship("Borrower", back_populates="loans")
    negotiations = relationship("NegotiationHistory", back_populates="loan", cascade="all, delete-orphan")
    recommendations = relationship("SettlementRecommendation", back_populates="loan", cascade="all, delete-orphan")


class SettlementRecommendation(Base):
    """Stores the AI-generated settlement/financial-health analysis for a loan."""
    __tablename__ = "settlement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)

    debt_stress_level = Column(String)
    emi_to_income_ratio = Column(Float)
    monthly_surplus = Column(Float)
    recommended_settlement_pct = Column(Float)
    recommended_settlement_amount = Column(Float)
    recommended_tenure_months = Column(Integer)
    ai_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    loan = relationship("Loan", back_populates="recommendations")


class NegotiationHistory(Base):
    """Stores each AI-generated negotiation letter/email for auditing and history."""
    __tablename__ = "negotiation_history"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)

    negotiation_type = Column(String, default="settlement_letter")
    tone = Column(String, default="professional")
    generated_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    loan = relationship("Loan", back_populates="negotiations")
