/**
 * Insights Section Component
 * Displays key metrics with icons in a responsive grid
 * Production-ready with proper spacing, layout, and accessibility
 */

import { memo } from "react";
import { SchoolIcon, ScoreIcon, PriorityIcon } from "./Icons";

/**
 * Individual Insight Card
 * - Icon on left in rounded container
 * - Metric label and value on right
 * - Responsive layout
 * - Hover effects
 */
const InsightCard = memo(({ icon: Icon, label, value }) => (
  <div
    className="
      flex items-center gap-4 p-4 sm:p-5
      bg-white rounded-xl border border-gray-100
      shadow-sm hover:shadow-md transition-shadow duration-200
      focus-within:ring-2 focus-within:ring-blue-400
    "
  >
    {/* Icon Container */}
    <div className="flex-shrink-0">
      <Icon size="md" />
    </div>

    {/* Content */}
    <div className="flex-1 min-w-0">
      <p className="text-xs sm:text-sm text-gray-600 font-medium uppercase tracking-wide">
        {label}
      </p>
      <p className="text-lg sm:text-2xl font-bold text-gray-900 truncate mt-0.5">
        {typeof value === "number" ? value.toLocaleString() : value}
      </p>
    </div>
  </div>
));

InsightCard.displayName = "InsightCard";

/**
 * Insights Section
 * Container for all metric cards with responsive grid
 */
export const InsightsSection = memo(({
  totalSchools = 0,
  averageScore = 0,
  highPriority = 0,
}) => {
  const metrics = [
    {
      icon: SchoolIcon,
      label: "Total Schools",
      value: totalSchools,
    },
    {
      icon: ScoreIcon,
      label: "Average Score",
      value: typeof averageScore === "number" ? averageScore.toFixed(1) : averageScore,
    },
    {
      icon: PriorityIcon,
      label: "High Priority",
      value: highPriority,
    },
  ];

  return (
    <div className="w-full p-4 sm:p-6">
      {/* Header */}
      <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-5">
        Insights
      </h2>

      {/* Cards Grid - Responsive: 1 col mobile → 2 cols tablet → 3 cols desktop */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        {metrics.map((metric) => (
          <InsightCard
            key={metric.label}
            icon={metric.icon}
            label={metric.label}
            value={metric.value}
          />
        ))}
      </div>
    </div>
  );
});

InsightsSection.displayName = "InsightsSection";

export default InsightsSection;
