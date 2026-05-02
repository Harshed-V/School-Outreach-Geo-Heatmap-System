    import { memo } from "react";

    const InsightCard = memo(({ title, value, icon: Icon }) => {
    return (
        <div className="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl shadow-sm hover:shadow-md transition-shadow">
        <Icon />
        <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500 uppercase font-medium tracking-wide">
            {title}
            </p>
            <p className="text-lg font-semibold text-gray-900 mt-0.5 truncate">
            {value}
            </p>
        </div>
        </div>
    );
    });

    InsightCard.displayName = "InsightCard";

    export default InsightCard;
