import React, { useState } from "react";
import { createBorrower } from "../api/client.js";

export default function Onboarding({ onCreated }) {
  const [form, setForm] = useState({ name: "", email: "", monthly_income: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const borrower = await createBorrower({
        ...form,
        monthly_income: parseFloat(form.monthly_income),
      });
      onCreated(borrower.id);
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <form onSubmit={handleSubmit} className="card" style={{ width: 400 }}>
        <h2>Welcome 👋</h2>
        <p style={{ color: "var(--text-dim)", fontSize: 14 }}>
          Let's set up your borrower profile to get personalized AI debt insights.
        </p>

        <label>Full name</label>
        <input
          required
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          placeholder="e.g. Talada Jayawanth"
        />

        <label>Email</label>
        <input
          required
          type="email"
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
          placeholder="you@example.com"
        />

        <label>Monthly income (₹)</label>
        <input
          required
          type="number"
          min="1"
          step="0.01"
          value={form.monthly_income}
          onChange={(e) => setForm({ ...form, monthly_income: e.target.value })}
          placeholder="e.g. 45000"
        />

        {error && <p className="error-text">{error}</p>}

        <button className="primary" type="submit" disabled={loading} style={{ width: "100%" }}>
          {loading ? "Creating profile..." : "Get Started"}
        </button>
      </form>
    </div>
  );
}
