# Web App Setup Guide

Complete setup instructions for the Netrikan Web App.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js** 16.0.0 or higher ([download](https://nodejs.org/))
- **npm** 7.0.0 or higher (comes with Node.js)
- **Git** for version control
- A code editor (VS Code recommended)
- **FastAPI Backend** running on `localhost:8000`

### Verify Prerequisites

```bash
# Check Node.js version
node --version  # Should be v16.0.0 or higher

# Check npm version
npm --version   # Should be 7.0.0 or higher

# Check Git version
git --version   # Should be git 2.0 or higher
```

## 🚀 Installation Steps

### Step 1: Navigate to Web App Directory

```bash
cd /path/to/Netrikan\ copy/web_app
```

### Step 2: Install Dependencies

```bash
# Install all npm packages
npm install

# This will install:
# - React 18.2.0
# - TypeScript 5.3.0
# - Vite 5.0.0
# - Axios 1.6.0
# - React Router 6.x
# - And development dependencies
```

**Expected Output:**
```
added 150+ packages in XX.XXXs
```

### Step 3: Create Environment File

```bash
# Copy the example env file
cp .env.example .env.local
```

Or manually create `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Netrikan
```

### Step 4: Verify Installation

```bash
# Check that node_modules was created properly
ls -la node_modules | head -20

# Verify package.json is readable
cat package.json | head -30
```

## 💻 Development Server

### Start the Development Server

```bash
# From the web_app directory
npm run dev

# Output should show:
# VITE v5.0.0  ready in XXX ms
# ➜  Local:   http://localhost:5173/
# ➜  press h to show help
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

You should see the Netrikan Web App landing page with:
- Glassmorphism design
- Hero section with animated blobs
- Stats cards
- Feature showcase
- Dark/Light mode toggle in header

### Hot Module Replacement (HMR)

The development server includes HMR—changes to source files automatically reload in the browser without losing state.

```bash
# Edit a component file and save
# The app will automatically update in your browser
```

### Troubleshooting Development Server

**Port Already in Use:**
```bash
# If port 5173 is in use, Vite will try the next available port
# Or specify a custom port:
npm run dev -- --port 3000
```

**Backend Connection Issues:**
```bash
# Check if FastAPI backend is running
curl http://localhost:8000/health

# If connection fails, verify:
# 1. Backend is running on localhost:8000
# 2. CORS is properly configured in backend
# 3. .env.local has correct VITE_API_BASE_URL
```

## 🏗️ Building for Production

### Create Optimized Build

```bash
# Generate optimized production build
npm run build

# Output directory: dist/
# Build time: Usually under 30 seconds
```

**Expected Output:**
```
vite v5.0.0 building for production...
✓ 123 modules transformed
dist/index.html         2.5 kb
dist/assets/main.xxx.js 123.4 kb │ gzip: 45.6 kb
```

### Preview Production Build

```bash
# Start a local server with production build
npm run preview

# Navigate to: http://localhost:4173
```

### Build Output Structure

```
dist/
├── index.html          # Main HTML file
├── assets/
│   ├── main.xxx.js    # Main JavaScript bundle (code-split)
│   ├── vendor.xxx.js  # Vendor dependencies
│   └── *.css          # Compiled stylesheets
└── vite.svg           # Vite logo
```

## 🔌 Backend Integration

### Backend Requirements

The FastAPI backend should be running with:

```bash
# From the backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

### API Proxy Configuration

The development server is configured to proxy API requests:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

This means:
- Frontend request: `http://localhost:5173/api/analyze`
- Proxies to: `http://localhost:8000/analyze`

### Testing API Connection

```bash
# From your browser console or use curl:
curl -X POST http://localhost:5173/api/health

# Or test directly through the web app:
# 1. Open browser DevTools (F12)
# 2. Go to Console tab
# 3. Execute:
fetch('/api/health').then(r => r.json()).then(console.log)
```

## 📦 Dependency Management

### Adding a New Package

```bash
# Install a new npm package
npm install package-name

# Or install as dev dependency
npm install --save-dev package-name
```

### Updating Packages

```bash
# Check for outdated packages
npm outdated

# Update all packages safely
npm update

# Update to latest major versions (breaking changes possible)
npm install package-name@latest
```

### Removing Packages

```bash
npm uninstall package-name
```

## 🎨 Theme Development

### Testing Dark Mode

```bash
# The theme toggle is in the Header component
# Click the moon icon in the top right to switch themes

# Or test programmatically:
# Open browser console and run:
localStorage.setItem('theme', 'dark')
location.reload()
```

### CSS Variable Testing

```bash
# Check applied CSS variables in browser console:
const root = document.documentElement;
const primaryColor = getComputedStyle(root).getPropertyValue('--color-primary');
console.log(primaryColor); // Should print the color value
```

## 🧪 Testing

### Run Unit Tests

```bash
npm run test
```

### Run Tests with Coverage

```bash
npm run test:coverage
```

### Test Specific File

```bash
npm test -- Button.test.tsx
```

## 📊 Code Quality

### Lint Code

```bash
# Check for linting issues
npm run lint

# Auto-fix issues
npm run lint:fix
```

### Type Checking

```bash
# Run TypeScript compiler
npx tsc --noEmit
```

## 🐛 Debugging

### Browser DevTools

1. Open your browser's Developer Tools (F12)
2. Go to the "Sources" tab
3. Set breakpoints in your code
4. Step through execution

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src",
      "sourceMapPathPrefix": "/@vite/"
    }
  ]
}
```

Then press F5 to start debugging.

### React DevTools

1. Install [React DevTools Extension](https://react-devtools-tutorial.vercel.app/)
2. Inspect component props and state
3. Trace component renders

## 📚 Project Scripts

### Available NPM Scripts

```bash
npm run dev          # Start development server
npm run build        # Create production build
npm run preview      # Preview production build locally
npm run lint         # Check code quality
npm run lint:fix     # Auto-fix linting issues
npm run test         # Run unit tests
npm run test:coverage # Run tests with coverage report
npm run type-check   # Run TypeScript compiler
```

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`npm run test`)
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] No linting issues (`npm run lint`)
- [ ] Build succeeds (`npm run build`)
- [ ] Environment variables configured
- [ ] Backend API endpoints verified
- [ ] Dark/light mode tested
- [ ] Responsive design tested (mobile/tablet/desktop)
- [ ] Performance metrics reviewed
- [ ] Browser compatibility tested

## 🔒 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_APP_NAME` | Application name | `Netrikan` |

