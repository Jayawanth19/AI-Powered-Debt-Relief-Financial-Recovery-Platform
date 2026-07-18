import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listLoans } from "../api/client.js";

export default function Loans({ borrowerId }) {
  const [loans, setLoans] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listLoans(borrowerId)
      .then(setLoans)
      .catch((err) => setError(err?.response?.data?.detail || "Failed to load loans"));
  }, [borrowerId]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>My Loans</h2>
        <Link to="/add-loan"><button className="primary" style={{ marginTop: 0 }}>+ Add Loan</button></Link>
      </div>

      {error && <p className="error-text">{error}</p>}

      <div className="card">
        {loans.length === 0 ? (
          <p className="hint-text">No loans yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Lender</th>
                <th>Type</th>
                <th>Outstanding</th>
                <th>EMI</th>
                <th>Overdue (mo)</th>
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
                  <td>{loan.overdue_months}</td>
                  <td>{loan.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
