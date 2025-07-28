import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ErrorBoundary } from '@/components/ui/error-boundary'
import { StatsSkeleton } from '@/components/ui/skeleton-loader'
import { useToast } from '@/hooks/use-toast'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import axios from 'axios'

// Import tab components (to be created in subsequent tasks)
import PropertiesTab from '@/components/dashboard/PropertiesTab'
import ManagersTab from '@/components/dashboard/ManagersTab'
import { EmployeesTab } from '@/components/dashboard/EmployeesTab'
import { ApplicationsTab } from '@/components/dashboard/ApplicationsTab'
import { AnalyticsTab } from '@/components/dashboard/AnalyticsTab'

interface DashboardStats {
  totalProperties: number
  totalManagers: number
  totalEmployees: number
  pendingApplications: number
}

export default function HRDashboard() {
  const { user, logout, loading: authLoading } = useAuth()
  const { error: showErrorToast, success: showSuccessToast } = useToast()
  const [stats, setStats] = useState<DashboardStats>({
    totalProperties: 0,
    totalManagers: 0,
    totalEmployees: 0,
    pendingApplications: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)

  useEffect(() => {
    // Only fetch stats after auth is loaded and user is available
    if (!authLoading && user) {
      fetchDashboardStats()
    }
  }, [retryCount, authLoading, user])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = localStorage.getItem('token')
      const axiosConfig = {
        headers: { Authorization: `Bearer ${token}` }
      }
      
      const response = await axios.get('http://127.0.0.1:8000/hr/dashboard-stats', axiosConfig)
      setStats(response.data)
      if (retryCount > 0) {
        showSuccessToast('Dashboard refreshed', 'Stats have been updated successfully')
      }
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
      const errorMessage = axios.isAxiosError(error) 
        ? error.response?.data?.detail || error.message 
        : 'Failed to load dashboard statistics'
      setError(errorMessage)
      showErrorToast('Failed to load dashboard', errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
  }

  if (user?.role !== 'hr') {
    return (
      <div className="responsive-container padding-lg flex items-center justify-center min-h-screen">
        <Card className="card-elevated card-rounded-lg max-w-md w-full">
          <CardContent className="card-padding-lg text-center spacing-sm">
            <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-heading-lg text-primary mb-2">Access Denied</h2>
            <p className="text-body-md text-secondary mb-6">HR role required to access this dashboard.</p>
            <Button onClick={logout} className="btn-primary btn-size-md">
              Return to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="responsive-container padding-md">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-8">
          <div className="spacing-xs">
            <h1 className="text-display-md">HR Dashboard</h1>
            <p className="text-body-md text-secondary">Welcome, {user?.email}</p>
          </div>
          <div className="flex items-center gap-3">
            {error && (
              <Button 
                onClick={handleRetry} 
                variant="outline" 
                size="sm"
                className="btn-secondary btn-size-sm"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            )}
            <Button onClick={logout} variant="outline" className="btn-secondary btn-size-md">
              Logout
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6 animate-slide-down">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="mb-8">
          {loading ? (
            <StatsSkeleton count={4} />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="space-y-2">
                    <p className="text-3xl font-bold text-blue-600">{stats.totalProperties}</p>
                    <p className="text-sm text-gray-500">Properties</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="space-y-2">
                    <p className="text-3xl font-bold text-blue-600">{stats.totalManagers}</p>
                    <p className="text-sm text-gray-500">Managers</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="space-y-2">
                    <p className="text-3xl font-bold text-blue-600">{stats.totalEmployees}</p>
                    <p className="text-sm text-gray-500">Employees</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <CardContent className="p-6 text-center">
                  <div className="space-y-2">
                    <p className="text-3xl font-bold text-blue-600">{stats.pendingApplications}</p>
                    <p className="text-sm text-gray-500">Pending Applications</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <Tabs defaultValue="properties" className="spacing-md">
          <TabsList className="nav-tabs w-full grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-1 bg-gray-50 p-1 rounded-xl">
            <TabsTrigger value="properties" className="nav-tab rounded-lg">Properties</TabsTrigger>
            <TabsTrigger value="managers" className="nav-tab rounded-lg">Managers</TabsTrigger>
            <TabsTrigger value="employees" className="nav-tab rounded-lg">Employees</TabsTrigger>
            <TabsTrigger value="applications" className="nav-tab rounded-lg">Applications</TabsTrigger>
            <TabsTrigger value="analytics" className="nav-tab rounded-lg">Analytics</TabsTrigger>
          </TabsList>

        <TabsContent value="properties">
          <PropertiesTab onStatsUpdate={fetchDashboardStats} />
        </TabsContent>

        <TabsContent value="managers">
          <ManagersTab onStatsUpdate={fetchDashboardStats} />
        </TabsContent>

        <TabsContent value="employees">
          <EmployeesTab userRole="hr" onStatsUpdate={fetchDashboardStats} />
        </TabsContent>

        <TabsContent value="applications">
          <ApplicationsTab userRole="hr" onStatsUpdate={fetchDashboardStats} />
        </TabsContent>

        <TabsContent value="analytics">
          <AnalyticsTab userRole="hr" />
        </TabsContent>
      </Tabs>
    </div>
    </ErrorBoundary>
  )
}