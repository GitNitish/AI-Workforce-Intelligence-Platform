import { BrowserRouter, Route, Routes } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import EmployeesPage from './pages/EmployeesPage'
import HomePage from './pages/HomePage'
import ProjectsPage from './pages/ProjectsPage'
import RecommendationsPage from './pages/RecommendationsPage'
import RequirementsPage from './pages/RequirementsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/employees" element={<EmployeesPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/requirements" element={<RequirementsPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App