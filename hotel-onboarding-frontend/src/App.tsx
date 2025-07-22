import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import HRDashboard from './pages/HRDashboard'
import ManagerDashboard from './pages/ManagerDashboard'
import JobApplicationForm from './pages/JobApplicationForm'
import OnboardingPortal from './pages/OnboardingPortal'
import SecretPortal from './pages/SecretPortal'
import { AuthProvider } from './contexts/AuthContext'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/hr" element={<HRDashboard />} />
            <Route path="/manager" element={<ManagerDashboard />} />
            <Route path="/apply/:propertyId" element={<JobApplicationForm />} />
            <Route path="/onboard/:employeeId" element={<OnboardingPortal />} />
            <Route path="/secret" element={<SecretPortal />} />
          </Routes>
          <Toaster />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
