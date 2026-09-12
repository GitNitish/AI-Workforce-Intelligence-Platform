import { NavLink, Outlet } from 'react-router-dom'
import '../App.css'

const navigationItems = [
  { to: '/', label: 'Home', icon: '⌂' },
  { to: '/employees', label: 'Employees', icon: '◉' },
  { to: '/projects', label: 'Projects', icon: '▣' },
  { to: '/requirements', label: 'Requirements', icon: '▤' },
  { to: '/recommendations', label: 'Recommendations', icon: '✦' },
]

function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">W</div>
          <div>
            <div className="brand-name">WorkForceIQ</div>
            <div className="brand-subtitle">Workforce Intelligence</div>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          <div className="nav-section-label">WORKSPACE</div>

          {navigationItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `nav-link${isActive ? ' active' : ''}`
              }
            >
              <span className="nav-icon" aria-hidden="true">
                {item.icon}
              </span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" aria-hidden="true" />
          <div>
            <div className="system-status">Platform Online</div>
            <div className="system-status-subtitle">AI services ready</div>
          </div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div>
            <span className="topbar-label">AI Workforce Intelligence Platform</span>
          </div>

          <div className="topbar-context">
            <span className="environment-badge">LOCAL</span>
          </div>
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppLayout