import React, { useState } from 'react'
import { Header } from '@components/Header'
import { Card } from '@components/Card'
import { Button } from '@components/Button'
import { Badge } from '@components/Badge'
import styles from './HomeScreen.module.css'

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string | number
  subtitle?: string
  color?: 'primary' | 'success' | 'warning' | 'danger'
}

const StatCard: React.FC<StatCardProps> = ({ icon, label, value, subtitle, color = 'primary' }) => (
  <Card variant="elevated" className={styles['stat-card']}>
    <div className={styles['stat-icon']} data-color={color}>
      {icon}
    </div>
    <div className={styles['stat-content']}>
      <p className={styles['stat-label']}>{label}</p>
      <h3 className={styles['stat-value']}>{value}</h3>
      {subtitle && <p className={styles['stat-subtitle']}>{subtitle}</p>}
    </div>
  </Card>
)

interface QuickActionProps {
  icon: React.ReactNode
  label: string
  description: string
  onClick: () => void
  color: 'primary' | 'secondary' | 'danger' | 'success'
}

const QuickAction: React.FC<QuickActionProps> = ({
  icon,
  label,
  description,
  onClick,
  color,
}) => (
  <button
    className={`${styles['action-card']} ${styles[`action-${color}`]}`}
    onClick={onClick}
  >
    <div className={styles['action-icon']}>{icon}</div>
    <h4>{label}</h4>
    <p>{description}</p>
  </button>
)

export const HomeScreen: React.FC = () => {
  const [selectedAction, setSelectedAction] = useState<string | null>(null)

  return (
    <div className={styles.container}>
      <Header />

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles['hero-content']}>
          <h1 className={styles['hero-title']}>
            Your <span className={styles.gradient}>Safe Travel</span> Companion
          </h1>
          <p className={styles['hero-subtitle']}>
            AI-powered route optimization, real-time safety assessment, and emergency response at your fingertips
          </p>
          <div className={styles['hero-actions']}>
            <Button variant="primary" size="lg">
              Get Started
            </Button>
            <Button variant="glass" size="lg">
              Learn More
            </Button>
          </div>
        </div>

        {/* Animated Background Elements */}
        <div className={styles['hero-bg']}>
          <div className={styles['blob']} />
          <div className={styles['blob']} style={{ animationDelay: '-2s' }} />
          <div className={styles['blob']} style={{ animationDelay: '-4s' }} />
        </div>
      </section>

      {/* Stats Section */}
      <section className={styles.stats}>
        <div className={styles.container}>
          <h2>Safety in Numbers</h2>
          <div className={styles['stats-grid']}>
            <StatCard
              icon={
                <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
              }
              label="Routes Analyzed"
              value="50K+"
              subtitle="This week"
              color="success"
            />
            <StatCard
              icon={
                <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                </svg>
              }
              label="Users Protected"
              value="100K+"
              subtitle="Globally"
              color="primary"
            />
            <StatCard
              icon={
                <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
                </svg>
              }
              label="Avg. Safety Score"
              value="94%"
              subtitle="User reported"
              color="success"
            />
            <StatCard
              icon={
                <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.99 5V1h-1v4H7.97v2h2.99v3.61H9.92v2h2.07V13h3v-2h2.07v-2h-2.07V7h2.99V5h-3.02V1h-1v4h-2.98zm.01 6.47v3.61h2.07v-3.61h-2.07z" />
                </svg>
              }
              label="Response Time"
              value="<2s"
              subtitle="Average"
              color="warning"
            />
          </div>
        </div>
      </section>

      {/* Quick Actions Section */}
      <section className={styles['quick-actions']}>
        <div className={styles.container}>
          <h2>Quick Actions</h2>
          <div className={styles['actions-grid']}>
            <QuickAction
              icon={
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              }
              label="Find Safe Route"
              description="Get optimized routes with safety scoring"
              onClick={() => setSelectedAction('route')}
              color="primary"
            />

            <QuickAction
              icon={
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              }
              label="Live Tracking"
              description="Share your location with trusted contacts"
              onClick={() => setSelectedAction('tracking')}
              color="secondary"
            />

            <QuickAction
              icon={
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="1" />
                  <path d="M12 1v6m0 6v6m6-6h6m-6-6h4m-12 0h4m6 0h6" />
                </svg>
              }
              label="Safety Check"
              description="Assess safety of current location"
              onClick={() => setSelectedAction('safety')}
              color="success"
            />

            <QuickAction
              icon={
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="9" />
                  <line x1="12" y1="8" x2="12" y2="16" />
                  <line x1="8" y1="12" x2="16" y2="12" />
                </svg>
              }
              label="Emergency SOS"
              description="Activate emergency alert"
              onClick={() => setSelectedAction('emergency')}
              color="danger"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className={styles.features}>
        <div className={styles.container}>
          <h2>Powerful Features</h2>
          <div className={styles['features-grid']}>
            <Card variant="dark" className={styles['feature-card']}>
              <div className={styles['feature-icon']}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                </svg>
              </div>
              <h4>AI-Powered Routing</h4>
              <p>Machine learning algorithms analyze crime data, traffic patterns, and weather for optimal routes.</p>
              <Badge variant="primary">Real-time</Badge>
            </Card>

            <Card variant="dark" className={styles['feature-card']}>
              <div className={styles['feature-icon']}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
                </svg>
              </div>
              <h4>Real-Time Alerts</h4>
              <p>Get instant notifications about safety risks and emergency situations in your area.</p>
              <Badge variant="danger">Critical</Badge>
            </Card>

            <Card variant="dark" className={styles['feature-card']}>
              <div className={styles['feature-icon']}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1C6.48 1 2 5.48 2 11s4.48 10 10 10 10-4.48 10-10S17.52 1 12 1zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6z" />
                </svg>
              </div>
              <h4>Emergency Response</h4>
              <p>One-tap SOS to alert emergency contacts and authorities immediately.</p>
              <Badge variant="success">Fast</Badge>
            </Card>

            <Card variant="dark" className={styles['feature-card']}>
              <div className={styles['feature-icon']}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                </svg>
              </div>
              <h4>Location Sharing</h4>
              <p>Share your live location with trusted contacts for added safety and peace of mind.</p>
              <Badge variant="primary">Private</Badge>
            </Card>

            <Card variant="dark" className={styles['feature-card']}>
              <div className={styles['feature-icon']}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
              </div>
              <h4>Safety Analytics</h4>
              <p>Detailed insights and reports about your travel patterns and safety metrics.</p>
              <Badge variant="success">Secure</Badge>
            </Card>

            <Card variant="dark" className={styles['feature-card']}>
              <div className={styles['feature-icon']}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
                </svg>
              </div>
              <h4>Privacy First</h4>
              <p>Your data is encrypted and never shared without explicit consent.</p>
              <Badge variant="success">E2E Encrypted</Badge>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.cta}>
        <div className={styles.container}>
          <Card variant="elevated" className={styles['cta-card']}>
            <h2>Ready to Travel Safer?</h2>
            <p>Join thousands of users who trust Netrikan for their daily safety needs.</p>
            <Button variant="primary" size="lg">
              Start Your Journey
            </Button>
          </Card>
        </div>
      </section>
    </div>
  )
}

export default HomeScreen
