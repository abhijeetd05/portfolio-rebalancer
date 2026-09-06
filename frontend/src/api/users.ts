import { getJson } from './client'

export interface UserProfile {
  user_id: string
  user_name: string
  age: number | null
  gender: string | null
  created_at: string
  updated_at: string
}

export function getCurrentUser(): Promise<UserProfile> {
  return getJson<UserProfile>('/api/users/me')
}
