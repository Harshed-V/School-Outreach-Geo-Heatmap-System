export const LoadingState = () => (
  <div className="state-screen" role="status" aria-live="polite">
    <div className="skeleton-map" aria-hidden="true">
      <div className="skeleton-pulse skeleton-block" style={{ width: "60%", height: "40%" }} />
      <div className="skeleton-pulse skeleton-block" style={{ width: "45%", height: "30%", marginTop: "1rem" }} />
      <div className="skeleton-pulse skeleton-block" style={{ width: "70%", height: "20%", marginTop: "1rem" }} />
    </div>
    <div className="spinner" aria-hidden="true" />
    <p className="state-message">Loading map data…</p>
  </div>
);

export const ErrorState = ({ onRetry }) => (
  <div className="state-screen" role="alert">
    <div className="state-icon" aria-hidden="true">⚠️</div>
    <p className="state-message state-error">Failed to load district data.</p>
    <p className="state-hint">Check that the backend is running on port 5000.</p>
    <button className="retry-btn" onClick={onRetry}>
      ↻ Retry
    </button>
  </div>
);

export const EmptyState = () => (
  <div className="state-screen" role="status">
    <div className="state-icon" aria-hidden="true">🔍</div>
    <p className="state-message">No districts match your filters.</p>
    <p className="state-hint">Try adjusting the search or score range.</p>
  </div>
);
