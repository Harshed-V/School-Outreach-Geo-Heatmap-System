import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "https://school-outreach-backend.onrender.com",
  timeout: 10000
});

export const fetchDistricts = async () => {
  const { data } = await api.get("/api/districts");
  return data;
};

export const fetchSummary = async () => {
  const { data } = await api.get("/api/summary");
  return data;
};

export const refreshPipeline = async () => {
  const { data } = await api.post("/api/refresh");
  return data;
};
