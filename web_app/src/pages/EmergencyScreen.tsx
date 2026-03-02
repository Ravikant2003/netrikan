import React, { useState } from 'react'
import { Header } from '@components/Header'
import { Card } from '@components/Card'
import { Button } from '@components/Button'
import { Badge } from '@components/Badge'
import { Alert } from '@components/Alert'
import styles from './EmergencyScreen.module.css'

interface EmergencyContact {
  id: string
  name: string
  phone: string
  relationship: string
  notified: boolean
}

export const EmergencyScreen: React.FC = () => {
  const [sosActive, setSosActive] = useState(false)
  const [emergencyType, setEmergencyType] = useState('other')
  const [contacts, setContacts] = useState<EmergencyContact[]>([
    {
      id: '1',
      name: 'Mom',
      phone: '+91 98765 43210',
      relationship: 'Parent',
      notified: false,
    },
    {
      id: '2',
      name: 'Best Friend',
      phone: '+91 87654 32109',
      relationship: 'Friend',
      notified: false,
    },
    {
      id: '3',
      name: 'Emergency Services',
      phone: '100',
      relationship: 'Authorities',
      notified: false,
    },
  ])

  const emergencyTypes = [
    { value: 'accident', label: 'Accident', icon: '🚗', color: 'warning' },
    { value: 'assault', label: 'Assault', icon: '🚨', color: 'danger' },
    { value: 'theft', label: 'Theft', icon: '💰', color: 'danger' },
    { value: 'medical', label: 'Medical', icon: '🏥', color: 'danger' },
    { value: 'harassment', label: 'Harassment', icon: '⚠️', color: 'warning' },
    { value: 'other', label: 'Other', icon: '❓', color: 'primary' },
  ]

  const handleSOS = () => {
    setSosActive(!sosActive)
    if (!sosActive) {
      // Mark contacts as notified
      setContacts(
        contacts.map((contact) => ({
          ...contact,
          notified: true,
        }))
      )
      // Trigger notification
      setTimeout(() => {
        setContacts(
          contacts.map((contact) => ({
            ...contact,
            notified: false,
          }))
        )
      }, 3000)
    }
  }

  return (
    <div className={styles.container}>
      <Header />

      <div className={styles.content}>
        {/* SOS Section */}
        <section className={styles['sos-section']}>
          <div className={styles.container}>
            <div className={styles['sos-card']}>
              <div className={styles['sos-header']}>
                <h1>Emergency SOS</h1>
                <Badge variant={sosActive ? 'danger' : 'success'}>
                  {sosActive ? 'ACTIVATED' : 'READY'}
                </Badge>
              </div>

              {sosActive && (
                <Alert
                  type="danger"
                  title="Emergency Alert Active"
                  message="Your emergency contacts have been notified of your location. Stay safe and await assistance."
                  icon={
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                    </svg>
                  }
                />
              )}

              <div className={styles['sos-button-container']}>
                <button
                  className={`${styles['sos-button']} ${sosActive ? styles['active'] : ''}`}
                  onClick={handleSOS}
                >
                  <span className={styles['sos-text']}>
                    {sosActive ? 'CANCEL SOS' : 'ACTIVATE SOS'}
                  </span>
                  <span className={styles['sos-icon']}>
                    {sosActive ? '✓' : '!'}
                  </span>
                </button>
                {sosActive && <div className={styles['pulse']} />}
              </div>

              <p className={styles['sos-info']}>
                {sosActive
                  ? 'Your live location is being shared with emergency contacts. Press again to cancel.'
                  : 'Hold for 3 seconds to activate emergency alert'}
              </p>
            </div>
          </div>
        </section>

        <div className={styles['main-content']}>
          {/* Emergency Type Selection */}
          <section className={styles['emergency-types']}>
            <div className={styles.container}>
              <h2>What's the emergency?</h2>
              <div className={styles['types-grid']}>
                {emergencyTypes.map((type) => (
                  <button
                    key={type.value}
                    className={`${styles['type-button']} ${
                      emergencyType === type.value ? styles['selected'] : ''
                    }`}
                    onClick={() => setEmergencyType(type.value)}
                  >
                    <span className={styles['type-icon']}>{type.icon}</span>
                    <span className={styles['type-label']}>{type.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </section>

          {/* Emergency Contacts */}
          <section className={styles['contacts-section']}>
            <div className={styles.container}>
              <h2>Emergency Contacts</h2>
              <div className={styles['contacts-grid']}>
                {contacts.map((contact) => (
                  <Card
                    key={contact.id}
                    variant={contact.notified ? 'success' : 'light'}
                    className={styles['contact-card']}
                  >
                    <div className={styles['contact-header']}>
                      <div>
                        <h4>{contact.name}</h4>
                        <p className={styles['relationship']}>{contact.relationship}</p>
                      </div>
                      {contact.notified && (
                        <Badge variant="success">Notified</Badge>
                      )}
                    </div>

                    <div className={styles['contact-phone']}>
                      <span className={styles['label']}>Phone</span>
                      <code>{contact.phone}</code>
                    </div>

                    <Button
                      variant={contact.notified ? 'success' : 'primary'}
                      size="sm"
                      fullWidth
                    >
                      {contact.notified ? 'Contacted ✓' : 'Quick Call'}
                    </Button>
                  </Card>
                ))}
              </div>
            </div>
          </section>

          {/* Safety Tips */}
          <section className={styles['tips-section']}>
            <div className={styles.container}>
              <h2>Safety Tips</h2>
              <div className={styles['tips-grid']}>
                <Card variant="dark" className={styles['tip-card']}>
                  <h4>📍 Stay Visible</h4>
                  <p>Stay in well-lit, populated areas. Avoid dark alleys and isolated locations.</p>
                </Card>

                <Card variant="dark" className={styles['tip-card']}>
                  <h4>📞 Stay Connected</h4>
                  <p>Keep your phone charged and location sharing active with trusted contacts.</p>
                </Card>

                <Card variant="dark" className={styles['tip-card']}>
                  <h4>🚗 Trust Your Instincts</h4>
                  <p>If something feels wrong, it probably is. Don't ignore your gut feeling.</p>
                </Card>

                <Card variant="dark" className={styles['tip-card']}>
                  <h4>🛑 Know Your Routes</h4>
                  <p>Always inform someone of your route and expected arrival time.</p>
                </Card>

                <Card variant="dark" className={styles['tip-card']}>
                  <h4>🎧 Stay Alert</h4>
                  <p>Avoid using headphones when walking alone, especially at night.</p>
                </Card>

                <Card variant="dark" className={styles['tip-card']}>
                  <h4>🤝 Travel in Groups</h4>
                  <p>When possible, travel with others. There's safety in numbers.</p>
                </Card>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default EmergencyScreen
