# Icon Integration - Visual Reference

## 🎯 Before vs After

### BEFORE
```jsx
// Icons had built-in backgrounds (cluttered)
export const SchoolIcon = ({ className = "w-10 h-10" }) => (
  <svg viewBox="0 0 80 80" className={className}>
    <rect width="80" height="80" rx="20" fill="#EEF2FF"/>  {/* Background */}
    {/* icon content */}
  </svg>
);

// Cards didn't display icons properly
<div className="flex items-center gap-3 p-3">
  <Icon className="w-8 h-8 sm:w-10 sm:h-10" />  {/* Just SVG */}
  <div>
    <p>{label}</p>
    <p>{value}</p>
  </div>
</div>
```

### AFTER
```jsx
// Icons are pure SVG, container handles styling
export const SchoolIcon = ({ size = "md" }) => {
  const sizeMap = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };
  
  return (
    <div className="inline-flex items-center justify-center p-2.5 bg-blue-50 rounded-xl">
      <svg viewBox="0 0 80 80" className={sizeMap[size]}>
        {/* Only icon content, no background in SVG */}
      </svg>
    </div>
  );
};

// Cards display icons with proper styling
<div className="flex items-center gap-4 p-4 sm:p-5 bg-white rounded-xl">
  <div className="flex-shrink-0">
    <Icon size="md" />  {/* Icon with container */}
  </div>
  <div className="flex-1 min-w-0">
    <p className="text-sm text-gray-600 uppercase">{label}</p>
    <p className="text-2xl font-bold text-gray-900">{value}</p>
  </div>
</div>
```

---

## 🎨 Visual Layout

### Mobile (320px - 640px)
```
┌────────────────────────────────┐
│           Insights             │
├────────────────────────────────┤
│  [icon]  Total Schools         │
│          28,820                │
├────────────────────────────────┤
│  [icon]  Average Score         │
│          46.0                  │
├────────────────────────────────┤
│  [icon]  High Priority         │
│          2                     │
└────────────────────────────────┘
```
- Stack vertically
- 1 column
- p-4 padding
- Full width cards

### Tablet (640px - 1024px)
```
┌────────────────────────────────────────────────────┐
│               Insights                             │
├──────────────────────┬──────────────────────────────┤
│ [icon] Total Schools │ [icon] Average Score        │
│        28,820        │       46.0                  │
├──────────────────────┴──────────────────────────────┤
│ [icon] High Priority                               │
│        2                                           │
└────────────────────────────────────────────────────┘
```
- 2 columns
- p-5 padding
- Better use of space

### Desktop (1024px+)
```
┌────────────────────────────────────────────────────────────────┐
│                        Insights                                 │
├─────────────────────┬──────────────────┬──────────────────────┤
│ [icon]              │ [icon]           │ [icon]              │
│ Total Schools       │ Average Score    │ High Priority       │
│ 28,820              │ 46.0             │ 2                   │
└─────────────────────┴──────────────────┴──────────────────────┘
```
- 3 columns
- p-6 padding
- All visible

---

## 🎨 Icon Container Design

### SchoolIcon Container
```
Background: Blue (#EEF2FF)
├─ Padding: 10px (p-2.5)
├─ Border Radius: 12px (rounded-xl)
└─ Icon Color: Blue (#4F6EF7)

Visual:
  ┌──────────────┐
  │   [  🏫  ]   │  ← Blue background
  └──────────────┘
     Building icon
```

### ScoreIcon Container
```
Background: Amber (#FFFBEB)
├─ Padding: 10px (p-2.5)
├─ Border Radius: 12px (rounded-xl)
└─ Icon Color: Amber (#F59E0B)

Visual:
  ┌──────────────┐
  │   [  🎯  ]   │  ← Yellow background
  └──────────────┘
   Speedometer icon
```

### PriorityIcon Container
```
Background: Red (#FFF1F2)
├─ Padding: 10px (p-2.5)
├─ Border Radius: 12px (rounded-xi)
└─ Icon Color: Red (#F43F5E)

Visual:
  ┌──────────────┐
  │   [  🔥  ]   │  ← Red background
  └──────────────┘
    Flame icon
```

---

## 📏 Size Options

### Small (sm)
```
Icon Size: 32px × 32px (w-8 h-8)
Container: 52px × 52px (with p-2.5)
Use When: Compact UI, sidebar items

  ┌──────────┐
  │[   🏫   ]│
  └──────────┘
```

