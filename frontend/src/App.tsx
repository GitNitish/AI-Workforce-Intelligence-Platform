import {
  BrowserRouter,
  Route,
  Routes,
} from 'react-router-dom'

import { AuthProvider } from './auth/AuthContext.tsx'
import ProtectedRoute from './auth/ProtectedRoute'
import AppLayout from './layouts/AppLayout'
import AnalyticsPage from './pages/AnalyticsPage'
import EmployeesPage from './pages/EmployeesPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import ProjectAnalyticsPage from './pages/ProjectAnalyticsPage'
import ProjectsPage from './pages/ProjectsPage'
import RecommendationsPage from './pages/RecommendationsPage'
import RequirementsPage from './pages/RequirementsPage'
import StaffingDemandPage from './pages/StaffingDemandPage'
import UtilizationDetailPage from './pages/UtilizationDetailPage'
import WorkforceOutlookPage from './pages/WorkforceOutlookPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route
            path="/login"
            element={<LoginPage />}
          />

          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route
              path="/"
              element={<HomePage />}
            />

            <Route
              path="/analytics"
              element={<AnalyticsPage />}
            />

            <Route
              path="/analytics/utilization"
              element={
                <UtilizationDetailPage />
              }
            />

            <Route
              path="/analytics/staffing"
              element={
                <StaffingDemandPage />
              }
            />

            <Route
              path="/analytics/projects"
              element={
                <ProjectAnalyticsPage />
              }
            />

            <Route
              path="/analytics/outlook"
              element={
                <WorkforceOutlookPage />
              }
            />

            <Route
              path="/employees"
              element={<EmployeesPage />}
            />

            <Route
              path="/projects"
              element={<ProjectsPage />}
            />

            <Route
              path="/requirements"
              element={
                <RequirementsPage />
              }
            />

            <Route
              path="/recommendations"
              element={
                <RecommendationsPage />
              }
            />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App