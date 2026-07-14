# AI-Powered Debt Relief & Financial Recovery Platform

An intelligent, AI-powered web application that helps borrowers manage loan
details, analyze their financial health, generate AI-driven negotiation
strategies, and receive adaptive settlement recommendations — all through a
secure, modern web interface.

Built with **React.js**, **FastAPI**, **Python**, **SQLite**, **SQLAlchemy
ORM**, and the **Google Gemini API**.

---

## ✨ Features

| Scenario | Description |
|---|---|
| **1. AI-Powered Settlement Recommendation** | Borrower enters outstanding amount, EMI, overdue duration, and income → system computes debt-stress metrics and asks Gemini to generate a plain-language settlement recommendation. |
| **2. Intelligent Negotiation Letter Generation** | Borrower selects a loan → platform uses Gemini to draft a lender-specific settlement letter, negotiation email, or hardship letter. |
| **3. Financial Health Tracking & Loan Analysis** | Dashboard surfaces EMI-to-income ratio, monthly surplus, debt stress level, settlement history, and past AI negotiation activity. |

---

## 🏗️ Architecture

```
ai-debt-relief-platform/
├── backend/                  FastAPI application
│   ├── main.py                App entrypoint, CORS, router registration
│   ├── database.py            SQLAlchemy engine/session (SQLite)
│   ├── models.py              ORM models: Borrower, Loan, SettlementRecommendation, NegotiationHistory
│   ├── schemas.py             Pydantic request/response schemas
│   ├── ai_service.py          Gemini API wrapper + deterministic financial math + fallback templates
│   ├── routers/
│   │   ├── borrowers.py       Borrower CRUD
│   │   ├── loans.py           Loan CRUD + settlement recommendation endpoint
│   │   ├── negotiation.py     Negotiation letter generation + history
│   │   └── dashboard.py       Aggregated financial-health dashboard
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 React (Vite) single-page app
    ├── src/
    │   ├── api/client.js       Axios client for all backend endpoints
    │   ├── pages/              Onboarding, Dashboard, Loans, LoanDetail, AddLoan
    │   ├── App.jsx              Routing + sidebar shell
    │   └── index.css            Dark, modern UI theme
    ├── package.json
    └── .env.example
```

### Why the numbers are computed in Python, not by the LLM
`ai_service.compute_financial_metrics()` performs the EMI-to-income ratio,
monthly surplus, debt-stress classification, and settlement percentage
**deterministically in Python**. Gemini is only used to turn those numbers
into a clear, empathetic narrative explanation and to draft negotiation
letters. This keeps the financial math auditable and avoids LLM hallucination
in a money-related context — a core "Responsible AI" principle for this
project.

If `GEMINI_API_KEY` is not configured, `ai_service.py` automatically falls
back to rule-based templates so the app remains fully functional for demos
and local development without an API key.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Google Gemini API key (optional but recommended) — get one free at
  https://aistudio.google.com/app/apikey

### 1. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit .env and add your GEMINI_API_KEY

uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`. SQLite tables are created automatically on
first run (`debt_relief.db`).

### 2. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env             # defaults to http://localhost:8000

npm run dev
```

Visit `http://localhost:5173` in your browser.

### 3. Using the app
1. Create your borrower profile (name, email, monthly income).
2. Add one or more loans (lender, outstanding amount, EMI, overdue months).
3. Open a loan → click **Generate New Analysis** for an AI settlement
   recommendation.
4. Use **Generate Negotiation Letter** to draft a settlement letter,
   negotiation email, or hardship letter tailored to that loan.
5. Check the **Dashboard** for your overall financial health snapshot and
   recent AI activity.

---

## 🔌 API Reference (summary)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/borrowers/` | Create borrower profile |
| GET | `/api/borrowers/{id}` | Get borrower |
| POST | `/api/loans/` | Add a loan |
| GET | `/api/loans/?borrower_id=` | List loans |
| PATCH | `/api/loans/{id}` | Update a loan |
| DELETE | `/api/loans/{id}` | Delete a loan |
| POST | `/api/loans/{id}/settlement-recommendation` | Generate AI settlement recommendation |
| GET | `/api/loans/{id}/settlement-recommendation` | List past recommendations |
| POST | `/api/negotiation/generate` | Generate negotiation letter/email |
| GET | `/api/negotiation/history/{loan_id}` | Negotiation history for a loan |
| GET | `/api/dashboard/{borrower_id}` | Aggregated financial health dashboard |

Full interactive documentation (Swagger UI) is auto-generated by FastAPI at
`/docs`.

---

## 🔒 Responsible AI Notes
- All AI-generated settlement suggestions and letters are clearly framed as
  **recommendations**, not binding legal or financial advice.
- Core financial calculations are deterministic and auditable; the LLM is
  only used for narrative generation.
- Every prompt to Gemini explicitly instructs the model not to invent
  numbers beyond what's provided.
- Graceful fallback templates ensure the app works (with a visible notice)
  even if the Gemini API is unavailable or misconfigured.

---

## 🛠️ Tech Stack
- **Frontend:** React 18, React Router, Axios, Vite
- **Backend:** FastAPI, SQLAlchemy ORM, Pydantic
- **Database:** SQLite (swap `DATABASE_URL` for Postgres/MySQL in production)
- **AI:** Google Gemini API (`google-generativeai`)

---

## 📦 Deployment Notes
- Backend: deployable to Render, Railway, Fly.io, or any ASGI-compatible host
  (`uvicorn main:app`).
- Frontend: `npm run build` produces a static `dist/` folder deployable to
  Netlify, Vercel, or GitHub Pages. Set `VITE_API_BASE_URL` to your deployed
  backend URL.
- For production, replace SQLite with a managed Postgres/MySQL instance and
  add Alembic migrations.

---

Google Drive Link :https://drive.google.com/drive/folders/1yHz4EaH_v0JtSNqe_K9_L0FuYkeucRyi?usp=sharing

## 📄 License
This project is provided as-is for educational and portfolio purposes.
