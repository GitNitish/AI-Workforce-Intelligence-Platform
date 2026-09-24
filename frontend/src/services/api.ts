const DEFAULT_API_BASE_URL = 'http://localhost:8000/api/v1'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL
).replace(/\/+$/, '')

export const AUTH_STORAGE_KEY = 'workforceiq_access_token'

export function getStoredAccessToken(): string | null {
  return localStorage.getItem(AUTH_STORAGE_KEY)
}

export function setStoredAccessToken(token: string): void {
  localStorage.setItem(AUTH_STORAGE_KEY, token)
}

export function clearStoredAccessToken(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

export async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  const headers = new Headers(options?.headers)

  const accessToken = getStoredAccessToken()

  if (accessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  if (
    !(options?.body instanceof URLSearchParams) &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(
    `${API_BASE_URL}${normalizedPath}`,
    {
      ...options,
      headers,
    },
  )

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`

    try {
      const errorBody = (await response.json()) as {
        detail?: string
      }

      if (errorBody.detail) {
        detail = errorBody.detail
      }
    } catch {
      // Keep the default HTTP error message when the response
      // does not contain a JSON error body.
    }

    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}