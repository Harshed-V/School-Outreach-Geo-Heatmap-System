export const ScoreIcon = () => (
  <div className="stat-icon stat-icon-score" aria-hidden="true">
    <svg viewBox="0 0 24 24" fill="none">
      {/* Gauge outer circle */}
      <circle cx="12" cy="13" r="9" fill="none" stroke="#F59E0B" strokeWidth="1.5" />
      {/* Gauge background arc */}
      <path d="M5 13 A7 7 0 0 1 19 13" fill="none" stroke="#FCD34D" strokeWidth="2" />
      {/* Gauge active arc */}
      <path d="M5 13 A7 7 0 0 1 16 7" fill="none" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" />
      {/* Center dot */}
      <circle cx="12" cy="13" r="1.5" fill="#F59E0B" />
      {/* Needle */}
      <line x1="12" y1="13" x2="15" y2="8" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  </div>
);
