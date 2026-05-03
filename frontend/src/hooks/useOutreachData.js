import { useCallback, useState } from "react";
import { refreshPipeline } from "../services/api";
import { useBackendData } from "./useBackendData";

export const useOutreachData = () => {
  const [lastUpdated, setLastUpdated] = useState(new Date());
  
  const { 
    data, 
    loading, 
    retryCount, 
    error, 
    refetch 
  } = useBackendData();

  const runRefresh = useCallback(async () => {
    try {
      await refreshPipeline();
      await refetch();
      setLastUpdated(new Date());
    } catch (error) {
      console.warn("[Refresh] /api/refresh failed:", error.message);
      // Fallback to just refetching the data
      await refetch();
    }
  }, [refetch]);

  return {
    status: loading ? "loading" : (error ? "error" : "ready"),
    districts: data.districts,
    summary: data.summary,
    lastUpdated,
    retryCount,
    error,
    refresh: runRefresh,
    retry: refetch
  };
};
