export const LoadingState = ({ retryCount = 0 }) => (
  <div className="state-screen" role="status" aria-live="polite">
    <section className="dots-container">
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
      <div className="loading-dot"></div>
    </section>
    <p className="state-message">
      {retryCount > 0 ? `Retrying... (${retryCount}/10)` : "Waking up server..."}
    </p>
    <p className="state-hint">
      First load may take 30–50 seconds on Render's free tier.
    </p>
  </div>
);

export const ErrorState = ({ onRetry, error }) => (
  <div className="state-screen" role="alert">
    <div className="state-icon" aria-hidden="true">⚠️</div>
    <p className="state-message state-error">Failed to connect to server</p>
    {error && <p className="state-hint">{error}</p>}
    <button className="retry-btn" onClick={onRetry}>
      ↻ Try Again
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
