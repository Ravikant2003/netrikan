# Quick Start Guide

Get the Netrikan Web App running in 5 minutes.

## ⚡ TL;DR

```bash
# 1. Navigate to web app
cd web_app

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open browser to http://localhost:5173
```

Done! You're running the app. 🎉

---

## 📋 Prerequisites

Verify you have:

```bash
node --version  # Should be v16.0.0 or higher
npm --version   # Should be 7.0.0 or higher
```

If not, [install Node.js](https://nodejs.org/)

---

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Directory (30 seconds)

```bash
cd /path/to/Netrikan\ copy/web_app
```

### Step 2: Install Dependencies (2-3 minutes)

```bash
npm install
```

This installs all packages listed in `package.json`:
- React 18
- TypeScript 5
- Vite 5
- Axios
- And dev tools

### Step 3: Create Environment File (30 seconds)

```bash
# Copy the example file
cp .env.example .env.local

# Or create manually with:
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
echo "VITE_APP_NAME=Netrikan" >> .env.local
```

### Step 4: Start Development Server (10 seconds)

```bash
npm run dev
```

You'll see:
```
VITE v5.0.0  ready in 123 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Step 5: Open in Browser (immediate)

Visit: **http://localhost:5173**

You should see the Netrikan landing page! 🎉

---

## ✨ What You're Seeing

The landing page includes:

1. **Header** - Logo, navigation, theme toggle, emergency button
2. **Hero Section** - Welcome message with animated blobs
3. **Stats** - 4 key metrics about the app
4. **Features** - 6 core feature cards
5. **Call to Action** - Start using buttons

### Test the App

- **Toggle Theme**: Click moon icon in header (top right)
- **Navigate**: Click navigation links
- **Test Buttons**: Click any button to see interactions
- **Responsive**: Resize browser window to see mobile view

---

## 🎨 Explore Features

### HomeScreen (/ or /home)
- Landing page with statistics
- Feature showcase
- Get started buttons

### RouteMapScreen (/route)
- Search for locations
- View optimized routes
- See safety scores
- Route comparison

### SafetyScoreScreen (/safety)
- Safety metrics dashboard
- Risk assessment
- Trip history
- Location insights

### EmergencyScreen (/emergency)
- Large SOS button
- Emergency type selection
- Emergency contacts
- Safety tips

### LiveTrackingScreen (/tracking)
- Share location
- Track others
- Sharing settings
- Privacy controls

---

## 🔌 API Integration

The app is ready to connect to the backend!

### Verify Backend Connection

1. Make sure FastAPI backend is running on `http://localhost:8000`
2. Open browser console (F12)
3. Run:

```javascript
fetch('/api/health')
  .then(r => r.json())
  .then(console.log)
```

You should see: `{ status: "ok" }`

### Configure API URL

If your backend is on a different URL, edit `.env.local`:

```env
VITE_API_BASE_URL=https://your-backend-url.com
VITE_APP_NAME=Netrikan
```

Restart the dev server and it will use the new URL.

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](./README.md) | Project overview and features |
| [SETUP.md](./SETUP.md) | Detailed installation guide |
| [API_DOCS.md](./API_DOCS.md) | Backend API integration |
| [COMPONENTS.md](./COMPONENTS.md) | Component API reference |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Project structure and design |
| [MIGRATION.md](./MIGRATION.md) | Mobile → Web migration guide |

---

## 🎯 Common Tasks

### Change API Backend URL

Edit `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:3000
```

### Stop Development Server

Press `Ctrl+C` in terminal

### Create Production Build

```bash
npm run build

# View build output in dist/ folder
# ~45KB gzipped
```

### Preview Production Build

```bash
npm run preview

# Opens http://localhost:4173
```

### Check for Code Issues

```bash
npm run lint
```

### Run Tests

```bash
npm run test
```

---

## 🐛 Troubleshooting

### Issue: Port 5173 Already in Use

```bash
# Use a different port
npm run dev -- --port 3000
```

### Issue: API Connection Failed

```bash
# Check if backend is running
curl http://localhost:8000/health

# If error, start your backend service
# Ensure CORS is configured in backend
```

