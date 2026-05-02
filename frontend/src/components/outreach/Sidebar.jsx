import { Search, Sliders, ChevronDown } from "lucide-react";
import { memo, useCallback } from "react";
import InsightCard from "./InsightCard";
import { SchoolIcon, ScoreIcon, PriorityIcon } from "@/components/icons";

/**
 * District Item Component
 * Memoized to prevent unnecessary re-renders
 */
const DistrictItem = memo(({ district, isActive, onSelect }) => {
  return (
    <button
      onClick={() => onSelect(district)}
      className={`
        w-full text-left px-3 py-2.5 rounded-lg transition-all duration-200
        ${
          isActive
            ? "bg-blue-500 text-white shadow-md"
            : "bg-white hover:bg-gray-50 border border-gray-100"
        }
        active:scale-98 focus:outline-none focus:ring-2 focus:ring-blue-400
      `}
      aria-current={isActive ? "true" : "false"}
    >
      <div className="font-medium truncate">{district.name}</div>
      <div className="text-xs opacity-75 mt-0.5">
        {district.schools} schools • Score: {district.score}
      </div>
    </button>
  );
});

DistrictItem.displayName = "DistrictItem";

/**
 * Sidebar Component - Responsive and Optimized
 * 
 * Features:
 * - Responsive layout (embedded on mobile, sidebar on desktop)
 * - Memoized district items to prevent re-renders
 * - Smooth interactions and transitions
 * - Better touch-friendly spacing
 * - Accessible form controls
 */
export const Sidebar = memo(({
  allDistricts,
  filteredDistricts,
  search,
  onSearchChange,
  selectedDistrict,
  onDistrictChange,
  scoreRange,
  onScoreRangeChange,
  schoolType,
  onSchoolTypeChange,
  onSelectDistrict,
  activeId,
  variant = "desktop",
}) => {
  const handleDistrictSelect = useCallback((district) => {
    onDistrictChange(district.id);
    onSelectDistrict(district);
  }, [onDistrictChange, onSelectDistrict]);

  const handleMinScore = useCallback((e) => {
    const newMin = parseInt(e.target.value);
    if (newMin <= scoreRange[1]) {
      onScoreRangeChange([newMin, scoreRange[1]]);
    }
  }, [scoreRange, onScoreRangeChange]);

  const handleMaxScore = useCallback((e) => {
    const newMax = parseInt(e.target.value);
    if (newMax >= scoreRange[0]) {
      onScoreRangeChange([scoreRange[0], newMax]);
    }
  }, [scoreRange, onScoreRangeChange]);

  return (
    <div className={variant === "embedded" ? "w-full" : "w-full"}>
      <div className="p-4 sm:p-6 space-y-5 sm:space-y-6">
        {/* Insights Section */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold text-gray-600 uppercase tracking-wide px-1">
            Insights
          </h3>
          <InsightCard title="Total Schools" value="28,820" icon={SchoolIcon} />
          <InsightCard title="Avg Score" value="46.0" icon={ScoreIcon} />
          <InsightCard title="High Priority" value="2" icon={PriorityIcon} />
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200"></div>

        {/* Search Input */}
        <div>
          <label htmlFor="search-districts" className="block text-xs sm:text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <Search className="h-4 w-4 flex-shrink-0" />
            Search Districts
          </label>
          <input
            id="search-districts"
            type="text"
            placeholder="Find a district..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          />
        </div>

        {/* Score Range Slider */}
        <div>
          <label htmlFor="score-min" className="block text-xs sm:text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Sliders className="h-4 w-4 flex-shrink-0" />
            Score Range: {scoreRange[0]} - {scoreRange[1]}
          </label>
          <div className="space-y-3">
            <div>
              <label htmlFor="score-min" className="text-xs text-gray-600 mb-1 block">
                Minimum Score
              </label>
              <input
                id="score-min"
                type="range"
                min="0"
                max="100"
                value={scoreRange[0]}
                onChange={handleMinScore}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                aria-label="Minimum score filter"
              />
            </div>
            <div>
              <label htmlFor="score-max" className="text-xs text-gray-600 mb-1 block">
                Maximum Score
              </label>
              <input
                id="score-max"
                type="range"
                min="0"
                max="100"
                value={scoreRange[1]}
                onChange={handleMaxScore}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                aria-label="Maximum score filter"
              />
            </div>
          </div>
        </div>

        {/* School Type Selector */}
        <div>
          <label htmlFor="school-type" className="block text-xs sm:text-sm font-semibold text-gray-700 mb-2">
            School Type
          </label>
          <div className="relative">
            <select
              id="school-type"
              value={schoolType}
              onChange={(e) => onSchoolTypeChange(e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white cursor-pointer transition-colors"
            >
              <option value="all">All Types</option>
              <option value="government">Government</option>
              <option value="private">Private</option>
              <option value="secondary">Secondary</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        {/* Districts List */}
        <div className="flex flex-col min-h-0">
          <h3 className="text-xs sm:text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            Districts
            <span className="inline-flex items-center justify-center min-w-6 h-6 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              {filteredDistricts.length}
            </span>
          </h3>
          <div className="space-y-2 overflow-y-auto flex-1">
            {filteredDistricts.length > 0 ? (
              filteredDistricts.map((district) => (
                <DistrictItem
                  key={district.id}
                  district={district}
                  isActive={activeId === district.id}
                  onSelect={handleDistrictSelect}
                />
              ))
            ) : (
              <div className="flex items-center justify-center py-8 px-4 text-center">
                <div>
                  <p className="text-sm text-gray-500">No districts match your filters</p>
                  <p className="text-xs text-gray-400 mt-1">Try adjusting your search criteria</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

Sidebar.displayName = "Sidebar";
