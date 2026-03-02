/**
 * Theme Configuration with Glassmorphism
 * Dark and Light mode with detailed color palette
 */

export type ThemeMode = 'light' | 'dark'

interface ThemeColors {
  // Primary palette
  primary: string
  primaryLight: string
  primaryDark: string
  
  // Secondary palette
  secondary: string
  secondaryLight: string
  secondaryDark: string
  
  // Status colors
  success: string
  warning: string
  danger: string
  info: string
  
  // Backgrounds
  bgPrimary: string
  bgSecondary: string
  bgTertiary: string
  bgOverlay: string
  
  // Text colors
  textPrimary: string
  textSecondary: string
  textTertiary: string
  textInvert: string
  
  // Borders
  border: string
  borderLight: string
  borderDark: string
  
  // Glassmorphism specific
  glassLight: string
  glassDark: string
  glassLightBorder: string
  glassDarkBorder: string
}

interface ThemeShadows {
  xs: string
  sm: string
  md: string
  lg: string
  xl: string
  depth1: string
  depth2: string
  depth3: string
  glow: string
  glowDanger: string
  glowSuccess: string
}

export interface Theme {
  mode: ThemeMode
  colors: ThemeColors
  shadows: ThemeShadows
}

// Light mode theme
export const lightTheme: Theme = {
  mode: 'light',
  colors: {
    // Primary - Vibrant Purple
    primary: '#6c5ce7',
    primaryLight: '#a29bfe',
    primaryDark: '#5f3dc4',
    
    // Secondary - Fresh Green
    secondary: '#00b894',
    secondaryLight: '#55efc4',
    secondaryDark: '#00a86b',
    
    // Status colors
    success: '#00b894',
    warning: '#fdcb6e',
    danger: '#d63031',
    info: '#74b9ff',
    
    // Backgrounds
    bgPrimary: '#f8f9fa',
    bgSecondary: '#ffffff',
    bgTertiary: '#f1f3f5',
    bgOverlay: 'rgba(0, 0, 0, 0.6)',
    
    // Text colors
    textPrimary: '#2d3436',
    textSecondary: '#636e72',
    textTertiary: '#b2bec3',
    textInvert: '#ffffff',
    
    // Borders
    border: '#e9ecef',
    borderLight: '#f1f3f5',
    borderDark: '#dee2e6',
    
    // Glassmorphism
    glassLight: 'rgba(255, 255, 255, 0.7)',
    glassDark: 'rgba(255, 255, 255, 0.85)',
    glassLightBorder: 'rgba(255, 255, 255, 0.2)',
    glassDarkBorder: 'rgba(255, 255, 255, 0.3)',
  },
  shadows: {
    xs: '0 1px 2px rgba(0, 0, 0, 0.05)',
    sm: '0 2px 4px rgba(0, 0, 0, 0.08)',
    md: '0 4px 12px rgba(0, 0, 0, 0.12)',
    lg: '0 8px 24px rgba(0, 0, 0, 0.15)',
    xl: '0 16px 40px rgba(0, 0, 0, 0.2)',
    depth1: '0 4px 16px rgba(108, 92, 231, 0.1)',
    depth2: '0 8px 32px rgba(108, 92, 231, 0.15)',
    depth3: '0 16px 48px rgba(108, 92, 231, 0.2)',
    glow: '0 0 20px rgba(108, 92, 231, 0.3)',
    glowDanger: '0 0 20px rgba(214, 48, 49, 0.3)',
    glowSuccess: '0 0 20px rgba(0, 184, 148, 0.3)',
  },
}

// Dark mode theme
export const darkTheme: Theme = {
  mode: 'dark',
  colors: {
    // Primary - Vibrant Purple (brighter for dark mode)
    primary: '#a29bfe',
    primaryLight: '#dfe6e9',
    primaryDark: '#6c5ce7',
    
    // Secondary - Fresh Green
    secondary: '#55efc4',
    secondaryLight: '#81ecec',
    secondaryDark: '#00b894',
    
    // Status colors
    success: '#55efc4',
    warning: '#ffeaa7',
    danger: '#ff7675',
    info: '#74b9ff',
    
    // Backgrounds
    bgPrimary: '#0f0f23',
    bgSecondary: '#1a1a3a',
    bgTertiary: '#252550',
    bgOverlay: 'rgba(0, 0, 0, 0.8)',
    
    // Text colors
    textPrimary: '#ffffff',
    textSecondary: '#b2bec3',
    textTertiary: '#636e72',
    textInvert: '#0f0f23',
    
    // Borders
    border: '#2d3436',
    borderLight: '#404060',
    borderDark: '#1a1a3a',
    
    // Glassmorphism
    glassLight: 'rgba(26, 26, 58, 0.7)',
    glassDark: 'rgba(26, 26, 58, 0.85)',
    glassLightBorder: 'rgba(255, 255, 255, 0.1)',
    glassDarkBorder: 'rgba(255, 255, 255, 0.15)',
  },
  shadows: {
    xs: '0 1px 2px rgba(0, 0, 0, 0.3)',
    sm: '0 2px 4px rgba(0, 0, 0, 0.4)',
    md: '0 4px 12px rgba(0, 0, 0, 0.5)',
    lg: '0 8px 24px rgba(0, 0, 0, 0.6)',
    xl: '0 16px 40px rgba(0, 0, 0, 0.7)',
    depth1: '0 4px 16px rgba(108, 92, 231, 0.2)',
    depth2: '0 8px 32px rgba(108, 92, 231, 0.3)',
    depth3: '0 16px 48px rgba(108, 92, 231, 0.4)',
    glow: '0 0 20px rgba(162, 155, 254, 0.4)',
    glowDanger: '0 0 20px rgba(255, 118, 117, 0.4)',
    glowSuccess: '0 0 20px rgba(85, 239, 196, 0.4)',
  },
}

export const getTheme = (mode: ThemeMode): Theme => {
  return mode === 'light' ? lightTheme : darkTheme
}
