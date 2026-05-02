# Production Component Best Practices

## Quick Reference

### Component Usage

#### InsightsSection
```jsx
import { InsightsSection } from "@/components/outreach/InsightsSection";

// In your component
<InsightsSection
  totalSchools={totalSchools}
  averageScore={avgScore}
  highPriority={priorityCount}
/>
```

#### Icons
```jsx
import { SchoolIcon, ScoreIcon, PriorityIcon } from "@/components/outreach/Icons";

// Use with size control
<SchoolIcon className="w-6 h-6" />
<ScoreIcon className="w-10 h-10" />
<PriorityIcon className="w-12 h-12" />
```

---

## Layout Patterns

### ✅ DO - Correct Layout Pattern
```jsx
<div className="flex flex-col h-screen overflow-hidden">
  <header className="flex-shrink-0">Header</header>
  <div className="flex flex-1 min-h-0 overflow-hidden">
    <aside className="hidden md:flex w-80 flex-shrink-0 overflow-y-auto">
      Sidebar
    </aside>
    <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
      Content
    </main>
  </div>
</div>
```

### ❌ DON'T - Avoid These Patterns
```jsx
// ❌ This breaks responsive layout
<div className="h-screen w-screen">
  <div className="h-screen"> {/* Nested h-screen breaks things */}
  
// ❌ This causes overflow
<div className="overflow-auto">
  <div className="w-[90vw]"> {/* Can exceed container */}

// ❌ This doesn't resize with parent
<aside className="w-80"> {/* Fixed width, won't fit mobile */}
```

---

## State Management Best Practices

### ✅ DO - Memoize Callbacks
```jsx
const handleChange = useCallback((value) => {
  setState(value);
}, []);

// In JSX
<Input onChange={handleChange} />
```

### ✅ DO - Memoize Expensive Computations
```jsx
const filtered = useMemo(() => {
  return data.filter(item => {
    // complex logic
    return item.score >= scoreRange[0];
  });
}, [data, scoreRange]);
```

### ✅ DO - Memoize Derived Props Objects
```jsx
const sidebarProps = useMemo(() => ({
  allDistricts: data,
  filteredDistricts: filtered,
  // ... other props
}), [data, filtered]); // Include all dependencies
```

### ❌ DON'T - Inline Object Props
```jsx
// ❌ Creates new object every render
<Sidebar props={{ a: 1, b: 2 }} />

// ✅ Use useMemo or define outside
const props = useMemo(() => ({ a: 1, b: 2 }), []);
```

---

## Responsive Design Patterns

### ✅ Mobile-First Approach
```jsx
// Start with mobile, add complexity
<div className="p-4 md:p-6 lg:p-8">
  <h1 className="text-lg sm:text-xl md:text-2xl">Title</h1>
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
    {/* Items */}
  </div>
</div>
```

### ✅ Hide/Show Based on Breakpoints
```jsx
// Desktop only
<aside className="hidden md:flex">Desktop Sidebar</aside>

// Mobile only
<button className="md:hidden">Mobile Menu</button>

// Responsive width
<div className="w-full md:w-80 lg:w-96">Content</div>
```

### ✅ Responsive Spacing
```jsx
<div className="p-4 sm:p-5 md:p-6 lg:p-8">
  <div className="gap-3 sm:gap-4 md:gap-6">
    {/* Children */}
  </div>
</div>
```

---

## Touch & Accessibility

### ✅ DO - Touch-Friendly Sizes
```jsx
// Minimum 44x44px touch target
<button className="px-3 py-2.5"> {/* ~44px height */}
  Click me
</button>

// Better spacing on mobile
<div className="space-y-3 sm:space-y-4">
  <button>Item 1</button>
  <button>Item 2</button>
</div>
```

### ✅ DO - Add Tactile Feedback
```jsx
<button className="
  transition-all duration-200
  hover:bg-gray-100
  active:scale-95
  focus:outline-none focus:ring-2 focus:ring-blue-400
">
  Click
</button>
```

