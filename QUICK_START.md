# SSDLC Analyzer - Quick Start Guide

## 🚀 Running the Application

### 1. Start the Backend API
```bash
cd "C:\Users\Thoufeek\Desktop\SSDLC Analyzer"
python -m uvicorn backend.back:app --reload
```
**Backend running at**: http://127.0.0.1:8000

### 2. Start the Frontend Dev Server
```bash
cd "C:\Users\Thoufeek\Desktop\SSDLC Analyzer\frontend"
npm run dev
```
**Frontend running at**: http://localhost:5173

### 3. Open in Browser
Navigate to: **http://localhost:5173**

---

## ⌨️ Keyboard Shortcuts

- **⌘K / Ctrl+K** - Open Command Palette
- **ESC** - Close modals/drawers/command palette
- **Arrow Keys** - Navigate command palette
- **Enter** - Execute selected command

---

## 🎨 Key Features Implemented

### Navigation
- **Sidebar** - Main navigation with domain filters
- **Command Palette** (⌘K) - Quick actions and search
- **Topbar** - Breadcrumbs and status indicators

### Assessment Flow
1. **Hero** - Landing page with clear CTAs
2. **Upload** - Drag-and-drop ZIP repository
3. **Scanning** - Live progress with phase tracking
4. **Results** - Animated score reveal + findings
5. **History** - Past assessments with scores

### Domain Filtering
Click any domain in sidebar to filter results:
- Requirements
- Architecture
- Implementation
- Testing
- Supply Chain
- Lifecycle

---

## 📱 Responsive Breakpoints

- **Desktop**: > 900px (Fixed sidebar, full layout)
- **Tablet**: 640px - 900px (Drawer sidebar, 2-col grid)
- **Mobile**: < 640px (Full mobile drawer, 1-col stack)

---

## 🎬 Notable Animations

### Score Reveal
- Counter animates from 0 to actual score (1.2s)
- SVG ring fills simultaneously
- Staggered metric cards appear

### Scanning
- Phase icons transition: pending → active → complete
- Pulse animation on active phase
- Smooth progress bar fill

### Microinteractions
- Buttons lift 1-2px on hover
- Cards elevate on hover with shadow
- Active nav indicator smoothly slides
- Toasts slide in from top-right

---

## 🛠️ Development Commands

```bash
# Frontend
npm run dev      # Start dev server
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # Run linter

# Backend
python -m uvicorn backend.back:app --reload  # Start API
python -m pytest tests/                      # Run tests
```

---

## 📁 Project Structure

```
SSDLC Analyzer/
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── styles/         # CSS design system
│   │   ├── App.jsx         # Main app
│   │   └── main.jsx        # Entry point
│   ├── index.html
│   └── package.json
├── backend/
│   └── back.py             # FastAPI backend
├── scanner/
│   ├── engine.py           # Scan engine
│   ├── checks/             # Security checks
│   └── utils/              # Utilities
└── tests/                  # Test suite
```

---

## 🎯 Testing the UI

### Test Scenarios
1. **Upload flow**: Drag a ZIP file onto upload zone
2. **Scanning**: Watch phase progression and stats
3. **Results**: See score animation and findings
4. **Command Palette**: Press ⌘K, search, navigate
5. **Domain Filter**: Click domain in sidebar
6. **Mobile**: Resize window < 640px
7. **Responsive**: Test at various widths

### Mock Data
If backend isn't running, the frontend will show connection errors but UI remains functional.

---

## 🎨 Design System Reference

### Colors
- Background: `#070a0f`
- Surface: `#0a0e15`
- Panel: `#0c1119`
- Accent: `#6b8aff`
- Success: `#6ee7b7`
- Danger: `#ef9191`

### Typography
- **UI Font**: Inter (400, 500, 600, 700)
- **Mono Font**: DM Mono (400, 500)
- **Scale**: 8px to 68px with clear hierarchy

### Spacing
- **Base**: 4px
- **Scale**: 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 80px

### Motion
- **Fast**: 120ms
- **Normal**: 180ms
- **Slow**: 250ms
- **Slower**: 350ms

---

## 🔧 Customization

### Changing Colors
Edit: `frontend/src/styles/tokens.css`

### Adjusting Animations
Edit: `frontend/src/styles/tokens.css` (duration/easing variables)

### Adding Components
1. Create in `frontend/src/components/`
2. Import in `App.jsx`
3. Add styles to appropriate CSS file

---

## 📸 Screenshots / Visual States

### Main States
1. **Hero** - Initial landing with upload panel
2. **Scanning** - Console with live phase tracking
3. **Results** - Score + domains + findings
4. **Command Palette** - Quick actions overlay
5. **Mobile** - Drawer sidebar open

### Component States
- Upload: idle → hover → dragging → selected
- Scanning: phases progressing with icons
- Results: animated score reveal
- Findings: expandable drawer
- Toasts: success/error notifications

---

## 🎉 What Makes It Premium

✨ **Smooth 60fps animations** throughout  
✨ **Purposeful motion** - every animation communicates  
✨ **Refined typography** - professional hierarchy  
✨ **Consistent spacing** - breathing room everywhere  
✨ **Subtle depth** - layered surfaces, not flat  
✨ **Responsive design** - works on all screen sizes  
✨ **Keyboard-first** - command palette + shortcuts  
✨ **Cinematic transitions** - orchestrated reveals  
✨ **Attention to detail** - hover states, focus rings, microinteractions  

---

## 💡 Tips

- **Use Command Palette** for fastest navigation (⌘K)
- **Domain filters** stay active across views
- **Upload accepts** .zip files only
- **Toasts auto-dismiss** after 4 seconds
- **Sidebar on mobile** - tap hamburger icon
- **Smooth scroll** enabled for long pages
- **Reduced motion** respected from OS settings

---

## 🐛 Troubleshooting

**Frontend won't start**: Check if port 5173 is available  
**Backend connection error**: Ensure backend is running on port 8000  
**CORS errors**: Backend configured for localhost:5173  
**Build fails**: Run `npm install` to ensure dependencies  

---

**Ready to use!** 🚀

Open http://localhost:5173 and experience the premium security platform.