### Issue: Module Not Found

```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

### Issue: Blank Page

1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Clear cache and reload

### Issue: Changes Not Reflecting

```bash
# Stop dev server (Ctrl+C)
# Start again
npm run dev
```

---

## 🎨 Theme Switching

### Dark/Light Mode

Click the moon icon ☾ in the top-right header

The theme will:
- Switch immediately
- Save to browser storage
- Apply to all pages

### Manual Override

In browser console:
```javascript
localStorage.setItem('theme', 'dark')  // or 'light'
location.reload()
```

---

## 📱 Responsive Testing

The app is fully responsive!

### Test Different Sizes

In browser DevTools (F12):
1. Click device icon (top left)
2. Select device or set custom width:
   - **Mobile**: 375px (iPhone)
   - **Tablet**: 768px (iPad)
   - **Desktop**: 1024px+ (laptop)

All components adapt automatically.

---

## 🚀 Next Steps

### To Continue Development

1. ✅ App is running - check!
2. 📖 Read [COMPONENTS.md](./COMPONENTS.md) - learn component API
3. 🎨 Read [ARCHITECTURE.md](./ARCHITECTURE.md) - understand structure
4. 🔌 Read [API_DOCS.md](./API_DOCS.md) - integrate with backend
5. ✏️ Start editing `src/pages/*.tsx` files

### To Deploy

1. Run `npm run build` to create production build
2. Deploy `dist/` folder to your hosting:
   - Netlify (drag and drop)
   - Vercel (connect GitHub)
   - AWS S3 + CloudFront
   - Any static hosting service

### To Add Features

1. Create new component in `src/components/`
2. Or create new page in `src/pages/`
3. Add route in `src/App.tsx`
4. Check [COMPONENTS.md](./COMPONENTS.md) for patterns

---

## 💡 Tips & Tricks

### Hot Reload
- Edit any `.tsx` or `.css` file
- Changes appear instantly in browser
- No page refresh needed!

### Component Isolation
- Edit one component file
- Only that component updates
- Perfect for development

### Theme Variables
- All colors are CSS variables
- Change theme in `src/theme/theme.ts`
- Affects entire app instantly

### Browser DevTools
- F12 opens developer tools
- "React" tab shows component hierarchy
- "Console" shows JavaScript output
- "Network" shows API requests

---

## 📞 Need Help?

1. **Quick questions**: Check [FAQ section](#faq) below
2. **Setup issues**: See [SETUP.md](./SETUP.md)
3. **Code examples**: See [COMPONENTS.md](./COMPONENTS.md)
4. **API help**: See [API_DOCS.md](./API_DOCS.md)

---

## ❓ FAQ

**Q: Is the backend required?**
A: No for testing UI. Yes for real data. The app has mock data for all screens.

**Q: Can I change the colors?**
A: Yes! Edit `src/theme/theme.ts` and rebuild or use dev server HMR.

**Q: Is it mobile-friendly?**
A: Yes! 100% responsive. Test with DevTools device mode.

**Q: How do I add a new page?**
A: Create `src/pages/MyPage.tsx`, add route in `src/App.tsx`, navigate to it.

**Q: Can I deploy this?**
A: Yes! Run `npm run build`, then deploy `dist/` folder to any static host.

**Q: How do I add authentication?**
A: See COMPONENTS.md for patterns, then implement auth in a new page.

**Q: What about PWA/offline?**
A: Not implemented yet. See ARCHITECTURE.md planned features.

**Q: Can I use this with a different backend?**
A: Yes! Update API client in `src/services/apiClient.ts` to match your backend.

---

## 🎉 You're All Set!

Your Netrikan Web App is ready to use and develop!

**Happy coding!** 🚀

---

**Quick Command Reference:**

```bash
npm run dev          # Start development server 🚀
npm run build        # Create production build 📦
npm run preview      # Preview production build 👀
npm run lint         # Check code quality 🔍
npm run test         # Run unit tests 🧪
npm run type-check   # Check TypeScript 📝
```

---

**Last Updated**: January 2025  
**Web App Version**: 1.0.0  
**Status**: Ready to Use ✅
