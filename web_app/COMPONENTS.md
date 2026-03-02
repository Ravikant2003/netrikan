# Component API & Best Practices Guide

Complete reference for all reusable components and development best practices.

## Component Overview

The Netrikan Web App includes 7 core reusable components and 5 complete page screens.

### Import Path

All components are accessible via the convenient alias:

```typescript
import { Button, Card, Input, Badge, Alert, Modal, Header } from '@/components'
import { HomeScreen, RouteMapScreen, LiveTrackingScreen, EmergencyScreen, SafetyScoreScreen } from '@/pages'
```

---

## 🎯 Core Components

### 1. Header Component

Sticky navigation header with logo, navigation, and theme toggle.

**Location:** `src/components/Header.tsx`

**Props:**

```typescript
interface HeaderProps {
  // No required props - all content is built-in
}
```

**Features:**
- Logo with gradient text
- Navigation links (Home, Route, Emergency, Safety, Tracking)
- Theme toggle with light/dark mode
- Emergency SOS button
- Sticky positioning
- Mobile responsive (hamburger menu below 768px)

**Usage:**

```typescript
import { Header } from '@/components'

function App() {
  return (
    <>
      <Header />
      {/* Page content */}
    </>
  )
}
```

**Styling:**
- Uses CSS Modules: `Header.module.css`
- Glassmorphism effect with backdrop blur
- Responsive layout with media queries
- Smooth transitions on theme change

---

### 2. Button Component

Versatile button with multiple variants and sizes.

**Location:** `src/components/Button.tsx`

**Props:**

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'glass' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  children: React.ReactNode
}
```

**Variants:**
- **primary**: Main action buttons (purple gradient)
- **secondary**: Alternative actions (gray/muted)
- **glass**: Glassmorphism style (transparent with blur)
- **danger**: Destructive actions (red)
- **success**: Positive confirmations (green)

**Sizes:**
- **sm**: 32px height, smaller font
- **md**: 40px height, normal font (default)
- **lg**: 48px height, larger font

**Features:**
- Ripple effect on click
- Loading spinner when `isLoading={true}`
- Disabled state styling
- Hover animations
- Active press feedback

**Usage:**

```typescript
import { Button } from '@/components'

function MyComponent() {
  const [isLoading, setIsLoading] = useState(false)
  
  const handleClick = async () => {
    setIsLoading(true)
    await apiCall()
    setIsLoading(false)
  }
  
  return (
    <div>
      <Button variant="primary" size="md" onClick={handleClick}>
        Submit
      </Button>
      
      <Button variant="secondary" size="sm">
        Cancel
      </Button>
      
      <Button variant="glass" onClick={() => {}}>
        Glass Effect
      </Button>
      
      <Button variant="danger" isLoading={isLoading}>
        {isLoading ? 'Loading...' : 'Delete'}
      </Button>
      
      <Button variant="success" size="lg">
        Confirm
      </Button>
    </div>
  )
}
```

**Best Practices:**
- Always provide meaningful button text
- Use `variant="danger"` only for destructive actions
- Show loading state during async operations
- Disable button when form is invalid

---

### 3. Card Component

Container component with multiple visual styles.

**Location:** `src/components/Card.tsx`

**Props:**

```typescript
interface CardProps {
  variant?: 'light' | 'dark' | 'elevated' | 'danger' | 'success'
  interactive?: boolean
  className?: string
  children: React.ReactNode
}
```

**Variants:**
- **light**: Light background with subtle borders
- **dark**: Dark background with glassmorphism
- **elevated**: Floating effect with larger shadows
- **danger**: Red tinted with danger styling
- **success**: Green tinted with success styling

**Features:**
- Glassmorphism with backdrop blur
- Hover transform animation (when interactive)
- Color-coded variants
- Depth shadows
- Border transitions

**Usage:**

```typescript
import { Card } from '@/components'

