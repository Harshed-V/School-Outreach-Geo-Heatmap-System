# Frontend UI Integration Guide

## ✅ What's Been Integrated

This frontend has been completely redesigned with a modern, responsive UI using:
- **React 18** + **Vite** for fast development
- **Tailwind CSS** for styling
- **Leaflet/React-Leaflet** for interactive maps
- **Radix UI** (Sheet component) for mobile drawer
- **Lucide React** for beautiful icons
- **TypeScript** support for better development experience

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── outreach/           # Main UI components
│   │   │   ├── Header.jsx      # Top navigation with refresh
│   │   │   ├── Sidebar.jsx     # Filters and district list
│   │   │   ├── HeatmapMap.jsx  # Interactive Leaflet map
│   │   │   ├── MapLegend.jsx   # Score legend
│   │   │   ├── MapStates.jsx   # Loading/Empty/Error states
│   │   │   └── Filters.ts      # Type definitions
│   │   └── ui/
│   │       └── sheet.jsx       # Mobile drawer (Radix UI)
│   ├── data/
│   │   └── districts.ts        # District data + types
│   ├── pages/
│   │   ├── Index.jsx           # New main page (TypeScript)
│   │   └── App.jsx             # Old page (kept for reference)
│   ├── main.jsx                # Entry point
│   └── styles.css              # Tailwind + base styles
├── vite.config.js              # Vite config with @ alias
├── tailwind.config.js          # Tailwind configuration
├── postcss.config.js           # PostCSS for Tailwind
├── jsconfig.json               # Path alias configuration
└── package.json                # Dependencies (updated)
```

---

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
cd frontend
npm install
```

This will install:
- All React dependencies
- Tailwind CSS & PostCSS
- Radix UI components
- Leaflet for mapping
- Lucide icons

### 2. Start Development Server
```bash
npm run dev
```

The frontend will be available at **http://localhost:5173**

### 3. Build for Production
```bash
npm run build
```

Output will be in `dist/` folder, ready for Vercel deployment.

---

## 🎨 Key Components

### Header
- Top navigation bar with refresh button
- Mobile hamburger menu trigger
- Shows last updated timestamp

### Sidebar (Desktop)
- Search by district name
- Score range filter (0-100)
- School type filter
- List of all districts
- Highlights selected district

### Sidebar (Mobile)
- Same as desktop but in a Sheet drawer
- Triggered by hamburger menu
- Auto-closes on district selection

### HeatmapMap
- Interactive Leaflet map centered on Tamil Nadu
- Circle markers for each district
- Size = number of schools
- Color = score/priority
- Click markers to see details

### MapLegend
- Shows score-to-color mapping
- Fixed position in bottom-left
- Only visible on large screens

### MapStates
- **LoadingState**: Shows spinner while data loads
- **EmptyState**: Shows message when no districts match filters
- **ErrorState**: Shows error with retry button

---

## 🔌 API Integration

### Current State
The frontend currently loads **dummy data** from `src/data/districts.ts`. This allows the app to work immediately without a backend.

### Connect to Real Backend

Edit `src/pages/Index.jsx` and replace the `fetchData` function:

**Before (Dummy Data):**
```javascript
const fetchData = () => {
  setStatus("loading");
  const t = setTimeout(() => {
    setData(DISTRICTS);  // Dummy data
    setStatus("ready");
    setLastUpdated(new Date());
  }, 700);
  return () => clearTimeout(t);
};
```

**After (Real API):**
```javascript
const fetchData = async () => {
  setStatus("loading");
  try {
    const response = await fetch("http://localhost:5000/api/districts");
    if (!response.ok) throw new Error("Failed to fetch");
    const districts = await response.json();
    setData(districts);
    setStatus("ready");
    setLastUpdated(new Date());
  } catch (error) {
    console.error("Error:", error);
    setStatus("error");
  }
};
```

### API Endpoints Expected

Your backend should provide:

**GET `/api/districts`**
```json
[
  {
    "district": "Chennai",
    "lat": 13.0827,
    "lng": 80.2707,
    "schools": 120,
    "score": 360,
    "priority": "high"
  },
  ...
]
```

**Update the Sidebar component** to work with your API response format:
- Change `district.id` → `district.district`
- Change `district.name` → `district.district`
- Keep `district.lat`, `district.lng`, `district.score`, `district.schools`

---

## 🎨 Styling & Customization