### ✅ DO - Proper Labels & ARIA
```jsx
<label htmlFor="search">Search</label>
<input id="search" type="text" />

<button aria-label="Open menu">☰</button>
<div aria-current="page">Active</div>
<button aria-busy={isLoading}>Load</button>
```

---

## Performance Tips

### Preventing Unnecessary Re-renders
```jsx
// ✅ Good: Component only re-renders when specific props change
const DistrictItem = memo(({ district, isActive, onSelect }) => (
  <button onClick={() => onSelect(district)}>
    {district.name}
  </button>
));

// ❌ Bad: All list items re-render when any filter changes
<div>
  {districts.map(d => <DistrictItem district={d} />)}
</div>
```

### Optimizing Lists
```jsx
// ✅ Always use stable IDs
{items.map(item => (
  <Item key={item.id} item={item} />
))}

// ❌ Never use index as key
{items.map((item, index) => (
  <Item key={index} item={item} /> // BAD!
))}
```

### Bundle Size
```jsx
// ✅ SVG icons are inline (no extra requests)
<SchoolIcon className="w-6 h-6" />

// Consider for larger images
import { Suspense, lazy } from 'react';
const HeavyComponent = lazy(() => import('./Heavy'));
```

---

## Common Issues & Solutions

### Issue: Sidebar Overflow on Mobile
**Solution:**
```jsx
// Use flex-shrink-0 and min-w-0
<aside className="w-80 flex-shrink-0 overflow-y-auto">
<main className="flex-1 min-w-0 overflow-auto">
```

### Issue: Map Not Resizing
**Solution:**
```jsx
// Container must have flex-1 with explicit overflow
<div className="flex-1 relative min-w-0 overflow-hidden">
  <HeatmapMap /> {/* Will fill remaining space */}
</div>
```

### Issue: Drawer Not Closing After Selection
**Solution:**
```jsx
// Include setMobileOpen(false) in callback
const handleSelect = useCallback((d) => {
  setFocused(d);
  setMobileOpen(false); // ← Critical!
}, []);
```

### Issue: Search Input Not Clearing Focus on Mobile
**Solution:**
```jsx
// Use onBlur for better mobile experience
<input
  type="text"
  value={search}
  onChange={(e) => onSearchChange(e.target.value)}
  onBlur={() => {
    // Optional: close keyboard on blur
  }}
/>
```

---

## Testing Guidelines

### Unit Tests
```javascript
import { render, screen } from '@testing-library/react';
import { Sidebar } from '@/components/outreach/Sidebar';

test('displays district count', () => {
  render(<Sidebar filteredDistricts={[...]} {...props} />);
  expect(screen.getByText(/3/)).toBeInTheDocument();
});
```

### Responsive Tests
```javascript
// Test across breakpoints
const renderAtBreakpoint = (component, width) => {
  window.matchMedia = jest.fn().mockImplementation(query => ({
    matches: width >= parseInt(query.match(/\d+/)[0]),
  }));
  return render(component);
};
```

### E2E Tests
```javascript
// With Playwright
test('mobile sidebar opens and closes', async () => {
  await page.goto('/');
  await page.click('button[aria-label="Open sidebar menu"]');
  expect(drawer).toBeVisible();
  await page.click('button[aria-label="District"]');
  expect(drawer).toBeHidden();
});
```

---

## Performance Checklist

- [ ] All callbacks wrapped in useCallback
- [ ] Heavy computations wrapped in useMemo
- [ ] Component props objects wrapped in useMemo
- [ ] List items use stable keys (not index)
- [ ] Child components memoized where appropriate
- [ ] No inline object/array literals as props
- [ ] No unnecessary state updates
- [ ] Proper cleanup in useEffect

---

## Deployment Checklist

- [ ] Run `npm run build`
- [ ] Check bundle size: `npm run build -- --analyze`
- [ ] Lighthouse score > 90 on mobile
- [ ] No console warnings/errors
- [ ] Responsive testing on real devices
- [ ] Touch interactions tested
- [ ] Screen reader tested
- [ ] Cross-browser tested

---

**Keep these patterns in mind when extending the application!**
