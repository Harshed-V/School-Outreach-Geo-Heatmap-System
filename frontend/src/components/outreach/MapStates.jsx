import { AlertCircle, Loader } from "lucide-react";

export const LoadingState = () => (
  <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-40">
    <div className="text-center">
      <Loader className="h-8 w-8 text-blue-600 animate-spin mx-auto mb-4" />
      <p className="text-gray-600">Loading districts...</p>
    </div>
  </div>
);

export const EmptyState = () => (
  <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-40">
    <div className="text-center">
      <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-gray-900">No districts found</h3>
      <p className="text-gray-600">Try adjusting your filters</p>
    </div>
  </div>
);

export const ErrorState = ({ onRetry }) => (
  <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-40">
    <div className="text-center">
      <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-gray-900">Something went wrong</h3>
      <p className="text-gray-600 mb-4">Failed to load data</p>
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Try Again
      </button>
    </div>
  </div>
);
