import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  getLoan,
  generateSettlementRecommendation,
  getSettlementRecommendations,
  generateNegotiation,
  getNegotiationHistory,
} from "../api/client.js";

const stressBadgeClass = (level) => {
  switch (level) {
    case "Low": return "badge badge-low";
    case "Moderate": return "badge badge-moderate";
    case "High": return "badge badge-high";
    default: return "badge badge-critical";
  }
};

export default function LoanDetail() {
  const { loanId } = useParams();
  const [loan, setLoan] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [negotiations, setNegotiations] = useState([]);
  const [genLoading, setGenLoading] = useState(false);
  const [negLoading, setNegLoading] = useState(false);
  const [error, setError] = useState("");

  const [negForm, setNegForm] = useState({
    negotiation_type: "settlement_letter",
    tone: "professional",
    additional_context: "",
  });

  const refresh = () => {
    getLoan(loanId).then(setLoan);
    getSettlementRecommendations(loanId).then(setRecommendations);
    getNegotiationHistory(loanId).then(setNegotiations);
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loanId]);

  const handleGenerateRecommendation = async () => {
    setGenLoading(true);
    setError("");
    try {
      await generateSettlementRecommendation(loanId);
      refresh();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to generate recommendation.");
    } finally {
      setGenLoading(false);
    }
  };

  const handleGenerateNegotiation = async (e) => {
    e.preventDefault();
    setNegLoading(true);
    setError("");
    try {
      await generateNegotiation({ loan_id: parseInt(loanId, 10), ...negForm });
      refresh();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to generate negotiation content.");
    } finally {
      setNegLoading(false);
    }
  };

  if (!loan) return <p>Loading loan...</p>;

  const latestRec = recommendations[0];

  return (
    <div>
      <Link to="/loans" style={{ color: "var(--text-dim)", fontSize: 13 }}>&larr; Back to loans</Link>
      <h2>{loan.lender_name} — {loan.loan_type}</h2>

      <div className="grid grid-3">
        <div className="stat-card">
          <div className="stat-label">Outstanding</div>
          <div className="stat-value">₹{loan.outstanding_amount.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Monthly EMI</div>
          <div className="stat-value">₹{loan.emi_amount.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Overdue</div>
          <div className="stat-value">{loan.overdue_months} mo</div>
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ margin: 0 }}>AI Settlement Recommendation</h3>
          <button className="primary" style={{ marginTop: 0 }} onClick={handleGenerateRecommendation} disabled={genLoading}>
            {genLoading ? "Analyzing..." : "Generate New Analysis"}
          </button>
        </div>

        {!latestRec ? (
          <p className="hint-text">No analysis yet. Click "Generate New Analysis" to get an AI-powered settlement recommendation.</p>
        ) : (
          <div style={{ marginTop: 16 }}>
            <div className="grid grid-4">
              <div className="stat-card">
                <div className="stat-label">Debt Stress</div>
                <span className={stressBadgeClass(latestRec.debt_stress_level)}>{latestRec.debt_stress_level}</span>
              </div>
              <div className="stat-card">
                <div className="stat-label">EMI/Income Ratio</div>
                <div className="stat-value">{latestRec.emi_to_income_ratio}%</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Suggested Settlement</div>
                <div className="stat-value">{latestRec.recommended_settlement_pct}%</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Suggested Amount</div>
                <div className="stat-value">₹{latestRec.recommended_settlement_amount.toLocaleString()}</div>
              </div>
            </div>
            <div className="ai-summary" style={{ marginTop: 16 }}>{latestRec.ai_summary}</div>
          </div>
        )}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Generate Negotiation Letter</h3>
        <form onSubmit={handleGenerateNegotiation}>
          <label>Type</label>
          <select
            value={negForm.negotiation_type}
            onChange={(e) => setNegForm({ ...negForm, negotiation_type: e.target.value })}
          >
            <option value="settlement_letter">Settlement Letter</option>
            <option value="email">Negotiation Email</option>
            <option value="hardship_letter">Financial Hardship Letter</option>
          </select>

          <label>Tone</label>
          <select value={negForm.tone} onChange={(e) => setNegForm({ ...negForm, tone: e.target.value })}>
            <option value="professional">Professional</option>
            <option value="empathetic">Empathetic</option>
            <option value="firm">Firm</option>
          </select>

          <label>Additional context (optional)</label>
          <textarea
            rows={3}
            value={negForm.additional_context}
            onChange={(e) => setNegForm({ ...negForm, additional_context: e.target.value })}
            placeholder="e.g. Recently lost job, medical emergency in family..."
          />

          <button className="primary" type="submit" disabled={negLoading}>
            {negLoading ? "Generating..." : "Generate Letter"}
          </button>
        </form>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Negotiation History</h3>
        {negotiations.length === 0 ? (
          <p className="hint-text">No negotiation letters generated yet.</p>
        ) : (
          negotiations.map((n) => (
            <div key={n.id} style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 13, color: "var(--text-dim)", marginBottom: 6 }}>
                {n.negotiation_type.replace("_", " ")} · {n.tone} · {new Date(n.created_at).toLocaleString()}
              </div>
              <div className="ai-summary">{n.generated_content}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
