import React from 'react'
import { useTheme } from '@theme/ThemeContext'
import styles from './Header.module.css'

export const Header: React.FC = () => {
  const { toggleTheme, mode } = useTheme()

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        {/* Logo */}
        <div className={styles.logoSection}>
          <div className={styles.logoIcon}>
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#gradient)" />
              <path
                d="M10 16C10 13.239 12.239 11 15 11C17.761 11 20 13.239 20 16C20 18.761 17.761 21 15 21C12.239 21 10 18.761 10 16Z"
                fill="white"
              />
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                  <stop offset="0%" stopColor="#a29bfe" />
                  <stop offset="100%" stopColor="#6c5ce7" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className={styles.logoText}>
            <h2>Netrikan</h2>
            <p>Safe Travel Assistant</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className={styles.navigation}>
          <a href="/" className={styles.navLink}>
            Home
          </a>
          <a href="/route" className={styles.navLink}>
            Route
          </a>
          <a href="/safety" className={styles.navLink}>
            Safety
          </a>
          <a href="/tracking" className={styles.navLink}>
            Tracking
          </a>
        </nav>

        {/* Actions */}
        <div className={styles.actions}>
          <button
            className={`${styles.themeToggle} btn btn-glass btn-icon`}
            onClick={toggleTheme}
            title="Toggle dark/light mode"
          >
            {mode === 'light' ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="5" />
                <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m3.08 3.08l4.24 4.24M1 12h6m6 0h6m-15.78 7.78l4.24-4.24m3.08-3.08l4.24-4.24" />
              </svg>
            )}
          </button>

          <button className="btn btn-primary">Emergency</button>
        </div>
      </div>
    </header>
  )
}

export default Header
