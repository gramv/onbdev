import { useState, useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ErrorBoundary } from '@/components/ui/error-boundary'
import { StatsSkeleton, SkeletonCard } from '@/components/ui/skeleton-loader'
import { DashboardBreadcrumb } from '@/components/ui/breadcrumb'
import { DashboardNavigation, MANAGER_NAVIGATION_ITEMS } from '@/components/ui/dashboard-navigation'
import { useSimpleNavigation, useNavigationAnalytics } from '@/hooks/use-simple-navigation'
import { useToast } from '@/hooks/use-toast'
import { Building2, MapPin, Phone, AlertTriangle, RefreshCw, Bell } from 'lucide-react'
// QR generator card removed from the property panel per design feedback
import { api } from '@/services/api'

interface Property {
  id: string
  name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone?: string
  qr_code_url: string
  is_active: boolean
  created_at: string
}

interface DashboardStats {
  total_applications: number
  pending_applications: number
  approved_applications: number
  total_employees: number
  active_employees: number
}

export function ManagerDashboardLayout() {
  const { user, logout } = useAuth()
  const { error: showErrorToast, success: showSuccessToast } = useToast()
  const location = useLocation()
  const navigate = useNavigate()
  
  // Navigation state management
  const navigation = useSimpleNavigation({
    role: 'manager'
    // Removed onNavigate callback - React Router handles navigation
  })
  
  const { trackNavigation } = useNavigationAnalytics()
  
  const [property, setProperty] = useState<Property | null>(null)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const [isMobile, setIsMobile] = useState(false)
  const [notificationCount, setNotificationCount] = useState(0)

  // Check if we're on mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Refresh notification count periodically
  useEffect(() => {
    // Fetch initial count
    fetchNotificationCount()
    
    // Set up interval to refresh every 30 seconds
    const interval = setInterval(() => {
      fetchNotificationCount()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const currentSection = navigation.currentSection

  useEffect(() => {
    if (user) {
      fetchData()
    }
  }, [user, retryCount])

  // Redirect to default section if on base /manager route
  useEffect(() => {
    if (location.pathname === '/manager') {
      navigate('/manager/applications', { replace: true })
    }
  }, [location.pathname, navigate])

  const fetchNotificationCount = async () => {
    try {
      const response = await api.get('/notifications/count')
      if (response.data?.success) {
        setNotificationCount(response.data.data.unread_count || 0)
      }
    } catch (error) {
      console.error('Failed to fetch notification count:', error)
    }
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      await Promise.all([fetchPropertyData(), fetchDashboardStats(), fetchNotificationCount()])
      if (retryCount > 0) {
        showSuccessToast('Dashboard refreshed', 'Data has been updated successfully')
      }
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load dashboard data'
      setError(errorMessage)
      showErrorToast('Failed to load dashboard', errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const fetchPropertyData = async () => {
    const response = await api.manager.getMyProperty()
    // API service handles response unwrapping
    setProperty(response.data || null)
  }

  const fetchDashboardStats = async () => {
    const response = await api.manager.getDashboardStats()
    // API service handles response unwrapping
    setStats(response.data || {
      total_applications: 0,
      pending_applications: 0,
      approved_applications: 0,
      total_employees: 0,
      active_employees: 0
    })
  }

  const handleRetry = () => {
    setRetryCount(prev => prev + 1)
  }

  // Access control check
  if (user?.role !== 'manager') {
    return (
      <div className="responsive-container padding-lg flex items-center justify-center min-h-screen">
        <Card className="card-elevated card-rounded-lg max-w-md w-full">
          <CardContent className="card-padding-lg text-center spacing-sm">
            <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-heading-lg text-primary mb-2">Access Denied</h2>
            <p className="text-body-md text-secondary mb-6">Manager role required to access this dashboard.</p>
            <Button onClick={logout} className="">
              Return to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Property will be fetched from the backend, no need to check property_id in JWT

  // Add pending applications badge to navigation items
  const navigationItems = MANAGER_NAVIGATION_ITEMS.map(item => ({
    ...item,
    badge: item.key === 'applications' && stats && stats.pending_applications > 0 
      ? stats.pending_applications 
      : undefined
  }))

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background">
        <div className="responsive-container padding-md">
          {/* Header Section */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-6">
            <div className="spacing-xs">
              <h1 className="text-display-md">Manager Dashboard</h1>
              <p className="text-body-md text-secondary">Welcome back, {user.first_name} {user.last_name}</p>
            </div>
            <div className="flex items-center gap-3">
              {/* Notification Badge */}
              <button
                className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
                onClick={() => navigate('/manager/notifications')}
                title="Notifications"
              >
                <Bell className="h-5 w-5 text-gray-600" />
                {notificationCount > 0 && (
                  <Badge 
                    className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center bg-red-500 text-white text-xs"
                  >
                    {notificationCount > 99 ? '99+' : notificationCount}
                  </Badge>
                )}
              </button>
              {error && (
                <Button 
                  onClick={handleRetry} 
                  variant="outline" 
                  size="sm"
                  className=""
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              )}
              <Button onClick={logout} variant="outline" className="">
                Logout
              </Button>
            </div>
          </div>

          {/* Breadcrumb Navigation */}
          <div className="mb-6">
            <DashboardBreadcrumb 
              dashboard="Manager"
              currentPage={currentSection}
            />
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

          {/* Property Information Card */}
          <div className="mb-6">
            {loading ? (
              <SkeletonCard className="h-32" />
            ) : property ? (
              <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="text-xl font-semibold flex items-center gap-2 text-gray-900">
                    <Building2 className="h-5 w-5 text-blue-600" />
                    {property.name}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
                    <div className="flex items-start gap-3">
                      <MapPin className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 mb-1">Address</p>
                        {property.address || property.city || property.state || property.zip_code ? (
                          <p className="text-sm text-gray-600 leading-relaxed">
                            {property.address || ''}{property.address ? <br /> : null}
                            {[property.city, property.state].filter(Boolean).join(', ')}{(property.city || property.state) && property.zip_code ? ` ${property.zip_code}` : property.zip_code || ''}
                          </p>
                        ) : (
                          <p className="text-sm text-gray-400">Not set</p>
                        )}
                      </div>
                    </div>
                    {property.phone && (
                      <div className="flex items-start gap-3">
                        <Phone className="h-4 w-4 text-gray-400 mt-1 flex-shrink-0" />
                        <div>
                          <p className="text-sm font-medium text-gray-900 mb-1">Phone</p>
                          <p className="text-sm text-gray-600">{property.phone}</p>
                        </div>
                      </div>
                    )}
                    {/* QR card removed. Managers can use the Applications view QR button. */}
                  </div>
                </CardContent>
              </Card>
            ) : null}
          </div>

          {/* Stats Cards */}
          <div className="mb-8">
            {loading ? (
              <StatsSkeleton count={4} />
            ) : stats ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="space-y-2">
                      <p className="text-3xl font-bold text-blue-600">{stats.total_applications}</p>
                      <p className="text-sm text-gray-500">Total Applications</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="space-y-2">
                      <p className="text-3xl font-bold text-blue-600">{stats.pending_applications}</p>
                      <p className="text-sm text-gray-500">Pending Applications</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="space-y-2">
                      <p className="text-3xl font-bold text-blue-600">{stats.approved_applications}</p>
                      <p className="text-sm text-gray-500">Approved Applications</p>
                    </div>
                  </CardContent>
                </Card>
                <Card className="shadow-sm border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="space-y-2">
                      <p className="text-3xl font-bold text-blue-600">{stats.total_employees}</p>
                      <p className="text-sm text-gray-500">Total Employees</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : null}
          </div>

          {/* Navigation */}
          <div className="mb-6">
            <DashboardNavigation 
              items={navigationItems}
              userRole="manager"
              className="w-full"
              variant={isMobile ? 'mobile' : 'tabs'}
              showLabels={true}
              compact={false}
              orientation="horizontal"
              onNavigate={(item) => {
                trackNavigation(navigation.currentSection, item.key)
                // React Router Link handles navigation automatically
                // No need to call navigation.handleNavigationClick(item)
              }}
            />
          </div>

          {/* Main Content */}
          <div className="spacing-md">
            <Outlet context={{ 
              stats, 
              property,
              onStatsUpdate: fetchData,
              userRole: 'manager',
              propertyId: property?.id 
            }} />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}