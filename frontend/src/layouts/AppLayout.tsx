
import {
  NavLink,
  Outlet,
  useNavigate,
} from 'react-router-dom'
import { useState } from 'react'
import '../App.css'

import { useAuth } from '../auth/useAuth'

const navigationItems = [
  { to: '/', label: 'Dashboard', icon: 'D' },
  { to: '/analytics', label: 'Analytics', icon: 'A' },
  { to: '/employees', label: 'Employees', icon: 'E' },
  { to: '/projects', label: 'Projects', icon: 'P' },
  { to: '/requirements', label: 'Requirements', icon: 'R' },
  { to: '/recommendations', label: 'Recommendations', icon: 'M' },
  { to: '/assistant', label: 'Assistant', icon: 'AI' },
]

function getUserInitial(username: string): string {
  return username.charAt(0).toUpperCase()
}

function AppLayout() {
  const { user, logout, hasPermission } = useAuth()
  const navigate = useNavigate()

  const [isUserMenuOpen, setIsUserMenuOpen] =
    useState(false)

  const isAdmin = user?.role?.toLowerCase() === 'admin'

  const canViewAllocations =
    hasPermission('allocation.read')

  const username = user?.username ?? 'Guest'
  const role = user?.role ?? 'Guest'
  const userInitial = getUserInitial(username)

  function handleLogout(): void {
    logout()
    setIsUserMenuOpen(false)
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-shell">
      <div className="main-area">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">W</div>

            <div>
              <div className="brand-name">
                WorkForceIQ
              </div>

              <div className="brand-subtitle">
                Workforce Intelligence
              </div>
            </div>
          </div>

          <div className="topbar-actions">
            <div className="platform-indicator">
              <span
                className="status-dot"
                aria-hidden="true"
              />

              <span>Platform Online</span>
            </div>

            <div className="environment-badge">
              LOCAL
            </div>

            <button
              type="button"
              className="notification-button"
              aria-label="Notifications"
              title="Notifications"
            >
              <span
                className="notification-symbol"
                aria-hidden="true"
              >
                N
              </span>

              <span className="notification-dot" />
            </button>

            <div className="user-context">
              <button
                type="button"
                className="user-context-button"
                aria-expanded={isUserMenuOpen}
                aria-haspopup="menu"
                aria-label={
                  user
                    ? `Account menu for ${username}`
                    : 'Guest account'
                }
                onClick={() =>
                  setIsUserMenuOpen(
                    (isOpen) => !isOpen,
                  )
                }
              >
                <div
                  className="user-avatar"
                  aria-hidden="true"
                >
                  {userInitial}
                </div>

                <div className="user-details">
                  <strong>{username}</strong>

                  <span>{role}</span>
                </div>

                <span
                  className="user-chevron"
                  aria-hidden="true"
                >
                  {isUserMenuOpen ? '-' : '+'}
                </span>
              </button>

              {isUserMenuOpen && (
                <div
                  className="user-menu"
                  role="menu"
                >
                  <div className="user-menu-header">
                    <strong>{username}</strong>
                    <span>{role}</span>
                  </div>

                  {user ? (
                    <button
                      type="button"
                      className="user-menu-item"
                      role="menuitem"
                      onClick={handleLogout}
                    >
                      <span aria-hidden="true">
                        L
                      </span>

                      <span>Logout</span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="user-menu-item"
                      role="menuitem"
                      onClick={() => {
                        setIsUserMenuOpen(false)
                        navigate('/login')
                      }}
                    >
                      <span aria-hidden="true">
                        A
                      </span>

                      <span>Admin Login</span>
                    </button>
                  )}

                  {isAdmin && (
                    <div className="user-menu-header">
                      <span>
                        Administrator access enabled
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        <nav
          className="main-navigation"
          aria-label="Main navigation"
        >
          <div className="navigation-group">
            <div className="nav-section-label">
              WORKSPACE
            </div>

            {navigationItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `nav-link${isActive ? ' active' : ''}`
                }
              >
                <span
                  className="nav-icon"
                  aria-hidden="true"
                >
                  {item.icon}
                </span>

                <span>{item.label}</span>
              </NavLink>
            ))}

            {canViewAllocations && (
              <NavLink
                to="/allocations"
                className={({ isActive }) =>
                  `nav-link${isActive ? ' active' : ''}`
                }
              >
                <span
                  className="nav-icon"
                  aria-hidden="true"
                >
                  AL
                </span>

                <span>Allocations</span>
              </NavLink>
            )}
          </div>
        </nav>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppLayout
