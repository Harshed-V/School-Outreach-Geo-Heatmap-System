/**
 * MapLegend Component - Responsive Legend
 * 
 * Features:
 * - Responsive positioning (bottom-right on desktop, adjusts on mobile)
 * - Smooth animations
 * - Better touch interaction
 * - Accessible color labels
 */
export const MapLegend = () => {
  const ranges = [
    { label: "Very high (81-100)", color: "#d73027" },
    { label: "High (61-80)", color: "#fc8d59" },
    { label: "Medium (41-60)", color: "#fee08b" },
    { label: "Low (21-40)", color: "#d9ef8b" },
    { label: "Very low (0-20)", color: "#91cf60" },
  ];

  return (
    <div className="absolute bottom-4 sm:bottom-6 left-4 sm:left-6 right-4 sm:right-auto bg-white rounded-lg shadow-lg p-4 sm:p-5 max-w-xs z-10 transition-all duration-200 hover:shadow-xl">
      <h3 className="font-semibold text-gray-900 mb-3 text-sm sm:text-base">
        Score Legend
      </h3>
      <div className="space-y-2.5">
        {ranges.map((range) => (
          <div key={range.label} className="flex items-center gap-3">
            <div
              className="w-4 h-4 sm:w-5 sm:h-5 rounded-full flex-shrink-0 transition-transform hover:scale-125"
              style={{ backgroundColor: range.color }}
              aria-label={`${range.label} marker color`}
            />
            <span className="text-xs sm:text-sm text-gray-600 leading-tight">
              {range.label}
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-4 leading-relaxed">
        Marker size and color follow the normalized outreach score.
      </p>
    </div>
  );
};
