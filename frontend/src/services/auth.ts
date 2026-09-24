import type {
  CurrentUser,
  LoginResponse,
} from '../types/auth'
import {
  API_BASE_URL,
  apiRequest,
  clearStoredAccessToken,
  setStoredAccessToken,
} from './api'

export async function login(
  username: string,
  password: string,
): Promise<CurrentUser> {
  const formData = new URLSearchParams()

  formData.set('username', username)
  formData.set('password', password)

  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    },
  )

  if (!response.ok) {
    let detail = 'Invalid username or password'

    try {
      const errorBody = (await response.json()) as {
        detail?: string
      }

      if (errorBody.detail) {
        detail = errorBody.detail
      }
    } catch {
      // Keep the default authentication error.
    }

    throw new Error(detail)
  }

  const tokenResponse =
    (await response.json()) as LoginResponse

  setStoredAccessToken(tokenResponse.access_token)

  try {
    return await getCurrentUser()
  } catch (error) {
    clearStoredAccessToken()
    throw error
  }
}

export async function getCurrentUser(): Promise<CurrentUser> {
  return apiRequest<CurrentUser>('/auth/me')
}

export function logout(): void {
  clearStoredAccessToken()
}