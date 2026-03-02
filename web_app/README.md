# Netrikan Web App

A modern, state-of-the-art web application for intelligent route optimization and personal safety built with React 18, TypeScript, and Vite.

## 🎨 Features

### Design System
- **Glassmorphism UI** - Modern frosted glass effects with backdrop blur
- **Dark & Light Modes** - Full theme support with system preference detection
- **3D Transforms** - Depth effects and perspective transforms on cards
- **Advanced Animations** - 12+ keyframe animations with smooth transitions
- **Responsive Design** - Fully responsive from 320px to 1400px+ screens

### Core Functionality
- **Smart Route Optimization** - AI-powered route analysis and safety scoring
- **Emergency Response** - SOS button with emergency contact management
- **Live Location Tracking** - Real-time location sharing with privacy controls
- **Safety Analytics** - Detailed safety metrics and crime area analysis
- **Risk Assessment** - Location-based risk evaluation

## 🛠️ Technology Stack

```
Frontend Framework:  React 18.2.0 + TypeScript 5.3.0
Build Tool:         Vite 5.0.0
HTTP Client:        Axios 1.6.0
Styling:            CSS Modules + Global CSS with CSS Variables
Routing:            React Router v6
Theme Management:   React Context API
```

## 📁 Project Structure

```
web_app/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Header.tsx
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Alert.tsx
│   │   ├── Modal.tsx
│   │   └── *.module.css   # Component-scoped styles
│   │
│   ├── pages/            # Screen components
│   │   ├── HomeScreen.tsx
│   │   ├── RouteMapScreen.tsx
│   │   ├── LiveTrackingScreen.tsx
│   │   ├── EmergencyScreen.tsx
│   │   ├── SafetyScoreScreen.tsx
│   │   └── *.module.css  # Page-scoped styles
│   │
│   ├── theme/           # Theme system
│   │   ├── theme.ts     # Color palettes, shadows, typography
│   │   └── ThemeContext.tsx  # Theme provider & hook
│   │
│   ├── styles/          # Global styles
│   │   ├── globals.css  # CSS variables, animations, base styles
│   │   └── components.css  # Reusable component patterns
│   │
│   ├── services/        # API & external services
│   │   └── apiClient.ts # Axios instance with backend endpoints
│   │
│   ├── models/          # TypeScript interfaces
│   │   ├── RouteModel.ts
│   │   ├── SafetyModel.ts
│   │   └── UserModel.ts
│   │
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Root component
│   └── main.tsx         # Entry point
│
├── package.json         # Dependencies and scripts
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
├── .env.local          # Environment variables (git-ignored)
├── index.html          # HTML template
└── README.md           # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm, yarn, or pnpm
- Backend running on `http://localhost:8000`

### Installation

```bash
# Navigate to web_app directory
cd web_app

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Update .env.local with your settings
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Netrikan
```

### Development Server

```bash
# Start development server (runs on http://localhost:5173)
npm run dev

# The app will auto-proxy API requests to http://localhost:8000
```

### Build for Production

```bash
# Create optimized build
npm run build

# Preview production build locally
npm run preview
```

## 🎨 Theme System

### Using the Theme Hook

```typescript
import { useTheme } from '@/theme'

export function MyComponent() {
  const { theme, toggleTheme } = useTheme()
  
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  )
}
```

### CSS Variables

Access theme variables in CSS:

```css
.myElement {
  color: var(--color-text);
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-md);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  transition: all var(--transition-base);
}
```

### Available CSS Variables

**Colors:**
- `--color-primary`, `--color-secondary`, `--color-danger`, `--color-success`, `--color-warning`
- `--color-text`, `--color-text-secondary`, `--color-text-tertiary`
- `--color-bg-primary`, `--color-bg-secondary`, `--color-bg-tertiary`
- `--color-border`, `--color-border-secondary`

**Shadows:**
- `--shadow-xs` through `--shadow-xl`
- `--shadow-depth-1`, `--shadow-depth-2`, `--shadow-depth-3`
- `--shadow-glow-primary`, `--shadow-glow-danger`, `--shadow-glow-success`

**Spacing:**
- `--spacing-xs` (4px) through `--spacing-3xl` (96px)

