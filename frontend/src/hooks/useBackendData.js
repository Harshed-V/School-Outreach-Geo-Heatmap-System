import { useState, useEffect, useRef, useCallback } from "react";
import { fetchDistricts, fetchSummary } from "../services/api";

/**
 * useBackendData Hook
 * Handles auto-retry (5s), success detection, and keep-alive (60s).
 */
export const useBackendData = () => {
  const [data, setData] = useState({ districts: [], summary: {} });
  const [loading, setLoading] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [error, setError] = useState(null);

  const retryRef = useRef(null);
  const keepAliveRef = useRef(null);
  const isInitialMount = useRef(true);

  const clearAllIntervals = useCallback(() => {
    if (retryRef.current) clearInterval(retryRef.current);
    if (keepAliveRef.current) clearInterval(keepAliveRef.current);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      // 1. Fetch data
      const [districts, summary] = await Promise.all([
        fetchDistricts(),
        fetchSummary()
      ]);

      // 2. Success detection
      const isValidArray = Array.isArray(districts);
      const isNotEmpty = isValidArray && districts.length > 0;

      if (isValidArray) {
        setData({ 
          districts: districts, 
          summary: summary || {} 
        });

        // If we have actual data, stop retrying and start keep-alive
        if (isNotEmpty) {
          console.log("[Backend] Success detected. Stopping retries.");
          clearInterval(retryRef.current);
          setLoading(false);
          setRetryCount(0);
          setError(null);

          // Start keep-alive ping every 60 seconds
          if (!keepAliveRef.current) {
            console.log("[Backend] Starting keep-alive ping (60s)");
            keepAliveRef.current = setInterval(() => {
              console.log("[Backend] Keep-alive ping...");
              fetchDistricts().catch(() => {}); // Silent ping
            }, 60000);
          }
        }
      }
    } catch (err) {
      console.warn(`[Backend] Fetch failed (Attempt ${retryCount + 1}):`, err.message);
      // We don't set loading=false here, we let the retry interval handle it
    }
  }, [retryCount]);

  const startRetryProcess = useCallback(() => {
    clearAllIntervals();
    setLoading(true);
    setRetryCount(0);
    setError(null);

    // Initial call
    fetchData();

    // Set interval for 5 seconds
    retryRef.current = setInterval(() => {
      setRetryCount(prev => {
        if (prev >= 9) { // 10th attempt (0-indexed)
          console.error("[Backend] Max retries reached.");
          clearInterval(retryRef.current);
          setLoading(false);
          setError("Failed to connect to server after 10 attempts.");
          return prev;
        }
        return prev + 1;
      });
    }, 5000);
  }, [fetchData, clearAllIntervals]);

  // Handle retry logic when retryCount increments
  useEffect(() => {
    if (retryCount > 0 && loading) {
      fetchData();
    }
  }, [retryCount, loading, fetchData]);

  // Setup on mount, cleanup on unmount
  useEffect(() => {
    if (isInitialMount.current) {
      startRetryProcess();
      isInitialMount.current = false;
    }

    return () => clearAllIntervals();
  }, [startRetryProcess, clearAllIntervals]);

  return {
    data,
    loading,
    retryCount: retryCount + 1, // 1-indexed for UI
    error,
    refetch: startRetryProcess
  };
};
