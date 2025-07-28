import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { HRDashboardLayout } from '@/components/layouts/HRDashboardLayout'
import { ManagerDashboardLayout } from '@/components/layouts/ManagerDashboardLayout'
import { OnboardingLayout } from '@/components/layouts/OnboardingLayout'
import PropertiesTab from '@/components/dashboard/PropertiesTab'
import ManagersTab from '@/components/dashboard/ManagersTab'
import { EmployeesTab } from '@/components/dashboard/EmployeesTab'
import { ApplicationsTab } from '@/components/dashboard/ApplicationsTab'
import { AnalyticsTab } from '@/components/dashboard/AnalyticsTab'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import HRDashboard from './pages/HRDashboard'
import ManagerDashboard from './pages/ManagerDashboard'
import EnhancedManagerDashboard from './pages/EnhancedManagerDashboard'
import JobApplicationForm from './pages/JobApplicationForm'
import OnboardingPortal from './pages/OnboardingPortal'
import EnhancedOnboardingPortal from './pages/EnhancedOnboardingPortal'
import OnboardingWelcome from './pages/OnboardingWelcome'
import SecretPortal from './pages/SecretPortal'
import TestComponents from './TestComponents'
import SimpleTest from './SimpleTest'
import TestStatus from './TestStatus'
import TestStepComponents from './TestStepComponents'
import TestOnboardingFlow from './pages/TestOnboardingFlow'
import WelcomePage from './pages/WelcomePage'
// Onboarding step components
import PersonalInfoStep from './pages/onboarding/PersonalInfoStep'
import I9Section1Step from './pages/onboarding/I9Section1Step'
import I9SupplementsStep from './pages/onboarding/I9SupplementsStep'
import DocumentUploadStep from './pages/onboarding/DocumentUploadStep'
import W4FormStep from './pages/onboarding/W4FormStep'
import DirectDepositStep from './pages/onboarding/DirectDepositStep'
import HealthInsuranceStep from './pages/onboarding/HealthInsuranceStep'
import CompanyPoliciesStep from './pages/onboarding/CompanyPoliciesStep'
import TraffickingAwarenessStep from './pages/onboarding/TrafficakingAwarenessStep'
import WeaponsPolicyStep from './pages/onboarding/WeaponsPolicyStep'
import EmployeeReviewStep from './pages/onboarding/EmployeeReviewStep'
import OnboardingComplete from './pages/OnboardingComplete'
import { AuthProvider } from './contexts/AuthContext'
import { LanguageProvider } from './contexts/LanguageContext'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Router>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              
              {/* HR Dashboard Routes with nested routing */}
              <Route path="/hr" element={
                <ProtectedRoute requiredRole="hr">
                  <HRDashboardLayout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/hr/properties" replace />} />
                <Route path="properties" element={<PropertiesTab onStatsUpdate={() => {}} />} />
                <Route path="managers" element={<ManagersTab onStatsUpdate={() => {}} />} />
                <Route path="employees" element={<EmployeesTab userRole="hr" onStatsUpdate={() => {}} />} />
                <Route path="applications" element={<ApplicationsTab userRole="hr" onStatsUpdate={() => {}} />} />
                <Route path="analytics" element={<AnalyticsTab userRole="hr" />} />
              </Route>
              
              {/* Manager Dashboard Routes with nested routing */}
              <Route path="/manager" element={
                <ProtectedRoute requiredRole="manager">
                  <ManagerDashboardLayout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/manager/applications" replace />} />
                <Route path="applications" element={<ApplicationsTab userRole="manager" onStatsUpdate={() => {}} />} />
                <Route path="employees" element={<EmployeesTab userRole="manager" onStatsUpdate={() => {}} />} />
                <Route path="analytics" element={<AnalyticsTab userRole="manager" />} />
              </Route>
              
              {/* Legacy routes for backward compatibility */}
              <Route path="/hr-old" element={
                <ProtectedRoute requiredRole="hr">
                  <HRDashboard />
                </ProtectedRoute>
              } />
              <Route path="/manager-old" element={
                <ProtectedRoute requiredRole="manager">
                  <ManagerDashboard />
                </ProtectedRoute>
              } />
              <Route path="/manager-enhanced" element={
                <ProtectedRoute requiredRole="manager">
                  <EnhancedManagerDashboard />
                </ProtectedRoute>
              } />
              
              {/* Other application routes */}
              <Route path="/apply/:propertyId" element={<JobApplicationForm />} />
              
              {/* Onboarding routes - Professional step-by-step approach */}
              <Route path="/onboarding" element={<OnboardingLayout />}>
                <Route index element={<Navigate to="/onboarding/personal-info" replace />} />
                <Route path="personal-info" element={<PersonalInfoStep />} />
                <Route path="i9-section1" element={<I9Section1Step />} />
                <Route path="i9-supplements" element={<I9SupplementsStep />} />
                <Route path="document-upload" element={<DocumentUploadStep />} />
                <Route path="w4-form" element={<W4FormStep />} />
                <Route path="direct-deposit" element={<DirectDepositStep />} />
                <Route path="health-insurance" element={<HealthInsuranceStep />} />
                <Route path="company-policies" element={<CompanyPoliciesStep />} />
                <Route path="trafficking-awareness" element={<TraffickingAwarenessStep />} />
                <Route path="weapons-policy" element={<WeaponsPolicyStep />} />
                <Route path="employee-review" element={<EmployeeReviewStep />} />
              </Route>
              
              {/* Onboarding welcome/entry point */}
              <Route path="/onboarding-welcome" element={<OnboardingWelcome />} />
              <Route path="/onboarding-complete" element={<OnboardingComplete />} />
              
              {/* Legacy onboarding routes */}
              <Route path="/onboard" element={<EnhancedOnboardingPortal />} />
              <Route path="/onboard/:employeeId" element={<OnboardingPortal />} />
              <Route path="/secret" element={<SecretPortal />} />
              <Route path="/test" element={<TestComponents />} />
              <Route path="/simple-test" element={<SimpleTest />} />
              <Route path="/test-status" element={<TestStatus />} />
              <Route path="/test-steps" element={<TestStepComponents />} />
              <Route path="/test-onboarding-flow" element={<TestOnboardingFlow />} />
              <Route path="/welcome" element={<WelcomePage />} />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </LanguageProvider>
    </AuthProvider>
  )
}

export default App