**Radius:**
- `--radius-sm` (4px) through `--radius-full` (9999px)

**Transitions:**
- `--transition-fast` (150ms)
- `--transition-base` (200ms)
- `--transition-slow` (300ms)

## 🧩 Component Library

### Button Component

```typescript
<Button 
  variant="primary"  // primary | secondary | glass | danger | success
  size="md"         // sm | md | lg
  onClick={() => {}}
  isLoading={false}
>
  Click me
</Button>
```

### Card Component

```typescript
<Card 
  variant="light"   // light | dark | elevated | danger | success
  interactive={true}
  className="custom"
>
  Content
</Card>
```

### Input Component

```typescript
<Input 
  label="Email"
  type="email"
  placeholder="user@example.com"
  icon="mail"
  error="Invalid email"
  onChange={handleChange}
/>
```

### Badge Component

```typescript
<Badge 
  variant="success"  // primary | danger | success | warning | info
  size="md"         // sm | md | lg
>
  Online
</Badge>
```

### Alert Component

```typescript
<Alert 
  type="success"    // success | error | warning | info
  title="Success!"
  message="Your changes have been saved"
  onClose={() => {}}
/>
```

### Modal Component

```typescript
<Modal 
  isOpen={true}
  size="md"        // sm | md | lg
  title="Confirm Action"
  onClose={() => {}}
>
  <p>Are you sure?</p>
  <Modal.Footer>
    <Button onClick={() => {}}>Cancel</Button>
    <Button variant="danger" onClick={() => {}}>Delete</Button>
  </Modal.Footer>
</Modal>
```

## 🔌 API Integration

The `apiClient` is pre-configured to connect with the FastAPI backend:

```typescript
import { apiClient } from '@/services'

// Get route recommendations
const routes = await apiClient.getRoute({
  start_location: 'Times Square',
  end_location: 'Central Park'
})

// Assess location risk
const riskData = await apiClient.assessRisk({
  location: 'Central Park',
  time: '22:00'
})

// Report emergency
await apiClient.reportEmergency({
  type: 'assault',
  location: { lat: 40.7128, lng: -74.0060 }
})

// Manage user profile
const user = await apiClient.getUser('user-id')
await apiClient.upsertUser({ id: 'user-id', name: 'John' })
```

## 🎯 Animations

Available keyframe animations in `globals.css`:

- `slideInUp` - Slide up with fade
- `slideInDown` - Slide down with fade
- `slideInLeft` - Slide left with fade
- `slideInRight` - Slide right with fade
- `fadeIn` - Simple fade animation
- `scaleIn` - Scale from 0.9 to 1
- `pulse` - Continuous pulse effect
- `float` - Floating animation
- `glow` - Glow shadow animation
- `shimmer` - Loading shimmer effect

Usage:
```css
.element {
  animation: slideInUp var(--transition-slow);
}
```

## 🎯 Glassmorphism Effects

Three glass effect utilities available:

```css
/* Light glass effect (20px blur) */
.glass-light {
  backdrop-filter: blur(20px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Medium glass effect (30px blur) */
.glass-medium {
  backdrop-filter: blur(30px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

/* Heavy glass effect (40px blur) */
.glass-dark {
  backdrop-filter: blur(40px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

## 📱 Responsive Breakpoints

- **Mobile**: < 480px (small screens)
- **Small**: 480px - 767px (tablets)
- **Tablet**: 768px - 1023px (landscape tablets)
- **Desktop**: 1024px - 1399px (desktop screens)
- **Large**: 1400px+ (large monitors)

All components use mobile-first CSS approach:

```css
/* Mobile styles (base) */
.element {
  font-size: 14px;
  grid-template-columns: 1fr;
}