function Dashboard() {
  return (
    <div>
      <Card variant="light">
        <h3>Light Card</h3>
        <p>Standard information card</p>
      </Card>
      
      <Card variant="elevated" interactive>
        <div style={{ cursor: 'pointer' }}>
          <h4>Interactive Card</h4>
          <p>Hovers with transform effect</p>
        </div>
      </Card>
      
      <Card variant="success">
        <h4>Success Alert</h4>
        <p>Operation completed successfully</p>
      </Card>
      
      <Card variant="danger">
        <h4>Error Alert</h4>
        <p>Something went wrong</p>
      </Card>
    </div>
  )
}
```

**Best Practices:**
- Use `interactive={true}` only for clickable cards
- Apply `variant="danger"` or `variant="success"` for status indicators
- Avoid nested cards (use sections instead)
- Keep card content concise

---

### 4. Input Component

Form input with labels, icons, and error handling.

**Location:** `src/components/Input.tsx`

**Props:**

```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  icon?: string // Icon class or identifier
  error?: string
  helperText?: string
}
```

**Features:**
- Optional label above input
- Icon support (left-aligned)
- Error message display
- Helper text below input
- Focus states with colored borders
- Hover background changes

**Supported Input Types:**
- `text`
- `email`
- `password`
- `number`
- `tel`
- `url`
- `search`
- `date`
- `time`

**Usage:**

```typescript
import { Input } from '@/components'
import { useState } from 'react'

function LoginForm() {
  const [email, setEmail] = useState('')
  const [emailError, setEmailError] = useState('')
  const [password, setPassword] = useState('')
  
  const handleEmailChange = (e) => {
    const value = e.target.value
    setEmail(value)
    
    if (!value.includes('@')) {
      setEmailError('Invalid email address')
    } else {
      setEmailError('')
    }
  }
  
  return (
    <form>
      <Input
        label="Email Address"
        type="email"
        placeholder="your@email.com"
        value={email}
        onChange={handleEmailChange}
        error={emailError}
        icon="mail"
      />
      
      <Input
        label="Password"
        type="password"
        placeholder="Enter your password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        icon="lock"
        helperText="Minimum 8 characters"
      />
      
      <Input
        label="Location"
        type="text"
        placeholder="Enter your location"
        icon="location"
      />
    </form>
  )
}
```

**Best Practices:**
- Always provide a `label` for accessibility
- Show `error` messages only after user interaction
- Use appropriate `type` attributes (email, password, tel, etc.)
- Provide `helperText` for requirements or hints
- Clear error state when input becomes valid

---

### 5. Badge Component

Small status indicator with visual variants.

**Location:** `src/components/Badge.tsx`

**Props:**

```typescript
interface BadgeProps {
  variant?: 'primary' | 'danger' | 'success' | 'warning' | 'info'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
}
```

**Variants:**
- **primary**: Purple/blue color
- **danger**: Red color
- **success**: Green color
- **warning**: Yellow color
- **info**: Blue color

**Sizes:**
- **sm**: 20px height, small text
- **md**: 24px height, normal text (default)
- **lg**: 32px height, larger text

**Features:**
- Pulsing animated dot
- Rounded pill shape
- Status indication
- Color-coded meanings

**Usage:**

```typescript
import { Badge } from '@/components'

function TrackingStatus() {
  return (
    <div>
      <Badge variant="success">Online</Badge>
      <Badge variant="danger">Offline</Badge>
      <Badge variant="warning" size="sm">Alert</Badge>
      <Badge variant="primary" size="lg">Featured</Badge>
      <Badge variant="info">Information</Badge>
    </div>
  )
}

function RiskIndicators() {
  return (
    <>
      <Badge variant="success">Low Risk</Badge>
      <Badge variant="warning">Medium Risk</Badge>
      <Badge variant="danger">High Risk</Badge>
    </>
  )
}
```

**Best Practices:**
- Use consistent variant meanings across the app
- Keep badge text short (1-2 words max)
- Pair badges with explanatory text
- Use for status, categories, or highlights

---

### 6. Alert Component

Notification message with optional close button.

**Location:** `src/components/Alert.tsx`

**Props:**

```typescript
interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  onClose?: () => void
  icon?: React.ReactNode
}
```

**Types:**
- **success**: Green border and icon
- **error**: Red border and icon
- **warning**: Yellow border and icon
- **info**: Blue border and icon

**Features:**
- Colored left border based on type
- Icon display
- Title and message content
- Optional close button
- Slide-in animation on mount
- Dismissible

**Usage:**

```typescript
import { Alert } from '@/components'
import { useState } from 'react'

