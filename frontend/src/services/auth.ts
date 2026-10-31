
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

async function readAuthenticationError(
  response: Response,
  fallbackMessage: string,
): Promise<Error> {
  try {
    const errorBody = (await response.json()) as {
      detail?: string
    }

    if (errorBody.detail) {
      return new Error(errorBody.detail)
    }
  } catch {
    // Keep the fallback authentication error.
  }

  return new Error(fallbackMessage)
}

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
    throw await readAuthenticationError(
      response,
      'Invalid username or password',
    )
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

export async function guestLogin(): Promise<CurrentUser> {
  const response = await fetch(
    `${API_BASE_URL}/auth/guest`,
    {
      method: 'POST',
    },
  )

  if (!response.ok) {
    throw await readAuthenticationError(
      response,
      'Unable to start Guest access.',
    )
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
