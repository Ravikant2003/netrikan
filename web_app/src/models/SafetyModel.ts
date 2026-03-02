/**
 * Safety Model - Mirrors mobile app structure
 */
export interface SafetyModel {
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  risk_score: number
  factors: {
    crime_rate: number
    time_of_day: number
    weather: number
    traffic: number
  }
  recommendations: string[]
  nearby_safe_zones: Array<{
    name: string
    distance: number
    latitude: number
    longitude: number
  }>
  [key: string]: any
}
