import React from 'react'
import styles from './Card.module.css'

interface CardProps {
  children: React.ReactNode
  variant?: 'light' | 'dark' | 'elevated' | 'danger' | 'success'
  className?: string
  onClick?: () => void
  interactive?: boolean
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'light',
  className = '',
  onClick,
  interactive = false,
}) => {
  return (
    <div
      className={`${styles[`card-${variant}`]} ${interactive ? styles['card-interactive'] : ''} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export default Card
