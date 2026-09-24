import {
  createContext,
} from 'react'

import type { CurrentUser } from '../types/auth'

export interface AuthContextValue {
  user: CurrentUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (
    username: string,
    password: string,
  ) => Promise<void>
  logout: () => void
  hasPermission: (permission: string) => boolean
}

export const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  )