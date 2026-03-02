import React from 'react'
import styles from './Modal.module.css'

interface ModalProps {
  isOpen: boolean
  title: string
  children: React.ReactNode
  onClose: () => void
  actions?: {
    primary?: { label: string; onClick: () => void }
    secondary?: { label: string; onClick: () => void }
  }
  size?: 'sm' | 'md' | 'lg'
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  title,
  children,
  onClose,
  actions,
  size = 'md',
}) => {
  if (!isOpen) return null

  return (
    <>
      <div className={styles.backdrop} onClick={onClose} />
      <div className={`${styles.modal} ${styles[`modal-${size}`]}`}>
        <div className={styles.header}>
          <h3>{title}</h3>
          <button className={styles.close} onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div className={styles.body}>{children}</div>

        {actions && (
          <div className={styles.footer}>
            {actions.secondary && (
              <button
                className="btn btn-glass"
                onClick={actions.secondary.onClick}
              >
                {actions.secondary.label}
              </button>
            )}
            {actions.primary && (
              <button
                className="btn btn-primary"
                onClick={actions.primary.onClick}
              >
                {actions.primary.label}
              </button>
            )}
          </div>
        )}
      </div>
    </>
  )
}

export default Modal
