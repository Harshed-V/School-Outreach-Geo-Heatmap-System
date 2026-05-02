import { useEffect, useMemo, useCallback, useState } from "react";
import { Header } from "@/components/outreach/Header";
import { Sidebar } from "@/components/outreach/Sidebar";
import { HeatmapMap } from "@/components/outreach/HeatmapMap";
import { MapLegend } from "@/components/outreach/MapLegend";
import { InsightsSection } from "@/components/outreach/InsightsSection";
import { LoadingState, EmptyState, ErrorState } from "@/components/outreach/MapStates";
import { DISTRICTS } from "@/data/districts";
import { Sheet, SheetContent } from "@/components/ui/sheet";

/**
 * Main Index Component - Production Ready
 * 
 * Features:
 * - Fully responsive layout (mobile/tablet/desktop)
 * - Mobile drawer sidebar with smooth transitions
 * - Optimized performance with useCallback and useMemo
 * - No layout shifts or overflow issues
 * - Touch-friendly interactions
 * - Improved accessibility
 */
const Index = () => {
  const [status, setStatus] = useState("loading");
  const [data, setData] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [mobileOpen, setMobileOpen] = useState(false);

  // Filter state
  const [search, setSearch] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("all");
  const [scoreRange, setScoreRange] = useState([0, 100]);
  const [schoolType, setSchoolType] = useState("all");
  const [focused, setFocused] = useState(null);

  /**
   * Fetch data with cleanup
   * Memoized to prevent unnecessary re-renders
   */
  const fetchData = useCallback(() => {
    setStatus("loading");
    // TODO: Replace with real API call to backend
    // const response = await fetch("http://localhost:5000/api/districts");
    // const districts = await response.json();
    
    const t = setTimeout(() => {
      setData(DISTRICTS);
      setStatus("ready");
      setLastUpdated(new Date());
    }, 700);
    return () => clearTimeout(t);
  }, []);

  // Initial data load
  useEffect(() => {
    const cleanup = fetchData();
    return cleanup;
  }, [fetchData]);

  /**
   * Memoized filtered data
   * Only recalculates when dependencies change
   */
  const filtered = useMemo(() => {
    return data.filter((d) => {
      if (search && !d.name.toLowerCase().includes(search.toLowerCase())) {
        return false;
      }
      if (selectedDistrict !== "all" && d.id !== selectedDistrict) {
        return false;
      }
      if (d.score < scoreRange[0] || d.score > scoreRange[1]) {
        return false;
      }
      return true;
    });
  }, [data, search, selectedDistrict, scoreRange]);

  /**
   * Calculate insights metrics
   * Memoized to prevent re-calculation on every render
   */
  const insights = useMemo(() => {
    if (filtered.length === 0) {
      return { totalSchools: 0, averageScore: 0, highPriority: 0 };
    }

    const totalSchools = filtered.reduce((sum, d) => sum + (d.schools || 0), 0);
    const averageScore = filtered.reduce((sum, d) => sum + d.score, 0) / filtered.length;
    const highPriority = filtered.filter((d) => d.score < 40).length;

    return { totalSchools, averageScore, highPriority };
  }, [filtered]);

  /**
   * Handle district selection
   * Memoized callback to prevent unnecessary re-renders
   */
  const handleSelectDistrict = useCallback((d) => {
    setFocused(d);
    setSelectedDistrict(d.id);
    setMobileOpen(false); // Close mobile drawer on selection
  }, []);

  /**
   * Handle score range change
   * Memoized callback
   */
  const handleScoreRangeChange = useCallback((range) => {
    setScoreRange(range);
  }, []);

  /**
   * Handle search change
   * Memoized callback
   */
  const handleSearchChange = useCallback((value) => {
    setSearch(value);
  }, []);

  /**
   * Handle district change from dropdown
   * Memoized callback
   */
  const handleDistrictChange = useCallback((districtId) => {
    setSelectedDistrict(districtId);
    const d = data.find((x) => x.id === districtId);
    if (d) {
      setFocused(d);
    }
  }, [data]);

  /**
   * Handle school type change
   * Memoized callback
   */
  const handleSchoolTypeChange = useCallback((type) => {
    setSchoolType(type);
  }, []);

  /**
   * Sidebar props
   * Memoized to prevent unnecessary re-renders of child components
   */
  const sidebarProps = useMemo(() => ({
    allDistricts: data,
    filteredDistricts: filtered,
    search,
    onSearchChange: handleSearchChange,
    selectedDistrict,
    onDistrictChange: handleDistrictChange,
    scoreRange,
    onScoreRangeChange: handleScoreRangeChange,
    schoolType,
    onSchoolTypeChange: handleSchoolTypeChange,
    onSelectDistrict: handleSelectDistrict,
    activeId: focused?.id ?? null,
  }), [
    data,
    filtered,
    search,
    handleSearchChange,
    selectedDistrict,
    handleDistrictChange,
    scoreRange,
    handleScoreRangeChange,
    schoolType,
    handleSchoolTypeChange,
    handleSelectDistrict,
    focused?.id,
  ]);

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Header - Fixed height, no overflow */}
      <Header
        lastUpdated={lastUpdated}
        onRefresh={fetchData}
        isRefreshing={status === "loading"}
        onOpenSidebar={() => setMobileOpen(true)}
      />

      {/* Main Layout Container - Flexible, fills remaining space */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Desktop Sidebar - Hidden on mobile */}
        <aside className="hidden md:flex md:w-80 lg:w-96 flex-shrink-0 bg-white border-r border-gray-200 overflow-y-auto">
          <Sidebar {...sidebarProps} />
        </aside>

        {/* Mobile Drawer - Sheet component for smooth drawer experience */}
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetContent
            side="left"
            className="p-0 w-[calc(100vw-3rem)] max-w-sm md:hidden overflow-y-auto"
          >
            <Sidebar {...sidebarProps} variant="embedded" />
          </SheetContent>
        </Sheet>

        {/* Main Content Area - Flexible, scrollable */}
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {/* Insights Section - Sticky header for quick metrics */}
          {status === "ready" && (
            <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
              <InsightsSection
                totalSchools={insights.totalSchools}
                averageScore={insights.averageScore}
                highPriority={insights.highPriority}
              />
            </div>
          )}

          {/* Map Container - Flexible, takes remaining space */}
          <div className="flex-1 relative min-w-0 overflow-hidden">
            {/* Map Component */}
            {status === "ready" && (
              <HeatmapMap
                districts={filtered}
                focused={focused}
                onSelect={handleSelectDistrict}
              />
            )}

            {/* Legend - Positioned absolutely, responsive positioning */}
            {status === "ready" && filtered.length > 0 && <MapLegend />}

            {/* Loading State */}
            {status === "loading" && <LoadingState />}

            {/* Empty State */}
            {status === "ready" && filtered.length === 0 && <EmptyState />}

            {/* Error State */}
            {status === "error" && <ErrorState onRetry={fetchData} />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Index;
