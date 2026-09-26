import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  Navigate,
  useLocation,
  useNavigate,
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
  const navigate = useNavigate()

  const [showLoginForm, setShowLoginForm] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

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

  const handleGuestAccess = () => {
    navigate('/')
  }

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
          maxWidth: showLoginForm
            ? '420px'
            : '760px',
          padding: '36px',
          borderRadius: '18px',
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          boxShadow:
            '0 18px 45px rgba(15, 23, 42, 0.10)',
          boxSizing: 'border-box',
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
              flexShrink: 0,
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

        {!showLoginForm ? (
          <>
            <div
              style={{
                marginBottom: '28px',
              }}
            >
              <h1
                style={{
                  margin: 0,
                  fontSize: '28px',
                  lineHeight: 1.2,
                  color: '#0f172a',
                }}
              >
                Welcome to WorkForceIQ
              </h1>

              <p
                style={{
                  margin: '10px 0 0',
                  fontSize: '14px',
                  lineHeight: 1.6,
                  color: '#64748b',
                }}
              >
                Explore workforce intelligence and analytics,
                or sign in to manage workforce data.
              </p>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns:
                  'repeat(2, minmax(0, 1fr))',
                gap: '16px',
                alignItems: 'stretch',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  minWidth: 0,
                  padding: '22px',
                  borderRadius: '14px',
                  background: '#f8fbff',
                  border: '1px solid #dbeafe',
                  boxSizing: 'border-box',
                }}
              >
                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: 700,
                    color: '#0f172a',
                    marginBottom: '10px',
                  }}
                >
                  Explore the system
                </div>

                <p
                  style={{
                    margin: 0,
                    minHeight: '72px',
                    fontSize: '13px',
                    lineHeight: 1.65,
                    color: '#64748b',
                  }}
                >
                  View dashboards, charts, workforce
                  analytics, utilization, project insights,
                  and staffing intelligence without signing in.
                </p>

                <div
                  style={{
                    marginTop: '18px',
                    width: '100%',
                  }}
                >
                  <button
                    type="button"
                    onClick={handleGuestAccess}
                    style={{
                      width: '100%',
                      height: '44px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxSizing: 'border-box',
                      padding: '0 16px',
                      border: '1px solid #cbd5e1',
                      borderRadius: '9px',
                      background: '#ffffff',
                      color: '#172554',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Enter System
                  </button>
                </div>
              </div>

              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  minWidth: 0,
                  padding: '22px',
                  borderRadius: '14px',
                  background: '#f8fbff',
                  border: '1px solid #dbeafe',
                  boxSizing: 'border-box',
                }}
              >
                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: 700,
                    color: '#0f172a',
                    marginBottom: '10px',
                  }}
                >
                  Manage workforce data
                </div>

                <p
                  style={{
                    margin: 0,
                    minHeight: '72px',
                    fontSize: '13px',
                    lineHeight: 1.65,
                    color: '#64748b',
                  }}
                >
                  Sign in when you need access to protected
                  workforce management operations.
                </p>

                <div
                  style={{
                    marginTop: '18px',
                    width: '100%',
                  }}
                >
                  <button
                    type="button"
                    onClick={() => {
                      setError('')
                      setShowLoginForm(true)
                    }}
                    style={{
                      width: '100%',
                      height: '44px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxSizing: 'border-box',
                      padding: '0 16px',
                      border: '1px solid #172554',
                      borderRadius: '9px',
                      background: '#172554',
                      color: '#ffffff',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    Sign In
                  </button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            <div
              style={{
                marginBottom: '24px',
              }}
            >
              <button
                type="button"
                onClick={() => {
                  setError('')
                  setShowLoginForm(false)
                }}
                style={{
                  padding: 0,
                  border: 'none',
                  background: 'transparent',
                  color: '#2563eb',
                  fontSize: '13px',
                  cursor: 'pointer',
                }}
              >
                ← Back
              </button>

              <h1
                style={{
                  margin: '18px 0 0',
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
                Sign in to access protected workforce
                management operations.
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
                    border: '1px solid #fecaca',
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
                  height: '44px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxSizing: 'border-box',
                  padding: '0 16px',
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
          </>
        )}
      </section>
    </main>
  )
}

export default LoginPage