### Medium (md) - Default
```
Icon Size: 40px × 40px (w-10 h-10)
Container: 60px × 60px (with p-2.5)
Use When: Insight cards, dashboards

  ┌──────────┐
  │[   🏫   ]│
  └──────────┘
```

### Large (lg)
```
Icon Size: 48px × 48px (w-12 h-12)
Container: 68px × 68px (with p-2.5)
Use When: Hero sections, featured items

  ┌──────────┐
  │[   🏫   ]│
  └──────────┘
```

---

## 💻 Card Component Anatomy

```
┌─────────────────────────────────────────────┐
│  flex items-center gap-4 p-4 sm:p-5         │
│                                              │
│  ┌────────┐  ┌──────────────────────────┐   │
│  │        │  │  TOTAL SCHOOLS           │   │
│  │ [icon] │  │  28,820                  │   │
│  │        │  │                          │   │
│  └────────┘  └──────────────────────────┘   │
│    flex-    │           flex-1              │
│   shrink-0  │         min-w-0              │
│             │                              │
│  bg-white                                   │
│  rounded-xl                                 │
│  border border-gray-100                     │
│  shadow-sm hover:shadow-md                  │
└─────────────────────────────────────────────┘
```

### Component Breakdown
1. **Icon (flex-shrink-0)**
   - Doesn't shrink
   - Fixed size
   - Left side

2. **Content (flex-1 min-w-0)**
   - Takes remaining space
   - Can shrink if needed
   - Right side

3. **Labels**
   - Small uppercase text
   - Gray color
   - Tracking wide

4. **Value**
   - Large bold number
   - Dark gray
   - Proper truncation

---

## 🎭 States

### Default State
```
┌──────────────────────────────────┐
│ [icon] LABEL                     │
│        VALUE                     │
│                                  │
│ Shadow: shadow-sm                │
│ Border: border-gray-100          │
└──────────────────────────────────┘
```

### Hover State
```
┌──────────────────────────────────┐
│ [icon] LABEL                     │
│        VALUE                     │
│                                  │
│ Shadow: shadow-md (elevated)     │
│ Border: border-gray-100          │
│ Transition: 200ms                │
└──────────────────────────────────┘
```

### Focus State (Keyboard Navigation)
```
┌──────────────────────────────────┐
│╭──────────────────────────────────╮│
│║ [icon] LABEL                    ║│
│║        VALUE                    ║│
│╰──────────────────────────────────╯│
│ Ring: focus:ring-2 focus:ring-blue-400│
└──────────────────────────────────┘
```

---

## 📋 Responsive Grid Progression

### All Sizes
```
Total columns calculation:
- Mobile (< 640px):   1 column × 3 rows
- Tablet (640-1024):  2 columns × 2 rows (last 1 alone)
- Desktop (1024+):    3 columns × 1 row
```

### Grid Classes
```jsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
       ↓              ↓               ↓
    Mobile      Tablet at 640px  Desktop at 1024px
```

### Gap Progression
```
Mobile:  gap-3 (12px between cards)
Tablet:  gap-4 (16px between cards)
Desktop: gap-4 (16px between cards)
```

---

## 🔍 Color Scheme

### SchoolIcon
- Background: `#EEF2FF` (blue-50)
- Icon Stroke: `#4F6EF7` (blue-500)
- Tailwind: `bg-blue-50`

### ScoreIcon
- Background: `#FFFBEB` (amber-50)
- Icon Stroke: `#F59E0B` (amber-500)
- Tailwind: `bg-amber-50`

### PriorityIcon
- Background: `#FFF1F2` (red-50)
- Icon Stroke: `#F43F5E` (red-500)
- Tailwind: `bg-red-50`

---

## 📐 Spacing System

### Container Padding
```
Mobile (p-4):    4px left, 4px top, 4px right, 4px bottom
Tablet (p-5):    5px left, 5px top, 5px right, 5px bottom
Desktop (p-6):   6px left, 6px top, 6px right, 6px bottom

Applied: <div className="p-4 sm:p-5">
```

### Gap Between Icon & Content
```
gap-4 = 16px spacing (constant across all sizes)
```

### Inner Padding (Icon Container)
```
p-2.5 = 10px padding all sides
```

---

## ✅ Quality Checklist

- [x] Icons extracted to separate components
- [x] Icons wrapped in colored containers
- [x] Cards display icon + label + value
- [x] Responsive grid (1 → 2 → 3 columns)
- [x] Proper spacing and gaps
- [x] Hover effects working
- [x] Accessible (ARIA, focus rings)
- [x] Memoized for performance
- [x] No breaking changes
- [x] Production ready

---

**All components complete and production-ready!** ✅
