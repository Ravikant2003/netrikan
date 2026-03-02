/**
 * User Model - Mirrors mobile app structure
 */
export interface EmergencyContact {
  name: string
  phone: string
  email?: string
  relationship?: string
}

export interface UserModel {
  user_id: string
  phone?: string
  email?: string
  name?: string
  emergency_contacts: EmergencyContact[]
  location_sharing_enabled: boolean
  notification_preferences: {
    push_enabled: boolean
    sms_enabled: boolean
    email_enabled: boolean
  }
  [key: string]: any
}