/* Tablet and up */
@media (min-width: 768px) {
  .element {
    font-size: 16px;
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .element {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## 🔒 Environment Variables

Create `.env.local` in the web_app root:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Netrikan
```

## 📝 Development Workflow

### Component Creation

1. Create component file in `src/components/MyComponent.tsx`
2. Create styles in `src/components/MyComponent.module.css`
3. Export from `src/components/index.ts`

```typescript
// MyComponent.tsx
import styles from './MyComponent.module.css'

export interface MyComponentProps {
  title: string
  variant?: 'primary' | 'secondary'
}

export function MyComponent({ title, variant = 'primary' }: MyComponentProps) {
  return <div className={styles[variant]}>{title}</div>
}
```

### Page Creation

1. Create page in `src/pages/MyPage.tsx`
2. Create styles in `src/pages/MyPage.module.css`
3. Export from `src/pages/index.ts`
4. Add route in `App.tsx`

## 🧪 Testing

```bash
# Run unit tests
npm run test

# Run tests with coverage
npm run test:coverage
```

## 🚀 Deployment

### Build Optimization

```bash
# Create production build with code splitting
npm run build

# Analyze bundle size
npm run build -- --analyze
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Environment Configuration for Production

```env
VITE_API_BASE_URL=https://api.production.com
VITE_APP_NAME=Netrikan
```

## Backend Endpoints

The web app connects to the following backend endpoints:

### Health Check
- `GET /health` - Service health status

### Route Management
- `POST /api/route` - Calculate optimal route with safety metrics

### Risk Assessment
- `POST /api/risk` - Assess location risk level

### Emergency
- `POST /api/emergency` - Report emergency situation

### User Management
- `POST /api/users` - Create/update user profile
- `GET /api/users/{user_id}` - Retrieve user profile

### General Analysis
- `POST /api/analyze` - Run full analysis through all agents

## 🔗 Integration with Backend

The web app expects the FastAPI backend running at `http://localhost:8000` with the following endpoints:

### Required Backend Endpoints

- `POST /analyze` - Analyze route safety
- `GET /route` - Get route recommendations
- `POST /risk` - Assess location risk
- `POST /emergency` - Report emergency
- `GET /user/{user_id}` - Get user profile
- `POST /user` - Create/update user

See `src/services/apiClient.ts` for detailed endpoint specifications.

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [Vite Documentation](https://vitejs.dev)
- [CSS Variables Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)

## 🤝 Contributing

1. Follow the component structure guidelines
2. Use TypeScript for type safety
3. Maintain responsive design across all screen sizes
4. Test theme switching (dark/light modes)
5. Ensure accessibility (WCAG 2.1 AA)

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated**: January 2025
**Status**: Production Ready - Awaiting Backend Integration
│   ├── pages/           # Screen components (HomeScreen, RouteMapScreen, etc.)
│   ├── components/      # Reusable UI components
│   ├── services/        # API client and external services
│   ├── models/          # TypeScript interfaces for data models
│   ├── utils/           # Helper functions and constants
│   ├── App.tsx          # Main app with routing
│   ├── main.tsx         # React entry point
│   └── main.css         # Global styles
├── public/
│   └── index.html       # HTML entry point
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
├── package.json         # Dependencies and scripts
└── .env.local          # Environment variables
```

## Getting Started

### Prerequisites
- Node.js 18+
- Backend running on `http://localhost:8000`

### Installation

```bash
cd web_app
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Environment Variables

Create a `.env.local` file:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Netrikan
```

## API Client Usage

The `apiClient` service handles all backend communication:

```typescript
import apiClient from '@services/apiClient'

// Check backend health
const health = await apiClient.healthCheck()

// Get route
const route = await apiClient.getRoute({
  start_lat: 28.7041,
  start_lng: 77.1025,
  end_lat: 28.5355,
  end_lng: 77.3910,
  avoid_unsafe: true
})

// Report emergency
const emergency = await apiClient.reportEmergency({
  latitude: 28.7041,
  longitude: 77.1025,
  emergency_type: 'assault',
  description: 'Emergency at location'
})
```

## Pages/Screens

All page components are placeholders with proper structure for frontend implementation:

- **HomeScreen** - Main landing and navigation
- **RouteMapScreen** - Route display with safety overlays
- **LiveTrackingScreen** - Real-time location sharing
- **EmergencyScreen** - SOS functionality
- **SafetyScoreScreen** - Safety assessment display

## Next Steps

1. Implement component UI in each page
2. Add state management (Redux/Zustand)
3. Implement geolocation service
4. Add map integration (Google Maps/Leaflet)
5. Set up notifications
6. Add authentication
