import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'

import type { CurrentUser } from '../types/auth'
import {
  clearStoredAccessToken,
  getStoredAccessToken,
} from '../services/api'
import {
  getCurrentUser,
  login as loginUser,
  logout as logoutUser,
} from '../services/auth'
import {
  AuthContext,
  type AuthContextValue,
} from './AuthContext'

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<CurrentUser | null>(null)

  const [isLoading, setIsLoading] =
    useState(true)

  useEffect(() => {
    const initializeAuthentication =
      async () => {
        const accessToken =
          getStoredAccessToken()

        if (!accessToken) {
          setIsLoading(false)
          return
        }

        try {
          const currentUser =
            await getCurrentUser()

          setUser(currentUser)
        } catch {
          clearStoredAccessToken()
          setUser(null)
        } finally {
          setIsLoading(false)
        }
      }

    void initializeAuthentication()
  }, [])

  const login = useCallback(
    async (
      username: string,
      password: string,
    ): Promise<void> => {
      const authenticatedUser =
        await loginUser(
          username,
          password,
        )

      setUser(authenticatedUser)
    },
    [],
  )

  const logout = useCallback((): void => {
    logoutUser()
    setUser(null)
  }, [])

  const hasPermission = useCallback(
    (permission: string): boolean => {
      return (
        user?.permissions.includes(
          permission,
        ) ?? false
      )
    },
    [user],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated:
        user !== null,
      isLoading,
      login,
      logout,
      hasPermission,
    }),
    [
      user,
      isLoading,
      login,
      logout,
      hasPermission,
    ],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}