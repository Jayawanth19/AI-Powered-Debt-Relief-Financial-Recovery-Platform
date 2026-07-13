import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createLoan } from "../api/client.js";

export default function AddLoan({ borrowerId }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    lender_name: "",
    loan_type: "Personal Loan",
    outstanding_amount: "",
    emi_amount: "",
    overdue_months: 0,
    interest_rate: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const loan = await createLoan({
        borrower_id: parseInt(borrowerId, 10),
        ...form,
        outstanding_amount: parseFloat(form.outstanding_amount),
        emi_amount: parseFloat(form.emi_amount),
        overdue_months: parseInt(form.overdue_months, 10) || 0,
        interest_rate: parseFloat(form.interest_rate) || 0,
      });
      navigate(`/loans/${loan.id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to add loan.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Add a Loan</h2>
      <form className="card" style={{ maxWidth: 500 }} onSubmit={handleSubmit}>
        <label>Lender name</label>
        <input
          required
          value={form.lender_name}
          onChange={(e) => setForm({ ...form, lender_name: e.target.value })}
          placeholder="e.g. HDFC Bank"
        />

        <label>Loan type</label>
        <select value={form.loan_type} onChange={(e) => setForm({ ...form, loan_type: e.target.value })}>
          <option>Personal Loan</option>
          <option>Credit Card</option>
          <option>Home Loan</option>
          <option>Auto Loan</option>
          <option>Education Loan</option>
          <option>Business Loan</option>
        </select>

        <label>Outstanding amount (₹)</label>
        <input
          required
          type="number"
          min="1"
          step="0.01"
          value={form.outstanding_amount}
          onChange={(e) => setForm({ ...form, outstanding_amount: e.target.value })}
        />

        <label>Monthly EMI (₹)</label>
        <input
          required
          type="number"
          min="1"
          step="0.01"
          value={form.emi_amount}
          onChange={(e) => setForm({ ...form, emi_amount: e.target.value })}
        />

        <label>Overdue duration (months)</label>
        <input
          type="number"
          min="0"
          value={form.overdue_months}
          onChange={(e) => setForm({ ...form, overdue_months: e.target.value })}
        />

        <label>Interest rate (% p.a., optional)</label>
        <input
          type="number"
          min="0"
          step="0.01"
          value={form.interest_rate}
          onChange={(e) => setForm({ ...form, interest_rate: e.target.value })}
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary" type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save Loan"}
        </button>
      </form>
    </div>
  );
}
