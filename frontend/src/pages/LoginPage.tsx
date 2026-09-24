import {
  useState,
} from 'react'
import type {
  FormEvent,
} from 'react'
import {
  Navigate,
  useLocation,
} from 'react-router-dom'

import { useAuth } from '../auth/useAuth'

interface LoginLocationState {
  from?: string
}

function LoginPage() {
  const {
    isAuthenticated,
    isLoading,
    login,
  } = useAuth()

  const location = useLocation()

  const [username, setUsername] =
    useState('')

  const [password, setPassword] =
    useState('')

  const [error, setError] =
    useState('')

  const [isSubmitting, setIsSubmitting] =
    useState(false)

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

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const locationState =
    location.state as LoginLocationState | null

  const destination =
    locationState?.from ?? '/'

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    setError('')
    setIsSubmitting(true)

    try {
      await login(
        username.trim(),
        password,
      )

      window.history.replaceState(
        null,
        '',
        destination,
      )

      window.location.assign(destination)
    } catch (loginError) {
      setError(
        loginError instanceof Error
          ? loginError.message
          : 'Unable to sign in',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        padding: '32px',
        background:
          'linear-gradient(135deg, #eef2f7 0%, #f8fafc 55%, #e8eef6 100%)',
        fontFamily:
          'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      <section
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '36px',
          borderRadius: '18px',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          boxShadow:
            '0 18px 45px rgba(15, 23, 42, 0.10)',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '28px',
          }}
        >
          <div
            style={{
              width: '42px',
              height: '42px',
              display: 'grid',
              placeItems: 'center',
              borderRadius: '11px',
              background: '#172554',
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '20px',
            }}
          >
            W
          </div>

          <div>
            <div
              style={{
                fontSize: '18px',
                fontWeight: 700,
                color: '#0f172a',
              }}
            >
              WorkForceIQ
            </div>

            <div
              style={{
                marginTop: '2px',
                fontSize: '12px',
                color: '#64748b',
              }}
            >
              Workforce Intelligence
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <h1
            style={{
              margin: 0,
              fontSize: '26px',
              color: '#0f172a',
            }}
          >
            Sign in
          </h1>

          <p
            style={{
              margin: '8px 0 0',
              fontSize: '14px',
              lineHeight: 1.5,
              color: '#64748b',
            }}
          >
            Sign in to access your workforce
            workspace.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <label
            style={{
              display: 'block',
              marginBottom: '7px',
              fontSize: '13px',
              fontWeight: 600,
              color: '#334155',
            }}
            htmlFor="username"
          >
            Username
          </label>

          <input
            id="username"
            type="text"
            value={username}
            onChange={(event) =>
              setUsername(event.target.value)
            }
            autoComplete="username"
            required
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '11px 12px',
              marginBottom: '18px',
              border: '1px solid #cbd5e1',
              borderRadius: '9px',
              fontSize: '14px',
              outline: 'none',
            }}
          />

          <label
            style={{
              display: 'block',
              marginBottom: '7px',
              fontSize: '13px',
              fontWeight: 600,
              color: '#334155',
            }}
            htmlFor="password"
          >
            Password
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            autoComplete="current-password"
            required
            style={{
              width: '100%',
              boxSizing: 'border-box',
              padding: '11px 12px',
              marginBottom: '18px',
              border: '1px solid #cbd5e1',
              borderRadius: '9px',
              fontSize: '14px',
              outline: 'none',
            }}
          />

          {error && (
            <div
              role="alert"
              style={{
                marginBottom: '16px',
                padding: '10px 12px',
                borderRadius: '8px',
                background: '#fef2f2',
                border:
                  '1px solid #fecaca',
                color: '#b91c1c',
                fontSize: '13px',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={
              isSubmitting ||
              !username.trim() ||
              !password
            }
            style={{
              width: '100%',
              padding: '12px',
              border: 'none',
              borderRadius: '9px',
              background: '#172554',
              color: '#ffffff',
              fontSize: '14px',
              fontWeight: 600,
              cursor: isSubmitting
                ? 'wait'
                : 'pointer',
              opacity: isSubmitting ? 0.7 : 1,
            }}
          >
            {isSubmitting
              ? 'Signing in...'
              : 'Sign in'}
          </button>
        </form>
      </section>
    </main>
  )
}

export default LoginPage