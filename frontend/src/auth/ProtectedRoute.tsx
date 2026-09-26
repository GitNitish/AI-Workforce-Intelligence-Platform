import type { ReactNode } from 'react'
import {
  Navigate,
  useLocation,
} from 'react-router-dom'

import { useAuth } from './useAuth'

interface ProtectedRouteProps {
  children: ReactNode
  requiredPermission?: string
}

function ProtectedRoute({
  children,
  requiredPermission,
}: ProtectedRouteProps) {
  const {
    isAuthenticated,
    isLoading,
    hasPermission,
  } = useAuth()

  const location = useLocation()

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          background: '#f5f7fa',
          color: '#334155',
          fontFamily:
            'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        }}
      >
        Loading WorkForceIQ...
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
        }}
      />
    )
  }

  if (
    requiredPermission &&
    !hasPermission(requiredPermission)
  ) {
    return (
      <Navigate
        to="/"
        replace
        state={{
          accessDenied: true,
          from: location.pathname,
        }}
      />
    )
  }

  return <>{children}</>
}

export default ProtectedRoute