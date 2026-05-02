import { PriorityIcon, SchoolIcon, ScoreIcon } from "./icons";

export const Sidebar = ({
  summary,
  districts,
  filteredDistricts,
  topDistricts,
  search,
  setSearch,
  selectedDistrict,
  setSelectedDistrict,
  scoreRange,
  setScoreRange,
  onSelectDistrict,
}) => {
  const getPriorityClass = (score) => {
    if (score > 80) return "badge-red";
    if (score > 60) return "badge-orange";
    if (score > 40) return "badge-yellow";
    return "badge-green";
  };

  return (
    <aside className="sidebar" role="complementary" aria-label="District filters and stats">
      {/* ── Stats ───────────────────────────────────────────────────── */}
      <section className="cards" aria-label="Summary statistics">
        <article className="card stat-card">
          <SchoolIcon />
          <div className="stat-copy">
            <p className="stat-label">Total Schools</p>
            <p className="stat-value">{summary.total_schools?.toLocaleString() ?? "-"}</p>
          </div>
        </article>
        <article className="card stat-card">
          <ScoreIcon />
          <div className="stat-copy">
            <p className="stat-label">Avg Score</p>
            <p className="stat-value">{summary.avg_score != null ? summary.avg_score.toFixed(1) : "-"}</p>
          </div>
        </article>
        <article className="card stat-card">
          <PriorityIcon />
          <div className="stat-copy">
            <p className="stat-label">High Priority</p>
            <p className="stat-value">{summary.high_priority ?? "-"}</p>
          </div>
        </article>
      </section>

      {/* ── Filters ─────────────────────────────────────────────────── */}
      <section className="filters card" aria-label="Filter controls">
        <h3 className="section-heading">Filters</h3>

        <label className="filter-label" htmlFor="district-search">Search</label>
        <input
          id="district-search"
          className="filter-input"
          placeholder="Search district..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          autoComplete="off"
          spellCheck={false}
        />

        <label className="filter-label" htmlFor="district-select">District</label>
        <select
          id="district-select"
          className="filter-input"
          value={selectedDistrict}
          onChange={(e) => setSelectedDistrict(e.target.value)}
        >
          <option value="all">All districts</option>
          {districts.map((d) => (
            <option key={d.district} value={d.district}>
              {d.district.charAt(0).toUpperCase() + d.district.slice(1)}
            </option>
          ))}
        </select>

        <label className="filter-label" htmlFor="score-range">
          Score: <strong>{scoreRange[0]}</strong> to <strong>100</strong>
        </label>
        <input
          id="score-range"
          className="filter-range"
          type="range"
          min="0"
          max="100"
          value={scoreRange[0]}
          onChange={(e) => setScoreRange([Number(e.target.value), 100])}
          aria-label={`Minimum score: ${scoreRange[0]}`}
        />

        <p className="filter-count">{filteredDistricts.length} district(s) shown</p>
      </section>

      {/* ── Top Districts ────────────────────────────────────────────── */}
      {topDistricts.length > 0 && (
        <section className="card" aria-label="Top performing districts">
          <h3 className="section-heading">Top Districts</h3>
          <ul className="top-list" role="list">
            {topDistricts.map((d) => (
              <li key={d.district} role="listitem">
                <button
                  className="top-list-btn"
                  onClick={() => onSelectDistrict(d)}
                  aria-label={`Select ${d.district}, score ${d.score.toFixed(1)}`}
                >
                  <span className="top-list-name">
                    {d.district.charAt(0).toUpperCase() + d.district.slice(1)}
                  </span>
                  <span className={`badge ${getPriorityClass(d.score)}`}>
                    {d.score.toFixed(1)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </aside>
  );
};
