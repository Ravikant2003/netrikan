import React, { createContext, useContext, useEffect, useState } from 'react'
import { Theme, ThemeMode, getTheme } from './theme'

interface ThemeContextType {
  theme: Theme
  mode: ThemeMode
  toggleTheme: () => void
  setTheme: (mode: ThemeMode) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: React.ReactNode
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    // Check localStorage
    const saved = localStorage.getItem('theme-mode')
    if (saved === 'light' || saved === 'dark') {
      return saved
    }
    
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  const theme = getTheme(mode)

  useEffect(() => {
    // Save to localStorage
    localStorage.setItem('theme-mode', mode)
    
    // Apply CSS variables
    const root = document.documentElement
    const colors = theme.colors
    const shadows = theme.shadows

    // Colors
    root.style.setProperty('--color-primary', colors.primary)
    root.style.setProperty('--color-primary-light', colors.primaryLight)
    root.style.setProperty('--color-primary-dark', colors.primaryDark)
    root.style.setProperty('--color-secondary', colors.secondary)
    root.style.setProperty('--color-secondary-light', colors.secondaryLight)
    root.style.setProperty('--color-secondary-dark', colors.secondaryDark)
    
    root.style.setProperty('--color-success', colors.success)
    root.style.setProperty('--color-warning', colors.warning)
    root.style.setProperty('--color-danger', colors.danger)
    root.style.setProperty('--color-info', colors.info)
    
    root.style.setProperty('--color-bg-primary', colors.bgPrimary)
    root.style.setProperty('--color-bg-secondary', colors.bgSecondary)
    root.style.setProperty('--color-bg-tertiary', colors.bgTertiary)
    root.style.setProperty('--color-bg-overlay', colors.bgOverlay)
    
    root.style.setProperty('--color-text-primary', colors.textPrimary)
    root.style.setProperty('--color-text-secondary', colors.textSecondary)
    root.style.setProperty('--color-text-tertiary', colors.textTertiary)
    root.style.setProperty('--color-text-invert', colors.textInvert)
    
    root.style.setProperty('--color-border', colors.border)
    root.style.setProperty('--color-border-light', colors.borderLight)
    root.style.setProperty('--color-border-dark', colors.borderDark)
    
    root.style.setProperty('--glass-light', colors.glassLight)
    root.style.setProperty('--glass-dark', colors.glassDark)
    root.style.setProperty('--glass-light-border', colors.glassLightBorder)
    root.style.setProperty('--glass-dark-border', colors.glassDarkBorder)

    // Shadows
    root.style.setProperty('--shadow-xs', shadows.xs)
    root.style.setProperty('--shadow-sm', shadows.sm)
    root.style.setProperty('--shadow-md', shadows.md)
    root.style.setProperty('--shadow-lg', shadows.lg)
    root.style.setProperty('--shadow-xl', shadows.xl)
    root.style.setProperty('--shadow-depth-1', shadows.depth1)
    root.style.setProperty('--shadow-depth-2', shadows.depth2)
    root.style.setProperty('--shadow-depth-3', shadows.depth3)
    root.style.setProperty('--shadow-glow', shadows.glow)
    root.style.setProperty('--shadow-glow-danger', shadows.glowDanger)
    root.style.setProperty('--shadow-glow-success', shadows.glowSuccess)

    // Update data attribute for CSS selectors
    document.documentElement.setAttribute('data-theme', mode)
  }, [mode, theme])

  const toggleTheme = () => {
    setMode(prev => (prev === 'light' ? 'dark' : 'light'))
  }

  const value: ThemeContextType = {
    theme,
    mode,
    toggleTheme,
    setTheme: setMode,
  }

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
