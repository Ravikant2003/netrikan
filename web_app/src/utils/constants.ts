/**
 * Constants utility
 * Mirrors mobile app constants
 */

export const API_ENDPOINTS = {
  HEALTH: '/health',
  ANALYZE: '/api/analyze',
  ROUTE: '/api/route',
  RISK: '/api/risk',
  EMERGENCY: '/api/emergency',
  USERS: '/api/users',
}

export const RISK_LEVELS = {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL',
}

export const EMERGENCY_TYPES = {
  ACCIDENT: 'accident',
  ASSAULT: 'assault',
  THEFT: 'theft',
  OTHER: 'other',
}

export const APP_CONFIG = {
  APP_NAME: import.meta.env.VITE_APP_NAME || 'Netrikan',
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  LOCATION_UPDATE_INTERVAL: 5000, // 5 seconds
  RISK_CHECK_INTERVAL: 10000, // 10 seconds
}
