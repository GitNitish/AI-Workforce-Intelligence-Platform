import { NavLink, Outlet } from 'react-router-dom'
import '../App.css'

const navigationItems = [
  { to: '/', label: 'Dashboard', icon: '⌂' },
  { to: '/analytics', label: 'Analytics', icon: '▥' },
  { to: '/employees', label: 'Employees', icon: '◉' },
  { to: '/projects', label: 'Projects', icon: '▣' },
  { to: '/requirements', label: 'Requirements', icon: '▤' },
  { to: '/recommendations', label: 'Recommendations', icon: '✦' },
]

function AppLayout() {
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
              <div
                className="user-avatar"
                aria-hidden="true"
              >
                N
              </div>

              <div className="user-details">
                <strong>Nitish Malik</strong>

                <span>Workspace</span>
              </div>

              <span
                className="user-chevron"
                aria-hidden="true"
              >
                ˅
              </span>
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