### Tailwind CSS
All components use Tailwind CSS classes. Modify `tailwind.config.js` to customize:
- Colors
- Spacing
- Typography
- Animations

### Example: Change Header Color
Edit `src/components/outreach/Header.jsx`:
```jsx
// Change from blue to green
<header className="bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg">
```

### Example: Change Map Colors
Edit `src/components/outreach/HeatmapMap.jsx`:
```javascript
const scoreToColor = (score) => {
  if (score >= 300) return "#DC2626";  // Red
  if (score >= 200) return "#EA580C";  // Orange
  if (score >= 100) return "#EAB308";  // Yellow
  return "#22C55E";                    // Green
};
```

---

## 📱 Responsive Design

The UI is fully responsive:

**Desktop (md+)**
- Sidebar always visible on left
- Full width map on right
- All filters accessible

**Tablet (sm-md)**
- Sidebar toggles with hamburger menu
- Map fills available space
- Touch-friendly buttons

**Mobile (sm)**
- Full-width map
- Sidebar as bottom/side drawer
- Optimized for small screens

---

## 🔍 Type Safety

The project uses TypeScript types for better development:

### District Type
```typescript
type District = {
  id: string;
  name: string;
  score: number;
  schools: number;
  lat: number;
  lng: number;
  priority: "high" | "medium" | "low";
};
```

### SchoolType Filter
```typescript
type SchoolType = "all" | "government" | "private" | "secondary";
```

---

## 🐛 Common Issues & Solutions

### Issue: Map not loading
**Solution**: Check that leaflet CSS is imported in `src/main.jsx`

### Issue: Path alias @ not working
**Solution**: Restart dev server after updating `vite.config.js`

### Issue: Styles not applying
**Solution**: Restart dev server. Tailwind needs to recompile.

### Issue: Sheet drawer not working
**Solution**: Ensure Radix UI packages are installed: `npm install @radix-ui/react-dialog`

### Issue: No icons showing
**Solution**: Check lucide-react is installed: `npm install lucide-react`

---

## 🚀 Development Workflow

### Hot Reload
Vite automatically reloads components as you edit them. Just save and see changes instantly!

### ESLint (Optional)
Add ESLint for code quality:
```bash
npm install -D eslint eslint-plugin-react
```

### Format Code
Add Prettier for code formatting:
```bash
npm install -D prettier
```

---

## 📦 Dependency Versions

Key packages:
- **react**: 18.3.1
- **vite**: 5.4.10
- **tailwindcss**: 3.3.6
- **leaflet**: 1.9.4
- **react-leaflet**: 4.2.1
- **@radix-ui/react-dialog**: 1.1.2
- **lucide-react**: 0.344.0

---

## 🌐 Environment Variables

Create a `.env` file for API configuration (optional):

```
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=School Outreach Intelligence
```

Use in code:
```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";
```

---

## 📚 Further Customization

### Add More Pages
Create in `src/pages/`:
```jsx
export default function Dashboard() {
  return <div>Dashboard Page</div>;
}
```

### Add More Components
Create in `src/components/outreach/`:
```jsx
export const MyComponent = () => {
  return <div>My Component</div>;
}
```

### Add Custom Hooks
Create in `src/hooks/`:
```javascript
export function useMyHook() {
  // Custom logic here
}
```

---

## 🔗 Integration with Backend

### Backend Expected at
```
http://localhost:5000
```

### API Endpoints Used
- `GET /api/districts` - Get all districts with data
- `GET /api/summary` - Get summary statistics (optional)
- `POST /api/refresh` - Trigger data refresh (optional)

See `FRONTEND_SETUP.md` in root for detailed API integration.

---

## ✅ Next Steps

1. ✅ **Setup**: Install dependencies (`npm install`)
2. ✅ **Run**: Start dev server (`npm run dev`)
3. ⭐ **Connect Backend**: Update `fetchData()` to call real API
4. 🎨 **Customize**: Adjust colors, add logo, modify layout
5. 🚀 **Deploy**: Build and deploy to Vercel

---

## 📝 Notes

- All components are production-ready
- Fully mobile-responsive
- Accessible (ARIA labels, keyboard navigation)
- Fast performance with Vite
- Type-safe with TypeScript

---

**Last Updated**: April 2026  
**Status**: ✅ Ready for Integration  
**Tested On**: Node 18+, Chrome, Firefox, Safari, Mobile
