import { useState, useCallback, useEffect, useRef } from "react";

/**
 * Custom hook for fetching data with automatic retries.
 * Handles Render's cold start by retrying every 5s (max 10 attempts).
 */
export const useFetchWithRetry = (fetchFn, maxRetries = 10, interval = 5000) => {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading"); // loading, ready, error
  const [retryCount, setRetryCount] = useState(0);
  const [error, setError] = useState(null);
  
  const timerRef = useRef(null);
  const isMounted = useRef(true);

  const executeFetch = useCallback(async (isManual = false) => {
    if (isManual) {
      setRetryCount(0);
      setError(null);
    }
    
    setStatus("loading");

    try {
      const result = await fetchFn();
      
      if (isMounted.current) {
        setData(result);
        setStatus("ready");
        setRetryCount(0);
      }
    } catch (err) {
      console.warn(`[useFetchWithRetry] Attempt ${retryCount + 1}/${maxRetries} failed:`, err.message);
      
      if (isMounted.current) {
        if (retryCount < maxRetries - 1) {
          // Schedule retry
          timerRef.current = setTimeout(() => {
            setRetryCount(prev => prev + 1);
          }, interval);
        } else {
          setError(err.message);
          setStatus("error");
        }
      }
    }
  }, [fetchFn, maxRetries, interval, retryCount]);

  // Handle auto-retry when retryCount changes
  useEffect(() => {
    if (retryCount > 0 && status === "loading") {
      executeFetch();
    }
  }, [retryCount, status, executeFetch]);

  // Initial fetch
  useEffect(() => {
    isMounted.current = true;
    executeFetch();
    return () => {
      isMounted.current = false;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [executeFetch]);

  return {
    data,
    status,
    retryCount,
    error,
    refresh: () => executeFetch(true)
  };
};
