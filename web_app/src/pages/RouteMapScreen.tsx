import React, { useState } from 'react'
import { Header } from '@components/Header'
import { Card } from '@components/Card'
import { Button } from '@components/Button'
import { Input } from '@components/Input'
import { Badge } from '@components/Badge'
import { Alert } from '@components/Alert'
import styles from './RouteMapScreen.module.css'

interface Route {
  id: string
  distance: number
  duration: number
  safetyScore: number
  crimeDensity: number
  traffic: 'light' | 'moderate' | 'heavy'
  warnings: string[]
}

export const RouteMapScreen: React.FC = () => {
  const [startLocation, setStartLocation] = useState('')
  const [endLocation, setEndLocation] = useState('')
  const [avoidUnsafe, setAvoidUnsafe] = useState(true)
  const [selectedRoute, setSelectedRoute] = useState<string | null>('route-1')
  const [isLoading, setIsLoading] = useState(false)

  const mockRoutes: Route[] = [
    {
      id: 'route-1',
      distance: 12.5,
      duration: 28,
      safetyScore: 92,
      crimeDensity: 2,
      traffic: 'light',
      warnings: []
    },
    {
      id: 'route-2',
      distance: 15.2,
      duration: 32,
      safetyScore: 88,
      crimeDensity: 5,
      traffic: 'moderate',
      warnings: ['Moderate crime density', 'Moderate traffic']
    },
    {
      id: 'route-3',
      distance: 18.0,
      duration: 42,
      safetyScore: 78,
      crimeDensity: 12,
      traffic: 'heavy',
      warnings: ['High crime density', 'Heavy traffic - Avoid if possible']
    }
  ]

  const handleSearch = () => {
    setIsLoading(true)
    setTimeout(() => setIsLoading(false), 1500)
  }

  const getTrafficColor = (traffic: string) => {
    switch (traffic) {
      case 'light':
        return 'success'
      case 'moderate':
        return 'warning'
      case 'heavy':
        return 'danger'
      default:
        return 'primary'
    }
  }

  return (
    <div className={styles.container}>
      <Header />

      <div className={styles.content}>
        {/* Search Panel */}
        <section className={styles['search-section']}>
          <div className={styles.container}>
            <Card variant="elevated" className={styles['search-card']}>
              <h2>Find Safe Route</h2>
              
              <div className={styles['search-form']}>
                <Input
                  label="Start Location"
                  placeholder="Enter starting point..."
                  value={startLocation}
                  onChange={(e) => setStartLocation(e.target.value)}
                  icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M12 1C6.48 1 2 5.48 2 11s4.48 10 10 10 10-4.48 10-10S17.52 1 12 1zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6z" />
                  </svg>}
                />

                <Input
                  label="End Location"
                  placeholder="Enter destination..."
                  value={endLocation}
                  onChange={(e) => setEndLocation(e.target.value)}
                  icon={<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                  </svg>}
                />

                <div className={styles['checkbox-group']}>
                  <input
                    type="checkbox"
                    id="avoid-unsafe"
                    checked={avoidUnsafe}
                    onChange={(e) => setAvoidUnsafe(e.target.checked)}
                  />
                  <label htmlFor="avoid-unsafe">Prioritize safety over distance</label>
                </div>

                <Button
                  variant="primary"
                  size="lg"
                  fullWidth
                  onClick={handleSearch}
                  isLoading={isLoading}
                >
                  Search Routes
                </Button>
              </div>
            </Card>
          </div>
        </section>

        <div className={styles['main-content']}>
          {/* Map Area */}
          <section className={styles['map-section']}>
            <Card variant="dark" className={styles['map-card']}>
              <div className={styles['map-container']}>
                {/* Placeholder for map */}
                <div className={styles['map-placeholder']}>
                  <svg width="100%" height="100%" viewBox="0 0 400 300" fill="none">
                    <rect width="400" height="300" fill="var(--color-bg-tertiary)" />
                    <circle cx="100" cy="100" r="4" fill="var(--color-success)" />
                    <circle cx="300" cy="200" r="4" fill="var(--color-danger)" />
                    <path d="M100 100 Q200 80 300 200" stroke="var(--color-primary)" strokeWidth="2" strokeDasharray="5,5" />
                    <text x="10" y="20" fill="var(--color-text-secondary)" fontSize="12">
                      Drag to pan • Scroll to zoom
                    </text>
                  </svg>
                </div>
                
                {/* Map Controls */}
                <div className={styles['map-controls']}>
                  <button className="btn btn-glass btn-icon small">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <line x1="12" y1="5" x2="12" y2="19" />
                      <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                  </button>
                  <button className="btn btn-glass btn-icon small">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                  </button>
                </div>
              </div>
            </Card>
          </section>

          {/* Routes List */}
          <section className={styles['routes-section']}>
            <h3>Available Routes</h3>
            <div className={styles['routes-list']}>
              {mockRoutes.map((route) => (
                <Card
                  key={route.id}
                  variant={selectedRoute === route.id ? 'elevated' : 'light'}
                  interactive
                  onClick={() => setSelectedRoute(route.id)}
                  className={`${styles['route-card']} ${
                    selectedRoute === route.id ? styles['selected'] : ''
                  }`}
                >
                  <div className={styles['route-header']}>
                    <div>
                      <h4>{route.distance} km</h4>
                      <p>{route.duration} min</p>
                    </div>
                    <Badge variant={route.safetyScore >= 90 ? 'success' : 'warning'}>
                      Safety: {route.safetyScore}%
                    </Badge>
                  </div>

                  <div className={styles['route-details']}>
                    <div className={styles['detail-item']}>
                      <span className={styles['label']}>Traffic</span>
                      <Badge variant={getTrafficColor(route.traffic) as any}>
                        {route.traffic.charAt(0).toUpperCase() + route.traffic.slice(1)}
                      </Badge>
                    </div>
                    <div className={styles['detail-item']}>
                      <span className={styles['label']}>Crime Density</span>
                      <span className={styles['value']}>{route.crimeDensity} incidents/km</span>
                    </div>
                  </div>

                  {route.warnings.length > 0 && (
                    <div className={styles['warnings']}>
                      {route.warnings.map((warning, idx) => (
                        <div key={idx} className={styles['warning-tag']}>
                          ⚠️ {warning}
                        </div>
                      ))}
                    </div>
                  )}

                  <Button
                    variant={selectedRoute === route.id ? 'primary' : 'glass'}
                    size="sm"
                    fullWidth
                  >
                    {selectedRoute === route.id ? 'Selected' : 'Select Route'}
                  </Button>
                </Card>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className={styles['action-bar']}>
        <div className={styles.container}>
          <div className={styles['action-content']}>
            <div className={styles['route-info']}>
              <h4>Route Selected</h4>
              <p>12.5 km • 28 min • Safety: 92%</p>
            </div>
            <div className={styles['action-buttons']}>
              <Button variant="secondary" size="lg">
                Share Route
              </Button>
              <Button variant="primary" size="lg">
                Navigate
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RouteMapScreen
