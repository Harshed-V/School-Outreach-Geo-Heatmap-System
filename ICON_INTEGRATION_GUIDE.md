# Icon & Insight Card Integration Guide

## 📦 Component Overview

### Icons (3 Separate Components)

Each icon is a **self-contained, reusable React component** with:
- Built-in Tailwind container with rounded background
- Size prop (sm, md, lg)
- Proper color scheme (blue, amber, red)
- ARIA accessibility
- Production-ready

---

## 🎨 Icon Components

### 1. SchoolIcon
```jsx
import { SchoolIcon } from "@/components/outreach/Icons";

// Use with size prop
<SchoolIcon size="sm" />   {/* w-8 h-8 */}
<SchoolIcon size="md" />   {/* w-10 h-10 (default) */}
<SchoolIcon size="lg" />   {/* w-12 h-12 */}
```

**Styling:**
- Background: Blue (#EEF2FF)
- Container: Rounded-xl with padding
- Icon color: Blue (#4F6EF7)

---

### 2. ScoreIcon
```jsx
import { ScoreIcon } from "@/components/outreach/Icons";

<ScoreIcon size="md" />
```

**Styling:**
- Background: Amber/Yellow (#FFFBEB)
- Container: Rounded-xl with padding
- Icon color: Amber (#F59E0B)

---

### 3. PriorityIcon
```jsx
import { PriorityIcon } from "@/components/outreach/Icons";

<PriorityIcon size="md" />
```

**Styling:**
- Background: Red (#FFF1F2)
- Container: Rounded-xl with padding
- Icon color: Red (#F43F5E)

---

## 🏆 Insight Card Component

### Complete Insight Card
```jsx
import { InsightsSection } from "@/components/outreach/InsightsSection";

<InsightsSection
  totalSchools={41760}
  averageScore={53.5}
  highPriority={7}
/>
```

### Card Layout
```
┌──────────────────────────────────┐
│ [ICON]  TOTAL SCHOOLS            │
│         41,760                   │
└──────────────────────────────────┘
```

**Grid Responsiveness:**
- Mobile (< 640px): 1 column
- Tablet (640px - 1024px): 2 columns
- Desktop (1024px+): 3 columns

---

## 🎯 Usage Examples

### Basic Usage in Dashboard
```jsx
import { InsightsSection } from "@/components/outreach/InsightsSection";

function Dashboard() {
  const [data, setData] = useState({
    totalSchools: 28820,
    averageScore: 46.0,
    highPriority: 2,
  });

  return (
    <main>
      <InsightsSection
        totalSchools={data.totalSchools}
        averageScore={data.averageScore}
        highPriority={data.highPriority}
      />
      {/* Rest of dashboard */}
    </main>
  );
}
```

### Using Individual Icons Elsewhere
```jsx
import { SchoolIcon, ScoreIcon, PriorityIcon } from "@/components/outreach/Icons";

function CustomCard() {
  return (
    <div className="p-6 bg-white rounded-lg">
      <div className="flex gap-4">
        <SchoolIcon size="lg" />
        <div>
          <h3>Schools</h3>
          <p>28,820</p>
        </div>
      </div>
    </div>
  );
}
```

### Size Variants
```jsx
// Small (w-8 h-8)
<SchoolIcon size="sm" />

// Medium (w-10 h-10) - default
<ScoreIcon size="md" />

// Large (w-12 h-12)
<PriorityIcon size="lg" />
```

---

## 🎨 Styling Breakdown

### Icon Containers
Each icon is wrapped in a rounded container:

```jsx
<div className="inline-flex items-center justify-center p-2.5 bg-blue-50 rounded-xl">
  {/* Icon SVG */}
</div>
```

**Container Classes:**
- `inline-flex` - flex container, inline
- `items-center justify-center` - center content
- `p-2.5` - 10px padding
- `rounded-xl` - rounded corners
- `bg-blue-50` / `bg-amber-50` / `bg-red-50` - light background

### Insight Cards

```jsx
<div className="
  flex items-center gap-4 p-4 sm:p-5
  bg-white rounded-xl border border-gray-100
  shadow-sm hover:shadow-md transition-shadow
">
  {/* Icon + Content */}
</div>
```

**Card Classes:**
- `flex items-center gap-4` - horizontal layout
- `p-4 sm:p-5` - responsive padding
- `bg-white` - white background
- `rounded-xl` - rounded corners
- `border border-gray-100` - subtle border
- `shadow-sm hover:shadow-md` - subtle shadow with hover

---

## 📱 Responsive Behavior

### Mobile (< 640px)
```
Insights
┌─────────────┐
│ [ICON] TEXT │
│ VALUE       │
└─────────────┘
┌─────────────┐
│ [ICON] TEXT │
│ VALUE       │
└─────────────┘
```
- 1 column layout
- 16px padding (p-4)
- 12px gap
- Smaller text

### Tablet (640px - 1024px)
```
Insights
┌─────────────┐ ┌─────────────┐
│ [ICON] TEXT │ │ [ICON] TEXT │
│ VALUE       │ │ VALUE       │
└─────────────┘ └─────────────┘
┌─────────────┐
│ [ICON] TEXT │
│ VALUE       │
└─────────────┘
```
- 2 column layout
- 20px padding (p-5)
- 16px gap
- Medium text

### Desktop (1024px+)
```
Insights
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ [ICON] TEXT │ │ [ICON] TEXT │ │ [ICON] TEXT │
│ VALUE       │ │ VALUE       │ │ VALUE       │
└─────────────┘ └─────────────┘ └─────────────┘
```
- 3 column layout
- 24px padding (p-6)
- 16px gap
- Larger text (text-2xl)

---

## ✨ Features

### Design
- ✅ Tailwind-only styling
- ✅ Consistent spacing and padding
- ✅ Subtle shadows and borders
- ✅ Color-coded backgrounds
- ✅ Smooth hover transitions

### Accessibility
- ✅ ARIA labels on icons
- ✅ Semantic HTML
- ✅ Focus ring on cards
- ✅ Readable text contrast
- ✅ Proper label hierarchy

### Performance
- ✅ Memoized components
- ✅ No unnecessary re-renders
- ✅ Optimized SVGs
- ✅ No extra dependencies

### Responsiveness
- ✅ Mobile-first design
- ✅ Tablet optimization
- ✅ Desktop layout
- ✅ No overflow issues
- ✅ Proper spacing at all sizes

---

## 🔧 Customization

### Changing Colors
Edit Icons.jsx to modify background colors:

```jsx
// SchoolIcon background
<div className="...bg-blue-50 rounded-xl">

// Change to different shade:
<div className="...bg-blue-100 rounded-xl">
```

### Changing Size
Use the size prop:
```jsx
<SchoolIcon size="lg" />  // Makes it w-12 h-12

// Or add new size in Icons.jsx:
const sizeMap = {
  xs: "w-6 h-6",
  sm: "w-8 h-8",
  md: "w-10 h-10",
  lg: "w-12 h-12",
  xl: "w-16 h-16",
};
```

### Changing Card Layout
Modify InsightCard styling:

```jsx
<div className="
  flex items-center gap-4 p-4 sm:p-5
  bg-white rounded-xl border border-gray-100
  shadow-sm hover:shadow-md
  {/* Add new classes */}
">
```

---

## 🐛 Common Issues & Solutions

### Icon not showing
```jsx
// ❌ Wrong
<SchoolIcon />

// ✅ Correct
<SchoolIcon size="md" />
```

### Card layout broken
```jsx
// Make sure gap and flex are set correctly
<div className="flex items-center gap-4">
  {/* Icon on left, content on right */}
</div>
```

### Not responsive
```jsx
// Include responsive classes
<div className="p-4 sm:p-5">  {/* Responds to breakpoints */}
```

---

## 📊 Integration Checklist

- [x] 3 separate icon components created
- [x] Icons wrapped in colored containers
- [x] InsightCard displays icon + text
- [x] Cards responsive (1 → 2 → 3 columns)
- [x] Proper spacing and padding
- [x] Hover effects on cards
- [x] Accessibility improved
- [x] Memoized for performance
- [x] No breaking changes
- [x] Production ready

---

## 🎓 Best Practices

### ✅ DO
```jsx
// Use memoization
const metrics = useMemo(() => [...], []);

// Size icons appropriately
<SchoolIcon size="md" />

// Responsive padding
className="p-4 sm:p-5"

// Proper spacing
gap-4
```

### ❌ DON'T
```jsx
// Don't change icon size in SVG
<SchoolIcon className="w-20 h-20" />

// Don't remove container
// (icon needs the background)

// Don't hardcode sizes
className="p-10"  // Use Tailwind scale

// Don't remove gap
className="flex items-center"  // Add gap-4
```

---

## 📝 Summary

**3 Icon Components:**
- SchoolIcon (Blue)
- ScoreIcon (Amber)
- PriorityIcon (Red)

**1 Card Component:**
- InsightCard (with icon, label, value)

**1 Section Component:**
- InsightsSection (responsive grid)

All components are:
- ✅ Production-ready
- ✅ Fully responsive
- ✅ Accessible
- ✅ Properly memoized
- ✅ Well-documented

---

*Ready to use in production!*
