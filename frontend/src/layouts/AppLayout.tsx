import {
  NavLink,
  Outlet,
  useNavigate,
} from 'react-router-dom'
import { useState } from 'react'
import '../App.css'

import { useAuth } from '../auth/useAuth'

const navigationItems = [
  { to: '/', label: 'Dashboard', icon: '⌂' },
  { to: '/analytics', label: 'Analytics', icon: '▥' },
  { to: '/employees', label: 'Employees', icon: '◉' },
  { to: '/projects', label: 'Projects', icon: '▣' },
  { to: '/requirements', label: 'Requirements', icon: '▤' },
  { to: '/recommendations', label: 'Recommendations', icon: '✦' },
]

function getUserInitial(username: string): string {
  return username.charAt(0).toUpperCase()
}

function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [isUserMenuOpen, setIsUserMenuOpen] =
    useState(false)

  const username = user?.username ?? 'User'
  const role = user?.role ?? 'Workspace'
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
              <div className="brand-name">WorkForceIQ</div>

              <div className="brand-subtitle">
                Workforce Intelligence
              </div>
            </div>
          </div>

          <div className="global-search">
            <span
              className="global-search-icon"
              aria-hidden="true"
            >
              ⌕
            </span>

            <input
              type="search"
              placeholder="Search employees, projects, skills..."
              aria-label="Search employees, projects and skills"
            />
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
              <span aria-hidden="true">♢</span>

              <span className="notification-dot" />
            </button>

            <div className="user-context">
              <button
                type="button"
                className="user-context-button"
                aria-expanded={isUserMenuOpen}
                aria-haspopup="menu"
                aria-label={`Account menu for ${username}`}
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
                  {isUserMenuOpen ? '⌃' : '˅'}
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

                  <button
                    type="button"
                    className="user-menu-item"
                    role="menuitem"
                    onClick={handleLogout}
                  >
                    <span aria-hidden="true">
                      ↪
                    </span>
                    <span>Logout</span>
                  </button>
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
          </div>

          <div className="navigation-management">
            <div className="nav-section-label">
              MANAGEMENT
            </div>

            <div className="nav-link nav-link-disabled">
              <span
                className="nav-icon"
                aria-hidden="true"
              >
                ⚙
              </span>

              <span>Administration</span>

              <span className="nav-coming-soon">
                Soon
              </span>
            </div>
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