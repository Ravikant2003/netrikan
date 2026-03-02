# API Integration Documentation

Complete reference for integrating with the Netrikan FastAPI backend.

## Overview

The web app communicates with the FastAPI backend through the `apiClient` instance. All HTTP requests are made through Axios with proper error handling, timeouts, and response type safety.

## Backend Configuration

### Expected Backend URL

```
http://localhost:8000
```

### Configurable via Environment

Edit `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## API Client Setup

### Importing the API Client

```typescript
import { apiClient } from '@/services'

// Or use specific methods:
import { apiClient } from '@/services/apiClient'
```

### Basic Usage Pattern

```typescript
try {
  const response = await apiClient.methodName(data)
  // Handle success
  console.log(response)
} catch (error) {
  // Handle error
  console.error(error.message)
}
```

## Available Endpoints

### 1. Health Check

Check if the backend is operational.

**Method:** `healthCheck()`

```typescript
const status = await apiClient.healthCheck()

// Response:
// { status: 'ok' }
```

**Use Cases:**
- Verify backend connectivity on app startup
- Display offline mode when unavailable

**Example:**

```typescript
useEffect(() => {
  apiClient.healthCheck()
    .then(() => setBackendOnline(true))
    .catch(() => setBackendOnline(false))
}, [])
```

---

### 2. Analyze Full Route

Comprehensive route analysis using all agents.

**Method:** `analyze(data)`

```typescript
const analysis = await apiClient.analyze({
  start_location: 'Times Square, New York',
  end_location: 'Central Park, New York',
  travel_time: '22:00',
  transportation_mode: 'walking'
})

// Response structure:
// {
//   route_analysis: { ... },
//   safety_analysis: { ... },
//   risk_assessment: { ... },
//   emergency_contacts: [ ... ],
//   recommendations: [ ... ]
// }
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_location` | string | Yes | Starting location address or coordinates |
| `end_location` | string | Yes | Destination location address or coordinates |
| `travel_time` | string | No | Time of travel (HH:MM format) |
| `transportation_mode` | string | No | Mode of transport (walking, driving, public) |

**Use Cases:**
- Complete route planning with all safety metrics
- Initial app load to get comprehensive data

**Example:**

```typescript
function RouteAnalysis() {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const handleAnalyze = async (start, end) => {
    setLoading(true)
    try {
      const result = await apiClient.analyze({
        start_location: start,
        end_location: end,
        travel_time: new Date().toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      })
      setAnalysis(result)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div>
      {/* Render analysis results */}
    </div>
  )
}
```

---

### 3. Get Route Recommendations

Get optimized route options with safety metrics.

**Method:** `getRoute(data)`

```typescript
const routes = await apiClient.getRoute({
  start_location: 'Times Square',
  end_location: 'Central Park',
  include_alternatives: true
})

// Response structure:
// {
//   routes: [
//     {
//       id: 'route-1',
//       distance: 2.5,
//       duration: '45 mins',
//       safety_score: 8.5,
//       warnings: [],
//       polyline: '...'
//     },
//     ...
//   ]
// }
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_location` | string | Yes | Starting location |
| `end_location` | string | Yes | Destination |
| `include_alternatives` | boolean | No | Get alternative routes |

**Use Cases:**
- Display route options to user
- Show safety comparisons between routes
- Route selection in RouteMapScreen

**Example:**

```typescript
async function loadRoutes(start, end) {
  try {
    const response = await apiClient.getRoute({
      start_location: start,
      end_location: end,
      include_alternatives: true
    })
    
    setRoutes(response.routes)
    
    // Render routes with safety scores
    response.routes.forEach(route => {
      console.log(`Route: ${route.duration}, Safety: ${route.safety_score}/10`)
    })
  } catch (error) {
    console.error('Failed to load routes:', error)
    showError('Unable to load routes. Please try again.')
  }
}
```

---

### 4. Assess Risk Level

Evaluate safety risk for a specific location and time.

**Method:** `assessRisk(data)`

```typescript
const riskData = await apiClient.assessRisk({
  location: 'Central Park, New York',
  time: '22:00',
  day_of_week: 'Friday'
})

// Response structure:
// {
//   risk_level: 'low' | 'medium' | 'high',
//   risk_score: 3.5,
//   factors: {
//     crime_rate: { score: 2, trend: 'stable' },
//     lighting: { score: 4, recommendation: 'Avoid dark paths' },
//     pedestrian_density: { score: 5, status: 'moderate' },
//     nearby_services: { score: 3, available: ['police', 'hospital'] }
//   },
//   recommendations: [
//     'Avoid Park after sunset',
//     'Stay on main paths',
//     'Travel in groups'
//   ]
// }
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | Yes | Location to assess |
| `time` | string | No | Time of day (HH:MM) |
| `day_of_week` | string | No | Day of week (Monday, etc) |

**Use Cases:**
- Safety score display on routes
- Location-based warnings
- SafetyScoreScreen metrics

**Example:**

```typescript
async function displayLocationRisk(location) {
  try {
    const risk = await apiClient.assessRisk({
      location: location,
      time: getCurrentTime(),
      day_of_week: getCurrentDayOfWeek()
    })
    
    const safetyColor = getRiskColor(risk.risk_level)
    
    return (
      <SafetyCard
        riskLevel={risk.risk_level}
        score={risk.risk_score}
        factors={risk.factors}
        recommendations={risk.recommendations}
        color={safetyColor}
      />
    )
  } catch (error) {
    console.error('Risk assessment failed:', error)
  }
}
```

---

### 5. Report Emergency

Submit an emergency alert to the backend.

**Method:** `reportEmergency(data)`

```typescript
await apiClient.reportEmergency({
  type: 'assault',
  location: {
    lat: 40.7128,
    lng: -74.0060
  },
  user_id: 'user-123',
  timestamp: new Date().toISOString()
})

// Response:
// {
//   emergency_id: 'em-12345',
//   status: 'reported',
//   notifications_sent: 5,
//   assigned_responder: 'Officer Smith'
// }
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Type: 'accident', 'assault', 'theft', 'medical', 'harassment', 'other' |
| `location` | object | Yes | GPS coordinates `{ lat, lng }` |
| `user_id` | string | Yes | User reporting emergency |
| `timestamp` | string | No | ISO timestamp of incident |
| `description` | string | No | Emergency description |

**Use Cases:**
- Emergency SOS button activation
- Automatic emergency reporting with location
- Emergency screen integration

**Example:**

```typescript
async function triggerEmergency(type, location) {
  try {
    const response = await apiClient.reportEmergency({
      type: type,
      location: location,
      user_id: currentUser.id,
      timestamp: new Date().toISOString(),
      description: 'User activated SOS button'
    })
    
    showEmergencyAlert({
      title: 'Emergency Reported',
      message: `Responder: ${response.assigned_responder}`,
      id: response.emergency_id
    })
    
    notifyEmergencyContacts(currentUser.emergency_contacts)
  } catch (error) {
    console.error('Failed to report emergency:', error)
    showError('Unable to report emergency. Retrying...')
  }
}
```

---

### 6. Get User Profile

Retrieve user profile and preferences.

**Method:** `getUser(userId)`

```typescript
const user = await apiClient.getUser('user-123')

// Response structure:
// {
//   id: 'user-123',
//   name: 'John Doe',
//   email: 'john@example.com',
//   phone: '+1-555-0123',
//   emergency_contacts: [
//     {
//       id: 'contact-1',
//       name: 'Jane Doe',
//       phone: '+1-555-0124',
//       relationship: 'Spouse'
//     }
//   ],
//   preferences: {
//     safety_threshold: 7.0,
//     notifications_enabled: true,
//     location_sharing: false
//   },
//   created_at: '2024-01-01T00:00:00Z'
// }
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | string | Yes | Unique user identifier |

**Use Cases:**
- Load user profile on app startup
- Display emergency contacts
- Retrieve user preferences

**Example:**

```typescript
useEffect(() => {
  const userId = getCurrentUserId()
  
  apiClient.getUser(userId)
    .then(user => {
      setCurrentUser(user)
      setEmergencyContacts(user.emergency_contacts)
      applyUserPreferences(user.preferences)
    })
    .catch(error => {
      console.error('Failed to load user:', error)
      createDefaultUser()
    })
}, [])
```

---

### 7. Create/Update User Profile

Upsert user profile and settings.

**Method:** `upsertUser(data)`

```typescript
const updatedUser = await apiClient.upsertUser({
  id: 'user-123',
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+1-555-0123',
  emergency_contacts: [
    {
      id: 'contact-1',
      name: 'Jane Doe',
      phone: '+1-555-0124',
      relationship: 'Spouse'
    }
  ],
  preferences: {
    safety_threshold: 7.5,
    notifications_enabled: true,
    location_sharing: false
  }
})

// Response: Updated user object
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | User ID (create if new) |
| `name` | string | No | User's full name |
| `email` | string | No | User's email address |
| `phone` | string | No | User's phone number |
| `emergency_contacts` | array | No | Emergency contacts list |
| `preferences` | object | No | User preferences |

**Use Cases:**
- Save user profile during signup
- Update emergency contacts
- Change user preferences
- Sync location sharing settings

**Example:**

```typescript
async function updateUserProfile(updates) {
  try {
    const updated = await apiClient.upsertUser({
      id: currentUser.id,
      ...currentUser,
      ...updates
    })
    
    setCurrentUser(updated)
    showSuccess('Profile updated successfully')
  } catch (error) {
    console.error('Profile update failed:', error)
    showError('Failed to update profile. Please try again.')
  }
}

// Usage:
updateUserProfile({
  phone: '+1-555-9999',
  preferences: {
    notifications_enabled: true,
    location_sharing: true
  }
})
```

---

## Error Handling

### Error Structure

```typescript
interface ApiError {
  message: string
  status: number
  details?: any
}
```

### Handling Errors

```typescript
try {
  const result = await apiClient.analyze({...})
} catch (error) {
  if (error.response) {
    // Backend returned an error status (4xx, 5xx)
    console.error('Server error:', error.response.status)
    console.error('Message:', error.response.data.message)
  } else if (error.request) {
    // Request made but no response (network issue)
    console.error('Network error: No response from server')
  } else {
    // Error in request setup
    console.error('Error:', error.message)
  }
}
```

### Common Error Codes

| Status | Meaning | Handling |
|--------|---------|----------|
| 400 | Bad Request | Validate input parameters |
| 401 | Unauthorized | Show login screen |
| 403 | Forbidden | Show permission denied |
| 404 | Not Found | Check endpoint URL |
| 500 | Server Error | Show error message, retry later |
| 503 | Service Unavailable | Show offline mode |

---

## Timeout Configuration

Default timeout: **30 seconds**

To customize:

```typescript
// In src/services/apiClient.ts
apiClient.defaults.timeout = 60000 // 60 seconds
```

---

## Request/Response Examples

### Example 1: Route Planning Flow

```typescript
async function planRoute() {
  // Step 1: Analyze full route
  const analysis = await apiClient.analyze({
    start_location: 'Madison Square Garden',
    end_location: 'Brooklyn Bridge',
    travel_time: '21:30'
  })
  
  // Step 2: Get specific route options
  const routes = await apiClient.getRoute({
    start_location: 'Madison Square Garden',
    end_location: 'Brooklyn Bridge'
  })
  
  // Step 3: Assess risk for selected route
  const riskData = await apiClient.assessRisk({
    location: 'Brooklyn Bridge',
    time: '21:30',
    day_of_week: 'Friday'
  })
  
  return {
    analysis,
    routes: routes.routes,
    destinationRisk: riskData
  }
}
```

### Example 2: Emergency Response Flow

```typescript
async function handleEmergency(emergencyType, currentLocation) {
  try {
    // Report emergency immediately
    const response = await apiClient.reportEmergency({
      type: emergencyType,
      location: currentLocation,
      user_id: currentUser.id,
      timestamp: new Date().toISOString()
    })
    
    // Notify emergency contacts
    const userProfile = await apiClient.getUser(currentUser.id)
    
    for (const contact of userProfile.emergency_contacts) {
      sendNotification(contact, {
        message: `${currentUser.name} reported a ${emergencyType}`,
        location: currentLocation
      })
    }
    
    return response
  } catch (error) {
    // Fallback: call emergency services directly
    callEmergencyServices()
    throw error
  }
}
```

### Example 3: User Registration Flow

```typescript
async function registerNewUser(formData) {
  // Create user profile
  const user = await apiClient.upsertUser({
    name: formData.name,
    email: formData.email,
    phone: formData.phone,
    emergency_contacts: formData.emergencyContacts,
    preferences: {
      safety_threshold: 7.0,
      notifications_enabled: true,
      location_sharing: false
    }
  })
  
  // Verify backend is healthy
  await apiClient.healthCheck()
  
  // Load initial safety data
  const riskData = await apiClient.assessRisk({
    location: formData.currentLocation
  })
  
  return { user, riskData }
}
```

---

## Testing API Endpoints

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Analyze route
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Times Square",
    "end_location": "Central Park"
  }'

# Get route
curl -X POST http://localhost:8000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Times Square",
    "end_location": "Central Park"
  }'

# Assess risk
curl -X POST http://localhost:8000/api/risk \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Central Park"
  }'
```

### Testing in Browser Console

```typescript
// Import and test API client
import { apiClient } from '@/services'

// Test health check
apiClient.healthCheck()
  .then(r => console.log('✅ Backend online:', r))
  .catch(e => console.log('❌ Backend offline:', e.message))

// Test route analysis
apiClient.getRoute({
  start_location: 'Times Square',
  end_location: 'Central Park'
})
  .then(r => console.log('Routes:', r.routes))
  .catch(e => console.error('Error:', e))
```

---

## CORS Configuration

If you encounter CORS errors:

Ensure FastAPI backend has CORS middleware configured:

```python
# In backend main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Rate Limiting

No rate limiting is configured in the development client. For production, implement:

```typescript
// Add rate limiting middleware if needed
const createRateLimitedClient = () => {
  const lastRequests = new Map()
  
  return {
    async request(config) {
      const endpoint = config.url
      const now = Date.now()
      const lastRequest = lastRequests.get(endpoint) || 0
      
      if (now - lastRequest < 1000) { // 1 second minimum between requests
        await new Promise(resolve => 
          setTimeout(resolve, 1000 - (now - lastRequest))
        )
      }
      
      lastRequests.set(endpoint, Date.now())
      return config
    }
  }
}
```

---

## Caching Strategy

Consider implementing caching for expensive operations:

```typescript
const cache = new Map()
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

async function getCachedRoute(start, end) {
  const key = `route:${start}:${end}`
  const cached = cache.get(key)
  
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data
  }
  
  const data = await apiClient.getRoute({
    start_location: start,
    end_location: end
  })
  
  cache.set(key, { data, timestamp: Date.now() })
  return data
}
```

---

## Performance Monitoring

Track API performance in production:

```typescript
// Add response interceptor to monitor times
apiClient.interceptors.response.use(
  response => {
    const duration = Date.now() - response.config.startTime
    console.log(`${response.config.method.toUpperCase()} ${response.config.url}: ${duration}ms`)
    return response
  },
  error => Promise.reject(error)
)

apiClient.interceptors.request.use(
  config => {
    config.startTime = Date.now()
    return config
  }
)
```

---

## Version Reference

- **API Base**: `http://localhost:8000`
- **Web App**: `http://localhost:5173`
- **Proxy Path**: `/api` → backend root
- **Timeout**: 30 seconds (configurable)
- **Content-Type**: `application/json`

---

**Last Updated**: January 2025
**Status**: Production Ready
