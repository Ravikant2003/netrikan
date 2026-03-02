import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * API Client for Netrikan Backend
 * Handles all communication with the FastAPI backend
 */
class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health')
    return response.data
  }

  /**
   * Analyze user location and context through all agents
   * @param payload Contains location, time, and contextual data
   */
  async analyze(payload: {
    latitude: number
    longitude: number
    time?: string
    user_id?: string
    [key: string]: any
  }) {
    const response = await this.client.post('/api/analyze', payload)
    return response.data
  }

  /**
   * Get optimal route based on location
   * @param payload Contains start/end coordinates and preferences
   */
  async getRoute(payload: {
    start_lat: number
    start_lng: number
    end_lat: number
    end_lng: number
    avoid_unsafe?: boolean
    [key: string]: any
  }) {
    const response = await this.client.post('/api/route', payload)
    return response.data
  }

  /**
   * Assess risk at current location
   * @param payload Contains location and time info
   */
  async assessRisk(payload: {
    latitude: number
    longitude: number
    time?: string
    [key: string]: any
  }) {
    const response = await this.client.post('/api/risk', payload)
    return response.data
  }

  /**
   * Handle emergency situation
   * @param payload Contains emergency details and user location
   */
  async reportEmergency(payload: {
    latitude: number
    longitude: number
    emergency_type: string
    description?: string
    user_id?: string
    [key: string]: any
  }) {
    const response = await this.client.post('/api/emergency', payload)
    return response.data
  }

  /**
   * Register or update user profile
   * @param payload Contains user information
   */
  async upsertUser(payload: {
    user_id: string
    phone?: string
    email?: string
    emergency_contacts?: Array<{ name: string; phone: string }>
    [key: string]: any
  }) {
    const response = await this.client.post('/api/users', payload)
    return response.data
  }

  /**
   * Retrieve user profile
   * @param userId User identifier
   */
  async getUser(userId: string) {
    const response = await this.client.get(`/api/users/${userId}`)
    return response.data
  }

  /**
   * Generic error handler
   */
  handleError(error: AxiosError) {
    if (error.response?.status === 404) {
      return 'Resource not found'
    }
    if (error.response?.status === 500) {
      return 'Server error. Please try again later.'
    }
    return error.message || 'An error occurred'
  }
}

export const apiClient = new ApiClient()
export default apiClient
