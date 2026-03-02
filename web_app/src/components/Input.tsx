import React from 'react'
import styles from './Input.module.css'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: React.ReactNode
  fullWidth?: boolean
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  icon,
  fullWidth = true,
  className = '',
  ...props
}) => {
  return (
    <div className={`${styles['input-group']} ${fullWidth ? styles['full-width'] : ''}`}>
      {label && <label className={styles['input-label']}>{label}</label>}
      <div className={styles['input-wrapper']}>
        {icon && <span className={styles['input-icon']}>{icon}</span>}
        <input className={`${styles['input-field']} ${className}`} {...props} />
      </div>
      {error && <span className={styles['input-error']}>{error}</span>}
    </div>
  )
}

export default Input
