import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ---- Borrowers ----
export const createBorrower = (data) => client.post("/api/borrowers/", data).then((r) => r.data);
export const listBorrowers = () => client.get("/api/borrowers/").then((r) => r.data);
export const getBorrower = (id) => client.get(`/api/borrowers/${id}`).then((r) => r.data);

// ---- Loans ----
export const createLoan = (data) => client.post("/api/loans/", data).then((r) => r.data);
export const listLoans = (borrowerId) =>
  client
    .get("/api/loans/", { params: borrowerId ? { borrower_id: borrowerId } : {} })
    .then((r) => r.data);
export const getLoan = (id) => client.get(`/api/loans/${id}`).then((r) => r.data);
export const updateLoan = (id, data) => client.patch(`/api/loans/${id}`, data).then((r) => r.data);
export const deleteLoan = (id) => client.delete(`/api/loans/${id}`);

// ---- Settlement Recommendations ----
export const generateSettlementRecommendation = (loanId) =>
  client.post(`/api/loans/${loanId}/settlement-recommendation`).then((r) => r.data);
export const getSettlementRecommendations = (loanId) =>
  client.get(`/api/loans/${loanId}/settlement-recommendation`).then((r) => r.data);

// ---- Negotiation ----
export const generateNegotiation = (data) =>
  client.post("/api/negotiation/generate", data).then((r) => r.data);
export const getNegotiationHistory = (loanId) =>
  client.get(`/api/negotiation/history/${loanId}`).then((r) => r.data);

// ---- Dashboard ----
export const getDashboard = (borrowerId) =>
  client.get(`/api/dashboard/${borrowerId}`).then((r) => r.data);

export default client;