function NotificationCenter() {
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: 'success',
      title: 'Route Updated',
      message: 'Your route has been optimized for safety'
    },
    {
      id: 2,
      type: 'warning',
      title: 'High Risk Area',
      message: 'The selected route includes areas with high crime rates'
    }
  ])
  
  const removeAlert = (id) => {
    setAlerts(alerts.filter(a => a.id !== id))
  }
  
  return (
    <div>
      {alerts.map(alert => (
        <Alert
          key={alert.id}
          type={alert.type}
          title={alert.title}
          message={alert.message}
          onClose={() => removeAlert(alert.id)}
        />
      ))}
    </div>
  )
}

// One-off alerts
function handleApiError(error) {
  return (
    <Alert
      type="error"
      title="Connection Failed"
      message={error.message}
    />
  )
}
```

**Best Practices:**
- Always provide a `message`
- Use appropriate `type` for the message content
- Show alerts at the top of the page
- Auto-dismiss alerts after 5-10 seconds for non-critical alerts
- Keep message concise and actionable

---

### 7. Modal Component

Dialog overlay for important actions or confirmations.

**Location:** `src/components/Modal.tsx`

**Props:**

```typescript
interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
}

interface ModalFooterProps {
  children: React.ReactNode
}
```

**Sizes:**
- **sm**: 400px max-width
- **md**: 600px max-width (default)
- **lg**: 800px max-width

**Features:**
- Dark backdrop that closes modal on click
- Scalized animation on open
- Fixed positioning
- Proper z-index stacking
- ESC key to close
- Header and footer sections

**Usage:**

```typescript
import { Modal, Button } from '@/components'
import { useState } from 'react'

function ConfirmDialog() {
  const [isOpen, setIsOpen] = useState(false)
  
  const handleConfirm = async () => {
    await apiCall()
    setIsOpen(false)
  }
  
  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        Open Dialog
      </Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Confirm Action"
        size="md"
      >
        <p>Are you sure you want to proceed?</p>
        <p>This action cannot be undone.</p>
        
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleConfirm}>
            Confirm Delete
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  )
}

function SettingsModal() {
  const [isOpen, setIsOpen] = useState(false)
  
  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      title="Edit Settings"
      size="lg"
    >
      <div>
        {/* Settings form content */}
      </div>
      
      <Modal.Footer>
        <Button onClick={() => setIsOpen(false)}>
          Close
        </Button>
        <Button variant="success">
          Save Changes
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
```

**Best Practices:**
- Use modals sparingly - prefer inline editing when possible
- Always provide a close button or ESC key support
- Keep modal content focused on one task
- Use appropriate `size` for content
- Show loading state during submission

---

## 📄 Page Components

### HomeScreen
Landing page with hero, stats, features, and CTA sections.
- **Location**: `src/pages/HomeScreen.tsx`
- **Features**: Animated hero, gradient text, stat cards, action cards

### RouteMapScreen
Route selection with search, map, and safety metrics.
- **Location**: `src/pages/RouteMapScreen.tsx`
- **Features**: Location search, interactive map, route list, action bar

### EmergencyScreen
SOS button and emergency response interface.
- **Location**: `src/pages/EmergencyScreen.tsx`
- **Features**: Massive SOS button, emergency types, contacts, tips

### SafetyScoreScreen
Safety metrics and analytics dashboard.
- **Location**: `src/pages/SafetyScoreScreen.tsx`
- **Features**: Circular score, factors, trip history, insights

### LiveTrackingScreen
Location sharing and real-time tracking.
- **Location**: `src/pages/LiveTrackingScreen.tsx`
- **Features**: Share controls, tracking grid, privacy settings

---

## 🎨 Theme System Usage

### Access Theme in Components

```typescript
import { useTheme } from '@/theme'

function MyComponent() {
  const { theme, toggleTheme } = useTheme()
  
  return (
    <>
      <p>Current theme: {theme}</p>
      <button onClick={toggleTheme}>Switch Theme</button>
    </>
  )
}
```

### Use CSS Variables

```css
/* Access theme colors in CSS */
.myElement {
  color: var(--color-text);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
}
```

---

## 🚀 Best Practices

### 1. Component Composition

Create complex UIs by composing simpler components:

```typescript
function RouteCard({ route }) {
  return (
    <Card variant="light" interactive>
      <div>
        <h4>{route.name}</h4>
        <p>Duration: {route.duration}</p>
        <Badge variant="success">{route.safetyScore}/10</Badge>
        <Button size="sm" variant="primary">
          Select
        </Button>
      </div>
    </Card>
  )
}
```

### 2. Props Validation

Use TypeScript interfaces for type safety:

```typescript
interface MyComponentProps {
  title: string
  count: number
  onAction?: (id: string) => void
  variant?: 'primary' | 'secondary'
}

export function MyComponent({
  title,
  count,
  onAction,
  variant = 'primary'
}: MyComponentProps) {
  // Component implementation
}
```

### 3. Accessibility

Include accessibility features:

```typescript
function SearchInput() {
  return (
    <Input
      label="Search location"
      type="search"
      placeholder="Enter address"
      aria-label="Search for locations"
      aria-describedby="search-help"
    />
  )
}
```

### 4. Responsive Design

Test components across breakpoints:

```typescript
// Mobile-first CSS
.container {
  display: grid;
  grid-template-columns: 1fr; // Mobile
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .container {
    grid-template-columns: repeat(2, 1fr); // Tablet
  }
}

@media (min-width: 1024px) {
  .container {
    grid-template-columns: repeat(3, 1fr); // Desktop
  }
}
```

### 5. State Management

Keep state close to where it's used:

```typescript
function ComponentWithState() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const handleAction = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      await apiCall()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div>
      {error && <Alert type="error" message={error} />}
      <Button onClick={handleAction} isLoading={isLoading}>
        Execute
      </Button>
    </div>
  )
}
```

### 6. Event Handling

Use appropriate event handlers:

```typescript
function FormComponent() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
  }
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Update state
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <Input onChange={handleChange} />
      <Button type="submit">Submit</Button>
    </form>
  )
}
```

### 7. Performance Optimization

```typescript
import { useCallback, useMemo } from 'react'

