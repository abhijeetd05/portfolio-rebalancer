import { postJson } from './client'

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface RegisterResponse {
  user_id: string
  user_name: string
}

export function login(user_name: string, password: string) {
  return postJson<AuthResponse>('/api/auth/login', { user_name, password })
}

export function register(user_name: string, password: string, age?: number, gender?: string) {
  return postJson<RegisterResponse>('/api/auth/register', { user_name, password, ...(age !== undefined ? { age } : {}), ...(gender ? { gender } : {}) })
}
