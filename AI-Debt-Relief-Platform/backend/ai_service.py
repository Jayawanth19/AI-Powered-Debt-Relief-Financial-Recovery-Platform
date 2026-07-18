"""
ai_service.py
--------------
Wraps Google Gemini API calls for:
  1. Debt-stress / settlement analysis (financial reasoning + narrative summary)
  2. Negotiation letter / email generation

Responsible-AI notes:
  - The model NEVER makes a binding legal/financial decision on behalf of the
    user; all output is framed as a "recommendation" for the borrower to review.
  - Numeric settlement math is computed deterministically in Python
    (see `compute_financial_metrics`) and only the *narrative explanation* is
    delegated to the LLM. This avoids hallucinated numbers in a financial
    context.
  - If the Gemini API key is missing or a call fails, the service falls back
    to a rule-based template so the app keeps working (graceful degradation).
"""

import os
import json
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_service")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

_gemini_enabled = False
try:
    import google.generativeai as genai

    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_enabled = True
except ImportError:  # library not installed
    logger.warning("google-generativeai not installed; running in fallback mode.")


def _call_gemini(prompt: str, temperature: float = 0.4) -> Optional[str]:
    """Low level helper to call Gemini. Returns None on any failure."""
    if not _gemini_enabled:
        return None
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": temperature, "max_output_tokens": 1024},
        )
        return response.text.strip()
    except Exception as exc:  # noqa: BLE001
        logger.error("Gemini call failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# 1. Deterministic financial metrics (no LLM involved -> trustworthy numbers)
# ---------------------------------------------------------------------------

def compute_financial_metrics(
    outstanding_amount: float,
    emi_amount: float,
    overdue_months: int,
    monthly_income: float,
) -> dict:
    """Pure-python calculation of debt stress + a suggested settlement plan."""

    emi_to_income_ratio = round((emi_amount / monthly_income) * 100, 2) if monthly_income else 0.0
    monthly_surplus = round(monthly_income - emi_amount, 2)

    # Debt stress heuristic (transparent, explainable rules)
    if emi_to_income_ratio >= 60 or overdue_months >= 6:
        stress_level = "Critical"
        settlement_pct = 45
        tenure_months = 3
    elif emi_to_income_ratio >= 45 or overdue_months >= 3:
        stress_level = "High"
        settlement_pct = 60
        tenure_months = 6
    elif emi_to_income_ratio >= 30 or overdue_months >= 1:
        stress_level = "Moderate"
        settlement_pct = 75
        tenure_months = 9
    else:
        stress_level = "Low"
        settlement_pct = 90
        tenure_months = 12

    recommended_settlement_amount = round(outstanding_amount * settlement_pct / 100, 2)

    return {
        "emi_to_income_ratio": emi_to_income_ratio,
        "monthly_surplus": monthly_surplus,
        "debt_stress_level": stress_level,
        "recommended_settlement_pct": settlement_pct,
        "recommended_settlement_amount": recommended_settlement_amount,
        "recommended_tenure_months": tenure_months,
    }


# ---------------------------------------------------------------------------
# 2. AI narrative summary for the settlement recommendation
# ---------------------------------------------------------------------------

def generate_settlement_summary(
    lender_name: str,
    metrics: dict,
    outstanding_amount: float,
    emi_amount: float,
    overdue_months: int,
    monthly_income: float,
) -> str:
    prompt = f"""
You are a responsible financial wellness assistant helping a borrower understand
their debt situation. You are NOT a lawyer or licensed financial advisor, and
your response must read like helpful guidance, not a guarantee or legal advice.

Borrower financial snapshot:
- Lender: {lender_name}
- Outstanding amount: {outstanding_amount}
- Monthly EMI: {emi_amount}
- Overdue months: {overdue_months}
- Monthly income: {monthly_income}
- EMI-to-income ratio: {metrics['emi_to_income_ratio']}%
- Monthly surplus after EMI: {metrics['monthly_surplus']}
- Computed debt stress level: {metrics['debt_stress_level']}
- Suggested settlement: {metrics['recommended_settlement_pct']}% of outstanding
  (~{metrics['recommended_settlement_amount']}) over {metrics['recommended_tenure_months']} months

Write a short (120-160 words), empathetic, plain-language summary that:
1. Explains what the debt stress level means for this borrower.
2. Explains the reasoning behind the suggested settlement percentage and tenure.
3. Gives 2 practical next-step tips for improving their position before negotiating.
4. Ends with one sentence reminding them this is an AI-generated suggestion and
   they should confirm final terms with the lender/a financial advisor.

Do not invent numbers beyond what is given above. Do not use markdown headers.
"""
    text = _call_gemini(prompt, temperature=0.5)
    if text:
        return text

    # ---- Fallback (rule-based) if Gemini is unavailable ----
    return (
        f"Based on your current EMI-to-income ratio of {metrics['emi_to_income_ratio']}% "
        f"and {overdue_months} overdue month(s), your debt stress level is classified as "
        f"{metrics['debt_stress_level']}. We suggest proposing a settlement of about "
        f"{metrics['recommended_settlement_pct']}% of the outstanding amount "
        f"(~{metrics['recommended_settlement_amount']}) spread over "
        f"{metrics['recommended_tenure_months']} months to {lender_name}. "
        "Consider trimming discretionary expenses and building a small emergency buffer "
        "before starting negotiations, and try to make any partial payment you can "
        "before contacting the lender to strengthen your position. "
        "This is an AI-generated suggestion only — please confirm final terms directly "
        "with your lender or a licensed financial advisor. "
        "(Note: AI narrative generation is currently running in offline fallback mode.)"
    )


# ---------------------------------------------------------------------------
# 3. Negotiation letter / email generation
# ---------------------------------------------------------------------------

def generate_negotiation_content(
    lender_name: str,
    loan_type: str,
    outstanding_amount: float,
    emi_amount: float,
    overdue_months: int,
    monthly_income: float,
    metrics: dict,
    negotiation_type: str = "settlement_letter",
    tone: str = "professional",
    additional_context: Optional[str] = None,
    borrower_name: str = "the borrower",
) -> str:
    type_instructions = {
        "settlement_letter": "a formal one-time settlement request letter",
        "email": "a concise negotiation email suitable for sending directly to the lender's collections/customer service address",
        "hardship_letter": "a financial hardship letter explaining the borrower's circumstances and requesting relief (reduced EMI, tenure extension, or settlement)",
    }
    doc_description = type_instructions.get(negotiation_type, type_instructions["settlement_letter"])

    prompt = f"""
You are drafting {doc_description} on behalf of a borrower named {borrower_name},
addressed to the lender "{lender_name}", regarding their {loan_type}.

Tone requested: {tone}.

Facts to use (do not invent additional facts or numbers):
- Outstanding amount: {outstanding_amount}
- Monthly EMI: {emi_amount}
- Overdue months: {overdue_months}
- Monthly income: {monthly_income}
- Suggested settlement offer: {metrics['recommended_settlement_pct']}% of outstanding
  (~{metrics['recommended_settlement_amount']}) payable over {metrics['recommended_tenure_months']} months
{"- Additional context from borrower: " + additional_context if additional_context else ""}

Write the full letter/email now, including a greeting and sign-off placeholder
"[Your Name]". Keep it realistic, respectful, and non-confrontational. Do not
make legal threats or guarantees. Do not include markdown formatting, just
plain text suitable for pasting into an email client or document.
"""
    text = _call_gemini(prompt, temperature=0.6)
    if text:
        return text

    # ---- Fallback template ----
    return (
        f"Subject: Settlement Request Regarding {loan_type} Account with {lender_name}\n\n"
        f"Dear {lender_name} Team,\n\n"
        f"I am writing regarding my {loan_type} account, currently overdue by "
        f"{overdue_months} month(s) with an outstanding balance of {outstanding_amount}. "
        f"Due to a temporary financial constraint, I am finding it difficult to continue "
        f"the current EMI of {emi_amount}.\n\n"
        f"I would like to propose a one-time settlement of approximately "
        f"{metrics['recommended_settlement_amount']} "
        f"({metrics['recommended_settlement_pct']}% of the outstanding amount), payable over "
        f"{metrics['recommended_tenure_months']} months. I believe this reflects a fair "
        "resolution given my current income and expenses.\n\n"
        "I would appreciate the opportunity to discuss this proposal further and reach an "
        "arrangement that works for both parties.\n\n"
        "Thank you for your understanding.\n\n"
        "Sincerely,\n[Your Name]\n\n"
        "(Note: AI narrative generation is currently running in offline fallback mode.)"
    )