function OptimizedComponent({ items }) {
  // Memoize expensive computations
  const filtered = useMemo(
    () => items.filter(item => item.active),
    [items]
  )
  
  // Memoize callbacks
  const handleSelect = useCallback((id) => {
    console.log('Selected:', id)
  }, [])
  
  return filtered.map(item => (
    <Card key={item.id} onClick={() => handleSelect(item.id)}>
      {item.name}
    </Card>
  ))
}
```

---

## 📐 Common Patterns

### Loading State Pattern

```typescript
function DataDisplay() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    apiClient.getData()
      .then(result => {
        setData(result)
        setError(null)
      })
      .catch(err => setError(err.message))
      .finally(() => setIsLoading(false))
  }, [])
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <Alert type="error" message={error} />
  if (!data) return <div>No data available</div>
  
  return <Card>{/* Display data */}</Card>
}
```

### Form Pattern

```typescript
function MyForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error for this field
    setErrors(prev => ({ ...prev, [name]: '' }))
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    try {
      await apiCall(formData)
    } catch (err) {
      setErrors({ submit: err.message })
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <Input
        name="email"
        value={formData.email}
        onChange={handleChange}
        error={errors.email}
      />
      <Input
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
        error={errors.password}
      />
      {errors.submit && <Alert type="error" message={errors.submit} />}
      <Button type="submit" isLoading={isSubmitting}>
        Submit
      </Button>
    </form>
  )
}
```

---

## 🔍 Debugging Components

### React DevTools

1. Install [React DevTools Extension](https://react-devtools-tutorial.vercel.app/)
2. Inspect component props and state
3. Trace component renders

### Browser Console

```typescript
// Check component styles
const element = document.querySelector('.myComponent')
console.log(getComputedStyle(element))

// Check CSS variables
const root = document.documentElement
console.log(getComputedStyle(root).getPropertyValue('--color-primary'))
```

---

## 📚 Additional Resources

- [React Hooks Documentation](https://react.dev/reference/react)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [CSS Modules Guide](https://create-react-app.dev/docs/adding-a-css-modules-stylesheet)
- [Accessibility (WCAG 2.1)](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated**: January 2025
**Version**: 1.0.0
