import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard } from "../api/client.js";

const stressBadgeClass = (level) => {
  switch (level) {
    case "Low": return "badge badge-low";
    case "Moderate": return "badge badge-moderate";
    case "High": return "badge badge-high";
    default: return "badge badge-critical";
  }
};

export default function Dashboard({ borrowerId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard(borrowerId)
      .then(setData)
      .catch((err) => setError(err?.response?.data?.detail || "Failed to load dashboard"));
  }, [borrowerId]);

  if (error) return <p className="error-text">{error}</p>;
  if (!data) return <p>Loading dashboard...</p>;

  const { borrower, financial_health, loans, recent_negotiations } = data;

  return (
    <div>
      <h2>Welcome back, {borrower.name.split(" ")[0]}</h2>
      <p style={{ color: "var(--text-dim)" }}>Here's your current financial health snapshot.</p>

      <div className="grid grid-4">
        <div className="stat-card">
          <div className="stat-label">Total Outstanding</div>
          <div className="stat-value">₹{financial_health.total_outstanding.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Monthly EMI</div>
          <div className="stat-value">₹{financial_health.total_emi.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Monthly Surplus</div>
          <div className="stat-value">₹{financial_health.monthly_surplus.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">EMI-to-Income Ratio</div>
          <div className="stat-value">{financial_health.emi_to_income_ratio}%</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div className="stat-label">Debt Stress Level</div>
            <span className={stressBadgeClass(financial_health.debt_stress_level)} style={{ marginTop: 8, display: "inline-block" }}>
              {financial_health.debt_stress_level}
            </span>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="stat-label">Active / Settled Loans</div>
            <div className="stat-value">{financial_health.active_loans} / {financial_health.settled_loans}</div>
          </div>
          {financial_health.average_settlement_pct != null && (
            <div style={{ textAlign: "right" }}>
              <div className="stat-label">Avg. Suggested Settlement</div>
              <div className="stat-value">{financial_health.average_settlement_pct}%</div>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Your Loans</h3>
        {loans.length === 0 ? (
          <p className="hint-text">No loans added yet. <Link to="/add-loan">Add your first loan</Link>.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Lender</th>
                <th>Type</th>
                <th>Outstanding</th>
                <th>EMI</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loans.map((loan) => (
                <tr key={loan.id} className="loan-row" onClick={() => (window.location.href = `/loans/${loan.id}`)}>
                  <td>{loan.lender_name}</td>
                  <td>{loan.loan_type}</td>
                  <td>₹{loan.outstanding_amount.toLocaleString()}</td>
                  <td>₹{loan.emi_amount.toLocaleString()}</td>
                  <td>{loan.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Recent AI Negotiation Activity</h3>
        {recent_negotiations.length === 0 ? (
          <p className="hint-text">No negotiation letters generated yet.</p>
        ) : (
          <ul style={{ paddingLeft: 18 }}>
            {recent_negotiations.map((n) => (
              <li key={n.id} style={{ marginBottom: 8, fontSize: 14 }}>
                <strong>{n.negotiation_type.replace("_", " ")}</strong> ({n.tone}) —{" "}
                {new Date(n.created_at).toLocaleDateString()}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
