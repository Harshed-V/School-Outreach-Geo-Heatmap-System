import { Menu, RefreshCw } from "lucide-react";
import { memo, useCallback } from "react";

/**
 * Header Component - Responsive Production-Ready
 * 
 * Features:
 * - Responsive title and layout
 * - Touch-friendly buttons
 * - Mobile hamburger menu
 * - Loading state management
 * - Accessibility improvements
 */
export const Header = memo(({ lastUpdated, onRefresh, isRefreshing, onOpenSidebar }) => {
  const handleRefresh = useCallback(() => {
    if (!isRefreshing) {
      onRefresh();
    }
  }, [isRefreshing, onRefresh]);

  return (
    <header className="flex-shrink-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
      <div className="px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between gap-4">
        {/* Left Section - Title */}
        <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
          {/* Mobile Menu Button */}
          <button
            onClick={onOpenSidebar}
            className="md:hidden p-2 -ml-2 hover:bg-blue-500 rounded-lg transition-colors duration-200 flex-shrink-0"
            aria-label="Open sidebar menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Title Section */}
          <div className="min-w-0 flex-1">
            <h1 className="text-xl sm:text-2xl font-bold leading-tight">
              School Outreach Intelligence
            </h1>
            <p className="text-blue-100 text-xs sm:text-sm mt-0.5">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
        </div>

        {/* Right Section - Refresh Button */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className={`
            px-3 sm:px-4 py-2 sm:py-2.5 rounded-lg font-medium transition-all duration-200
            flex items-center gap-2 whitespace-nowrap flex-shrink-0
            ${
              isRefreshing
                ? "bg-blue-500 text-white opacity-75 cursor-not-allowed"
                : "bg-white text-blue-600 hover:bg-blue-50 active:scale-95"
            }
            focus:outline-none focus:ring-2 focus:ring-blue-300
          `}
          aria-busy={isRefreshing}
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
          <span className="hidden sm:inline text-sm">
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </span>
        </button>
      </div>
    </header>
  );
});

Header.displayName = "Header";
