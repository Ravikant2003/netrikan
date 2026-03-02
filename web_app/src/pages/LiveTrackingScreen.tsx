import React, { useState } from 'react'
import { Header } from '@components/Header'
import { Card } from '@components/Card'
import { Button } from '@components/Button'
import { Badge } from '@components/Badge'
import styles from './LiveTrackingScreen.module.css'

interface SharedLocation {
  id: string
  name: string
  relationship: string
  status: 'active' | 'inactive'
  location: string
  lastUpdate: string
  distance: number
}

interface SharedWith {
  id: string
  name: string
  relationship: string
  sharingStatus: 'active' | 'paused' | 'expired'
  sharedSince: string
  expiresIn: string
}

export const LiveTrackingScreen: React.FC = () => {
  const [isSharingLocation, setIsSharingLocation] = useState(true)
  const [sharingDuration, setSharingDuration] = useState('until-arrival')

  const [sharedLocations] = useState<SharedLocation[]>([
    {
      id: '1',
      name: 'Mom',
      relationship: 'Parent',
      status: 'active',
      location: 'New Delhi',
      lastUpdate: '2 minutes ago',
      distance: 15,
    },
    {
      id: '2',
      name: 'Best Friend',
      relationship: 'Friend',
      status: 'active',
      location: 'Same area',
      lastUpdate: '1 minute ago',
      distance: 0.5,
    },
    {
      id: '3',
      name: 'Brother',
      relationship: 'Family',
      status: 'inactive',
      location: 'Gurgaon',
      lastUpdate: '30 minutes ago',
      distance: 25,
    },
  ])

  const [sharedWith] = useState<SharedWith[]>([
    {
      id: '1',
      name: 'Mom',
      relationship: 'Parent',
      sharingStatus: 'active',
      sharedSince: 'Today',
      expiresIn: 'On arrival',
    },
    {
      id: '2',
      name: 'Best Friend',
      relationship: 'Friend',
      sharingStatus: 'active',
      sharedSince: 'Yesterday',
      expiresIn: '23 hours',
    },
    {
      id: '3',
      name: 'Partner',
      relationship: 'Significant Other',
      sharingStatus: 'paused',
      sharedSince: 'Last week',
      expiresIn: '5 days',
    },
  ])

  return (
    <div className={styles.container}>
      <Header />

      <div className={styles.content}>
        {/* Location Sharing Control */}
        <section className={styles['sharing-section']}>
          <div className={styles.container}>
            <Card variant="elevated" className={styles['control-card']}>
              <div className={styles['control-header']}>
                <div>
                  <h2>Location Sharing</h2>
                  <p className={styles['status-text']}>
                    {isSharingLocation
                      ? 'Your location is being shared'
                      : 'Location sharing is disabled'}
                  </p>
                </div>
                <Badge variant={isSharingLocation ? 'success' : 'warning'}>
                  {isSharingLocation ? 'ACTIVE' : 'INACTIVE'}
                </Badge>
              </div>

              <div className={styles['control-body']}>
                <div className={styles['toggle-group']}>
                  <label className={styles['toggle-label']}>
                    <input
                      type="checkbox"
                      checked={isSharingLocation}
                      onChange={(e) => setIsSharingLocation(e.target.checked)}
                      className={styles['toggle-input']}
                    />
                    <span className={styles['toggle-slider']} />
                    <span className={styles['toggle-text']}>
                      {isSharingLocation ? 'Sharing Enabled' : 'Sharing Disabled'}
                    </span>
                  </label>
                </div>

                {isSharingLocation && (
                  <div className={styles['duration-selector']}>
                    <label className={styles['label']}>Sharing Duration</label>
                    <select
                      value={sharingDuration}
                      onChange={(e) => setSharingDuration(e.target.value)}
                      className={styles['select']}
                    >
                      <option value="1-hour">1 Hour</option>
                      <option value="until-arrival">Until Arrival</option>
                      <option value="24-hours">24 Hours</option>
                      <option value="permanent">Permanent</option>
                    </select>
                  </div>
                )}
              </div>

              <Button variant="primary" size="lg" fullWidth>
                {isSharingLocation ? 'Stop Sharing' : 'Start Sharing'}
              </Button>
            </Card>
          </div>
        </section>

        <div className={styles['main-content']}>
          {/* Tracking Map Section */}
          <section className={styles['map-section']}>
            <div className={styles.container}>
              <Card variant="dark" className={styles['map-card']}>
                <h3>Live Map</h3>
                <div className={styles['map-container']}>
                  <svg width="100%" height="100%" viewBox="0 0 400 300" fill="none">
                    <rect width="400" height="300" fill="var(--color-bg-tertiary)" />
                    {/* Map placeholder */}
                    <circle cx="200" cy="150" r="8" fill="var(--color-primary)" />
                    <text x="10" y="20" fill="var(--color-text-secondary)" fontSize="12">
                      Your Location: Dragging to pan • Scroll to zoom
                    </text>
                  </svg>
                </div>
              </Card>
            </div>
          </section>

          {/* Shared Locations */}
          <section className={styles['locations-section']}>
            <div className={styles.container}>
              <h2>Can See My Location</h2>
              <div className={styles['locations-grid']}>
                {sharedWith.map((item) => (
                  <Card key={item.id} variant="light" className={styles['shared-card']}>
                    <div className={styles['card-header']}>
                      <div>
                        <h4>{item.name}</h4>
                        <p className={styles['relationship']}>{item.relationship}</p>
                      </div>
                      <Badge
                        variant={
                          item.sharingStatus === 'active'
                            ? 'success'
                            : item.sharingStatus === 'paused'
                              ? 'warning'
                              : 'primary'
                        }
                      >
                        {item.sharingStatus.toUpperCase()}
                      </Badge>
                    </div>

                    <div className={styles['card-details']}>
                      <div className={styles['detail']}>
                        <span className={styles['label']}>Shared Since</span>
                        <span className={styles['value']}>{item.sharedSince}</span>
                      </div>
                      <div className={styles['detail']}>
                        <span className={styles['label']}>Expires In</span>
                        <span className={styles['value']}>{item.expiresIn}</span>
                      </div>
                    </div>

                    <Button variant="glass" size="sm" fullWidth>
                      {item.sharingStatus === 'active' ? 'Pause' : 'Resume'}
                    </Button>
                  </Card>
                ))}
              </div>
            </div>
          </section>

          {/* Tracking Others */}
          <section className={styles['tracking-section']}>
            <div className={styles.container}>
              <h2>Tracking My Location</h2>
              <div className={styles['tracking-grid']}>
                {sharedLocations.map((item) => (
                  <Card
                    key={item.id}
                    variant={item.status === 'active' ? 'light' : 'dark'}
                    className={styles['tracking-card']}
                  >
                    <div className={styles['tracking-header']}>
                      <div>
                        <h4>{item.name}</h4>
                        <p className={styles['relationship']}>{item.relationship}</p>
                      </div>
                      <Badge variant={item.status === 'active' ? 'success' : 'warning'}>
                        {item.status === 'active' ? 'ONLINE' : 'OFFLINE'}
                      </Badge>
                    </div>

                    <div className={styles['tracking-details']}>
                      <div className={styles['detail']}>
                        <span className={styles['label']}>📍 Location</span>
                        <span className={styles['value']}>{item.location}</span>
                      </div>
                      <div className={styles['detail']}>
                        <span className={styles['label']}>⏱️ Last Update</span>
                        <span className={styles['value']}>{item.lastUpdate}</span>
                      </div>
                      <div className={styles['detail']}>
                        <span className={styles['label']}>📏 Distance</span>
                        <span className={styles['value']}>{item.distance} km away</span>
                      </div>
                    </div>

                    <Button variant="primary" size="sm" fullWidth>
                      View on Map
                    </Button>
                  </Card>
                ))}
              </div>
            </div>
          </section>

          {/* Settings & Privacy */}
          <section className={styles['privacy-section']}>
            <div className={styles.container}>
              <h2>Privacy & Settings</h2>
              <div className={styles['settings-grid']}>
                <Card variant="dark" className={styles['setting-card']}>
                  <h4>🔒 Privacy Controls</h4>
                  <p>Manage who can see your location and for how long.</p>
                  <Button variant="glass" size="sm" fullWidth>
                    Manage Access
                  </Button>
                </Card>

                <Card variant="dark" className={styles['setting-card']}>
                  <h4>📊 Activity Log</h4>
                  <p>View detailed activity history of all location shares.</p>
                  <Button variant="glass" size="sm" fullWidth>
                    View Log
                  </Button>
                </Card>

                <Card variant="dark" className={styles['setting-card']}>
                  <h4>⚙️ Preferences</h4>
                  <p>Configure location sharing preferences and defaults.</p>
                  <Button variant="glass" size="sm" fullWidth>
                    Settings
                  </Button>
                </Card>

                <Card variant="dark" className={styles['setting-card']}>
                  <h4>🛡️ Security</h4>
                  <p>View encryption details and security information.</p>
                  <Button variant="glass" size="sm" fullWidth>
                    View Details
                  </Button>
                </Card>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default LiveTrackingScreen
