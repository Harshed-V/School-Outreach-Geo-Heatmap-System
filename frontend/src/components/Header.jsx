import logo from "../assets/logo.svg";

export const Header = ({ onRefresh, lastUpdated, isRefreshing, onOpenSidebar }) => {
  return (
    <header className="header" role="banner">
      <label className="burger" onClick={onOpenSidebar} aria-label="Open filters sidebar">
        <input type="checkbox" readOnly checked={false} />
        <span></span>
        <span></span>
        <span></span>
      </label>

      <div className="header-brand">
        <img
          src={logo}
          alt=""
          className="header-logo"
          aria-hidden="true"
          draggable="false"
        />
        <div className="header-title">
          <h1>School Outreach Intelligence</h1>
          <p className="header-subtitle">District-level outreach potential</p>
        </div>
      </div>

      <div className="header-actions">
        <button
          className={`refresh-btn${isRefreshing ? " refreshing" : ""}`}
          onClick={onRefresh}
          disabled={isRefreshing}
          aria-label={isRefreshing ? "Refreshing data" : "Refresh data"}
        >
          <svg className="refresh-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M20 12a8 8 0 1 1-2.34-5.66" />
            <path d="M20 4v6h-6" />
          </svg>
          <span className="refresh-label">
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </span>
        </button>
        <small className="header-timestamp">
          Updated: {lastUpdated.toLocaleTimeString()}
        </small>
      </div>
    </header>
  );
};
