const DEFAULT_API_BASE_URL = 'http://localhost:8000/api/v1'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL
).replace(/\/+$/, '')

export async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  const response = await fetch(
    `${API_BASE_URL}${normalizedPath}`,
    {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
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