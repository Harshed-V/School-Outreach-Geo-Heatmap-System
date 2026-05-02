/**
 * SVG Icon Components with Tailwind Containers
 * Production-ready, reusable, responsive icons with built-in styling
 */

/**
 * School Icon - Blue
 * Building icon representing total schools
 */
export const SchoolIcon = ({ size = "md", className = "" }) => {
  const sizeMap = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };

  const SVG = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 80 80"
      className={`${sizeMap[size]} ${className}`}
      aria-hidden="true"
    >
      <rect x="22" y="42" width="36" height="22" rx="2" fill="none" stroke="#4F6EF7" strokeWidth="2" />
      <path
        d="M20,44 Q40,28 60,44"
        fill="none"
        stroke="#4F6EF7"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M34,64 L34,52 Q40,46 46,52 L46,64"
        fill="none"
        stroke="#4F6EF7"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="24" y="48" width="7" height="7" rx="1.5" fill="none" stroke="#4F6EF7" strokeWidth="1.6" />
      <rect x="49" y="48" width="7" height="7" rx="1.5" fill="none" stroke="#4F6EF7" strokeWidth="1.6" />
      <line
        x1="40"
        y1="28"
        x2="40"
        y2="20"
        stroke="#4F6EF7"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
      <polygon points="40,20 47,23 40,26" fill="#4F6EF7" />
    </svg>
  );

  return (
    <div className="inline-flex items-center justify-center p-2.5 bg-blue-50 rounded-xl">
      {SVG}
    </div>
  );
};

/**
 * Score Icon - Amber/Yellow
 * Speedometer gauge representing average score
 */
export const ScoreIcon = ({ size = "md", className = "" }) => {
  const sizeMap = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };

  const SVG = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 80 80"
      className={`${sizeMap[size]} ${className}`}
      aria-hidden="true"
    >
      <path
        d="M18,52 A22,22 0 1,1 62,52"
        fill="none"
        stroke="#fde68a"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <path
        d="M18,52 A22,22 0 0,1 51,24"
        fill="none"
        stroke="#F59E0B"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <line
        x1="40"
        y1="50"
        x2="50"
        y2="27"
        stroke="#F59E0B"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="40" cy="50" r="3" fill="#F59E0B" />
      <line x1="18" y1="52" x2="21" y2="52" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="62" y1="52" x2="59" y2="52" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="40" y1="30" x2="40" y2="33" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );

  return (
    <div className="inline-flex items-center justify-center p-2.5 bg-amber-50 rounded-xl">
      {SVG}
    </div>
  );
};

/**
 * Priority Icon - Red
 * Flame icon representing high priority schools
 */
export const PriorityIcon = ({ size = "md", className = "" }) => {
  const sizeMap = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };

  const SVG = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 80 80"
      className={`${sizeMap[size]} ${className}`}
      aria-hidden="true"
    >
      <path
        d="M40,62 C28,62 22,54 22,46 C22,38 28,33 32,30 C31,35 34,37 36,35 C37,30 40,24 44,20 C44,27 48,29 50,33 C52,29 51,26 50,23 C55,27 58,34 58,42 C58,52 52,62 40,62 Z"
        fill="none"
        stroke="#F43F5E"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M40,56 C34,56 31,51 31,46 C31,42 34,39 36,37 C36,40 38,41 40,39 C41,37 42,34 43,32 C44,36 46,37 47,40 C48,37 47,35 46,33 C49,36 50,40 50,44 C50,51 46,56 40,56 Z"
        fill="#F43F5E"
        opacity="0.25"
      />
    </svg>
  );

  return (
    <div className="inline-flex items-center justify-center p-2.5 bg-red-50 rounded-xl">
      {SVG}
    </div>
  );
};

export default { SchoolIcon, ScoreIcon, PriorityIcon };
