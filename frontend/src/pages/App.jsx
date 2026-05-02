import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import { DistrictMap } from "../components/DistrictMap";
import { MapLegend } from "../components/MapLegend";
import { LoadingState, EmptyState, ErrorState } from "../components/MapStates";
import { useOutreachData } from "../hooks/useOutreachData";

const App = () => {
  const { status, districts, summary, lastUpdated, refresh, retry } = useOutreachData();

  // ── Filters ────────────────────────────────────────────────────────────────
  const [search, setSearch]                   = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("all");
  const [scoreRange, setScoreRange]           = useState([0, 100]);
  const [focused, setFocused]                 = useState(null);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  // Sync data→state once loaded
  const [data, setData] = useState([]);
  useEffect(() => {
    setData(districts);
  }, [districts]);

  // ── Filtered list (memoised) ───────────────────────────────────────────────
  const filteredData = useMemo(() => {
    const q = search.toLowerCase();
    return data.filter((d) => {
      if (q && !d.district?.toLowerCase().includes(q)) return false;
      if (selectedDistrict !== "all" && d.district !== selectedDistrict) return false;
      if (d.score < scoreRange[0] || d.score > scoreRange[1]) return false;
      return true;
    });
  }, [data, search, selectedDistrict, scoreRange]);

  const topDistricts = useMemo(
    () => [...filteredData].sort((a, b) => b.score - a.score).slice(0, 5),
    [filteredData]
  );

  // ── Handlers ───────────────────────────────────────────────────────────────
  const handleSelect = useCallback((district) => {
    setFocused(district);
    setSelectedDistrict(district.district);
    setMobileDrawerOpen(false);
  }, []);

  const handleDistrictChange = useCallback((value) => {
    setSelectedDistrict(value);
    const found = data.find((d) => d.district === value);
    if (found) setFocused(found);
  }, [data]);

  // Close drawer on Escape key
  useEffect(() => {
    if (!mobileDrawerOpen) return;
    const handler = (e) => { if (e.key === "Escape") setMobileDrawerOpen(false); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [mobileDrawerOpen]);

  // ── Sidebar props (stable reference) ──────────────────────────────────────
  const sidebarProps = {
    summary,
    districts: data,
    filteredDistricts: filteredData,
    topDistricts,
    search,
    setSearch,
    selectedDistrict,
    setSelectedDistrict: handleDistrictChange,
    scoreRange,
    setScoreRange,
    onSelectDistrict: handleSelect,
  };

  const mapReady = status === "ready" && filteredData.length > 0;

  return (
    <div className="app-layout">
      <Header
        onRefresh={refresh}
        lastUpdated={lastUpdated}
        isRefreshing={status === "loading"}
        onOpenSidebar={() => setMobileDrawerOpen(true)}
      />

      <div className="app-body">
        {/* Desktop sidebar — hidden on small screens */}
        <Sidebar {...sidebarProps} />

        {/* Mobile drawer overlay */}
        {mobileDrawerOpen && (
          <>
            <div
              className="drawer-overlay"
              onClick={() => setMobileDrawerOpen(false)}
              aria-hidden="true"
            />
            <aside
              className="drawer"
              role="dialog"
              aria-label="Filters"
              aria-modal="true"
            >
              <button
                className="drawer-close"
                onClick={() => setMobileDrawerOpen(false)}
                aria-label="Close sidebar"
              >
                <svg className="drawer-close-icon" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
              <Sidebar {...sidebarProps} />
            </aside>
          </>
        )}

        {/* Map area */}
        <main className="map-area" id="map-main">
          {status === "loading" && <LoadingState />}
          {status === "error"   && <ErrorState onRetry={retry} />}
          {status === "ready" && filteredData.length === 0 && <EmptyState />}
          {mapReady && (
            <>
              <DistrictMap
                districts={filteredData}
                focused={focused}
                onSelectDistrict={handleSelect}
              />
              <MapLegend />
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