**Note:** All `VITE_` prefixed variables are exposed to the client at build time.

## 📖 Important Files

| File | Purpose |
|------|---------|
| `package.json` | Dependencies and scripts |
| `vite.config.ts` | Build configuration and server proxy |
| `tsconfig.json` | TypeScript configuration |
| `src/main.tsx` | Application entry point |
| `src/App.tsx` | Root component and routing |
| `src/theme/ThemeContext.tsx` | Theme management |
| `.env.local` | Local environment variables |

## 🆘 Common Issues & Solutions

### Issue: "Cannot find module '@/components'"

**Solution:** Path aliases are configured in `vite.config.ts`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Verify `tsconfig.json` has the paths configured

### Issue: "API Connection Failed"

**Solution:**
1. Verify FastAPI backend is running: `curl http://localhost:8000/health`
2. Check `.env.local` has correct `VITE_API_BASE_URL`
3. Verify backend CORS settings allow `localhost:5173`
4. Check browser console for CORS errors

### Issue: "Vite Port Already in Use"

**Solution:**
```bash
# Find process using port 5173
lsof -i :5173

# Kill the process
kill -9 <PID>

# Or use different port
npm run dev -- --port 3000
```

### Issue: "Hot Reload Not Working"

**Solution:**
1. Restart development server: `Ctrl+C` and `npm run dev`
2. Clear browser cache: Ctrl+Shift+Delete
3. Check file permissions are correct

### Issue: "Build Size Too Large"

**Solution:**
- Analyze bundle: `npm run build -- --analyze`
- Check for unused dependencies: `npm ls`
- Consider code splitting for large pages

## 📞 Support

For additional help:

1. Check the main [README.md](./README.md)
2. Review component documentation in `src/components/`
3. Check TypeScript types in component interfaces
4. Run `npm run lint` to find potential issues

---

**Last Updated**: January 2025
**Created**: During Phase 2 - UI Implementation
