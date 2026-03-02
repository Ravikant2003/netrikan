import React, { useState } from 'react'
import { Header } from '@components/Header'
import { Card } from '@components/Card'
import { Button } from '@components/Button'
import { Badge } from '@components/Badge'
import styles from './SafetyScoreScreen.module.css'

interface SafetyData {
  overallScore: number
  location: string
  timestamp: string
  factors: {
    crimeRate: number
    lightingQuality: number
    pedestrianDensity: number
    nearbyServices: number
  }
  recommendation: string
  level: 'safe' | 'moderate' | 'unsafe'
}

export const SafetyScoreScreen: React.FC = () => {
  const [safetyData] = useState<SafetyData>({
    overallScore: 78,
    location: 'New Delhi, India',
    timestamp: new Date().toLocaleString(),
    factors: {
      crimeRate: 65,
      lightingQuality: 85,
      pedestrianDensity: 90,
      nearbyServices: 72,
    },
    recommendation:
      'This area is generally safe with good pedestrian activity. However, avoid traveling late at night and stay in well-lit areas.',
    level: 'moderate',
  })

  const [trips] = useState([
    {
      id: '1',
      date: 'Today',
      distance: 12.5,
      duration: 28,
      safetyScore: 92,
      status: 'completed',
    },
    {
      id: '2',
      date: 'Yesterday',
      distance: 8.3,
      duration: 18,
      safetyScore: 88,
      status: 'completed',
    },
    {
      id: '3',
      date: '2 days ago',
      distance: 15.2,
      duration: 35,
      safetyScore: 82,
      status: 'completed',
    },
  ])

  const getSafetyColor = (score: number) => {
    if (score >= 80) return 'success'
    if (score >= 60) return 'warning'
    return 'danger'
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'safe':
        return 'success'
      case 'moderate':
        return 'warning'
      case 'unsafe':
        return 'danger'
      default:
        return 'primary'
    }
  }

  return (
    <div className={styles.container}>
      <Header />

      <div className={styles.content}>
        {/* Current Safety Section */}
        <section className={styles['current-section']}>
          <div className={styles.container}>
            <h1>Current Safety Assessment</h1>

            <div className={styles['safety-card']}>
              <Card variant="elevated" className={styles['score-card']}>
                <div className={styles['score-display']}>
                  <div className={styles['score-circle']}>
                    <svg viewBox="0 0 100 100" className={styles['svg-circle']}>
                      <circle cx="50" cy="50" r="45" className={styles['bg-circle']} />
                      <circle cx="50" cy="50" r="45" className={styles['progress-circle']} />
                    </svg>
                    <div className={styles['score-text']}>
                      <span className={styles['score-number']}>{safetyData.overallScore}</span>
                      <span className={styles['score-label']}>Safety Score</span>
                    </div>
                  </div>

                  <div className={styles['score-info']}>
                    <h3>{safetyData.location}</h3>
                    <p className={styles['timestamp']}>{safetyData.timestamp}</p>
                    <Badge
                      variant={getLevelColor(safetyData.level) as any}
                      size="lg"
                    >
                      {safetyData.level.toUpperCase()}
                    </Badge>
                  </div>
                </div>

                <div className={styles['recommendation']}>
                  <p className={styles['rec-title']}>Recommendation:</p>
                  <p className={styles['rec-text']}>{safetyData.recommendation}</p>
                </div>
              </Card>
            </div>

            {/* Safety Factors */}
            <div className={styles['factors-grid']}>
              <Card variant="dark" className={styles['factor-card']}>
                <h4>🚨 Crime Rate</h4>
                <div className={styles['factor-bar']}>
                  <div
                    className={styles['factor-progress']}
                    style={{ width: `${safetyData.factors.crimeRate}%` }}
                  />
                </div>
                <div className={styles['factor-details']}>
                  <span>{safetyData.factors.crimeRate}% incidents</span>
                  <Badge variant="warning">Medium</Badge>
                </div>
              </Card>

              <Card variant="dark" className={styles['factor-card']}>
                <h4>💡 Lighting Quality</h4>
                <div className={styles['factor-bar']}>
                  <div
                    className={styles['factor-progress']}
                    style={{
                      width: `${safetyData.factors.lightingQuality}%`,
                      background: 'linear-gradient(90deg, #fdcb6e, #ffeb3b)',
                    }}
                  />
                </div>
                <div className={styles['factor-details']}>
                  <span>{safetyData.factors.lightingQuality}% well-lit</span>
                  <Badge variant="success">Good</Badge>
                </div>
              </Card>

              <Card variant="dark" className={styles['factor-card']}>
                <h4>👥 Pedestrian Density</h4>
                <div className={styles['factor-bar']}>
                  <div
                    className={styles['factor-progress']}
                    style={{
                      width: `${safetyData.factors.pedestrianDensity}%`,
                      background: 'linear-gradient(90deg, #55efc4, #00b894)',
                    }}
                  />
                </div>
                <div className={styles['factor-details']}>
                  <span>{safetyData.factors.pedestrianDensity}% crowded</span>
                  <Badge variant="success">Very Good</Badge>
                </div>
              </Card>

              <Card variant="dark" className={styles['factor-card']}>
                <h4>🏥 Nearby Services</h4>
                <div className={styles['factor-bar']}>
                  <div
                    className={styles['factor-progress']}
                    style={{
                      width: `${safetyData.factors.nearbyServices}%`,
                      background: 'linear-gradient(90deg, #74b9ff, #0984e3)',
                    }}
                  />
                </div>
                <div className={styles['factor-details']}>
                  <span>{safetyData.factors.nearbyServices}% coverage</span>
                  <Badge variant="success">Good</Badge>
                </div>
              </Card>
            </div>
          </div>
        </section>

        {/* Trip History */}
        <section className={styles['history-section']}>
          <div className={styles.container}>
            <h2>Recent Trips</h2>
            <div className={styles['trips-list']}>
              {trips.map((trip) => (
                <Card key={trip.id} variant="light" className={styles['trip-card']}>
                  <div className={styles['trip-header']}>
                    <div className={styles['trip-date']}>
                      <span className={styles['date-label']}>{trip.date}</span>
                    </div>
                    <Badge variant={getSafetyColor(trip.safetyScore) as any}>
                      {trip.safetyScore}%
                    </Badge>
                  </div>

                  <div className={styles['trip-details']}>
                    <div className={styles['detail']}>
                      <span className={styles['label']}>📍 Distance</span>
                      <span className={styles['value']}>{trip.distance} km</span>
                    </div>
                    <div className={styles['detail']}>
                      <span className={styles['label']}>⏱️ Duration</span>
                      <span className={styles['value']}>{trip.duration} min</span>
                    </div>
                    <div className={styles['detail']}>
                      <span className={styles['label']}>✓ Status</span>
                      <span className={styles['value']}>
                        {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
                      </span>
                    </div>
                  </div>

                  <Button variant="glass" size="sm" fullWidth>
                    View Details
                  </Button>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Insights */}
        <section className={styles['insights-section']}>
          <div className={styles.container}>
            <h2>Your Insights</h2>
            <div className={styles['insights-grid']}>
              <Card variant="dark" className={styles['insight-card']}>
                <h4>📊 Safety Trend</h4>
                <p>Your average safety score has improved by 5% this month.</p>
                <Badge variant="success">↑ Improving</Badge>
              </Card>

              <Card variant="dark" className={styles['insight-card']}>
                <h4>🎯 Best Time</h4>
                <p>You travel safest during morning hours (6-9 AM).</p>
                <Badge variant="primary">Morning</Badge>
              </Card>

              <Card variant="dark" className={styles['insight-card']}>
                <h4>🏆 Safe Zones</h4>
                <p>You have 3 favorite routes with excellent safety ratings.</p>
                <Badge variant="success">Verified</Badge>
              </Card>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export default SafetyScoreScreen
