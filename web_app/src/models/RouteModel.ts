/**
 * Route Model - Mirrors mobile app structure
 */
export interface RouteModel {
  id: string
  start_lat: number
  start_lng: number
  end_lat: number
  end_lng: number
  distance: number
  duration: number
  safe_score: number
  alternative_routes: Array<{
    id: string
    distance: number
    duration: number
    safe_score: number
  }>
  warnings: string[]
  [key: string]: any
}
