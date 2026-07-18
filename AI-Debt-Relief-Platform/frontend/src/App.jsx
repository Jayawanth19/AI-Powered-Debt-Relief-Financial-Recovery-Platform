import React, { useState, useEffect } from "react";
import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import Onboarding from "./pages/Onboarding.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Loans from "./pages/Loans.jsx";
import LoanDetail from "./pages/LoanDetail.jsx";
import AddLoan from "./pages/AddLoan.jsx";

const BORROWER_KEY = "debtrelief_borrower_id";

export default function App() {
  const [borrowerId, setBorrowerId] = useState(() => localStorage.getItem(BORROWER_KEY));

  useEffect(() => {
    if (borrowerId) localStorage.setItem(BORROWER_KEY, borrowerId);
  }, [borrowerId]);

  if (!borrowerId) {
    return <Onboarding onCreated={(id) => setBorrowerId(String(id))} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>
          AI Debt <span>Relief</span>
        </h1>
        <NavLink to="/" end className="nav-link">Dashboard</NavLink>
        <NavLink to="/loans" className="nav-link">My Loans</NavLink>
        <NavLink to="/add-loan" className="nav-link">Add Loan</NavLink>
        <button
          className="secondary"
          style={{ marginTop: 24, width: "100%" }}
          onClick={() => {
            localStorage.removeItem(BORROWER_KEY);
            setBorrowerId(null);
          }}
        >
          Switch Borrower
        </button>
      </aside>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard borrowerId={borrowerId} />} />
          <Route path="/loans" element={<Loans borrowerId={borrowerId} />} />
          <Route path="/loans/:loanId" element={<LoanDetail />} />
          <Route path="/add-loan" element={<AddLoan borrowerId={borrowerId} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
