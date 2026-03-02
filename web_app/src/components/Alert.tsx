import React from 'react'
import styles from './Alert.module.css'

interface AlertProps {
  type: 'danger' | 'success' | 'warning' | 'info'
  title?: string
  message: string
  icon?: React.ReactNode
  onClose?: () => void
}

export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  message,
  icon,
  onClose,
}) => {
  return (
    <div className={`${styles[`alert-${type}`]}`}>
      {icon && <div className={styles['alert-icon']}>{icon}</div>}
      <div className={styles['alert-content']}>
        {title && <div className={styles['alert-title']}>{title}</div>}
        <div className={styles['alert-message']}>{message}</div>
      </div>
      {onClose && (
        <button className={styles['alert-close']} onClick={onClose}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      )}
    </div>
  )
}

export default Alert
