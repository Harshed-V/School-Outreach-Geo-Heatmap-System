import axios from "axios";

// 1. Sanitize environment variable (handles common Vercel misconfigurations)
const getBaseURL = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (!envUrl) return "https://school-outreach-backend.onrender.com";
  
  // If the user accidentally pasted "VITE_API_BASE_URL = https://..." into Vercel
  const cleanUrl = envUrl.replace(/^VITE_API_BASE_URL\s*=\s*/, "").trim();
  
  // Ensure it starts with http
  return cleanUrl.startsWith("http") ? cleanUrl : `https://${cleanUrl}`;
};

const baseURL = getBaseURL();
console.log("[API] Active Base URL:", baseURL);

const api = axios.create({
  baseURL,
  timeout: 15000, // Increased timeout for Render cold starts
  headers: {
    "Content-Type": "application/json"
  }
});

export const fetchDistricts = async () => {
  const response = await api.get("/api/districts");
  return response.data;
};

export const fetchSummary = async () => {
  const response = await api.get("/api/summary");
  return response.data;
};

export const refreshPipeline = async () => {
  // Backend expects POST based on routes/districts.py
  const response = await api.post("/api/refresh");
  return response.data;
};

