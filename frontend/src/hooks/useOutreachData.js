import { useCallback, useEffect, useState } from "react";
import { fetchDistricts, fetchSummary, refreshPipeline } from "../services/api";

export const useOutreachData = () => {
  const [status, setStatus] = useState("loading");
  const [districts, setDistricts] = useState([]);
  const [summary, setSummary] = useState({
    total_schools: 0,
    avg_score: 0,
    high_priority: 0,
    high_priority_districts: 0
  });
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const loadData = useCallback(async () => {
    try {
      setStatus("loading");
      const [districtData, summaryData] = await Promise.all([
        fetchDistricts(),
        fetchSummary()
      ]);

      console.log("[useOutreachData] API Response - Districts:", districtData);
      console.log("[useOutreachData] API Response - Summary:", summaryData);

      // Handle both raw array and { data: [] } wrapper
      const finalDistricts = Array.isArray(districtData) 
        ? districtData 
        : (districtData?.data && Array.isArray(districtData.data) ? districtData.data : []);

      setDistricts(finalDistricts);
      setSummary(summaryData || {
        total_schools: 0,
        avg_score: 0,
        high_priority: 0,
        high_priority_districts: 0
      });
      setLastUpdated(new Date());
      setStatus("ready");
    } catch (error) {
      console.error("[useOutreachData] Load error:", error);
      setStatus("error");
    }
  }, []);

  const runRefresh = useCallback(async () => {
    try {
      setStatus("loading");
      await refreshPipeline();
    } catch (error) {
      // /api/refresh failed — not fatal, still reload the current data
      console.warn("[Refresh] /api/refresh failed:", error.message);
    }
    // Always reload data after refresh attempt (success or failure)
    await loadData();
  }, [loadData]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    status,
    districts,
    summary,
    lastUpdated,
    refresh: runRefresh,
    retry: loadData
  };
};
