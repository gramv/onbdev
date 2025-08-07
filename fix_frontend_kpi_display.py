#!/usr/bin/env python3
"""
Fix Frontend KPI Display Issue
Comprehensive fix for the HR Dashboard KPI display problem
"""

import requests
import json
import time

def test_backend_api():
    """Test the backend API to ensure it's working correctly"""
    print("🔍 Testing backend API...")
    
    # Login
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Backend login failed: {login_response.status_code}")
        return False
    
    token = login_response.json().get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test dashboard stats
    stats_response = requests.get('http://127.0.0.1:8000/hr/dashboard-stats', headers=headers)
    
    if stats_response.status_code == 200:
        data = stats_response.json()
        stats_data = data.get('data', {})
        
        print(f"✅ Backend API working correctly")
        print(f"   Properties: {stats_data.get('totalProperties', 0)}")
        print(f"   Managers: {stats_data.get('totalManagers', 0)}")
        print(f"   Employees: {stats_data.get('totalEmployees', 0)}")
        print(f"   Pending Applications: {stats_data.get('pendingApplications', 0)}")
        
        return True
    else:
        print(f"❌ Backend API failed: {stats_response.status_code}")
        return False

def check_frontend_server():
    """Check if the frontend server is running"""
    print("\n🔍 Checking frontend server...")
    
    try:
        # Try to reach the frontend server
        frontend_response = requests.get('http://localhost:3000', timeout=5)
        
        if frontend_response.status_code == 200:
            print("✅ Frontend server is running on http://localhost:3000")
            return True
        else:
            print(f"⚠️ Frontend server responded with status: {frontend_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server is not running on http://localhost:3000")
        print("💡 Please start the frontend server with: npm start or yarn start")
        return False
    except requests.exceptions.Timeout:
        print("⚠️ Frontend server is slow to respond")
        return False

def create_debug_component():
    """Create a debug version of the HR Dashboard component"""
    print("\n🔧 Creating debug version of HR Dashboard component...")
    
    debug_component = '''import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import axios from 'axios'

interface DashboardStats {
  totalProperties: number
  totalManagers: number
  totalEmployees: number
  pendingApplications: number
}

export default function HRDashboardDebug() {
  const { user, logout } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    totalProperties: 0,
    totalManagers: 0,
    totalEmployees: 0,
    pendingApplications: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [debugInfo, setDebugInfo] = useState<any>(null)

  useEffect(() => {
    if (user) {
      fetchDashboardStats()
    }
  }, [user])

  const fetchDashboardStats = async () => {
    console.log('🔍 [DEBUG] Starting fetchDashboardStats...')
    
    try {
      setLoading(true)
      setError(null)
      
      const token = localStorage.getItem('token')
      console.log('🔍 [DEBUG] Token exists:', !!token)
      console.log('🔍 [DEBUG] Token preview:', token ? token.substring(0, 20) + '...' : 'None')
      
      const axiosConfig = {
        headers: { Authorization: `Bearer ${token}` }
      }
      
      console.log('🔍 [DEBUG] Making API request to /hr/dashboard-stats...')
      const response = await axios.get('http://127.0.0.1:8000/hr/dashboard-stats', axiosConfig)
      
      console.log('🔍 [DEBUG] API Response status:', response.status)
      console.log('🔍 [DEBUG] API Response headers:', response.headers)
      console.log('🔍 [DEBUG] API Response data:', response.data)
      
      // Handle the standardized API response format
      const statsData = response.data.data || response.data
      console.log('🔍 [DEBUG] Extracted stats data:', statsData)
      
      // Set debug info
      setDebugInfo({
        rawResponse: response.data,
        extractedData: statsData,
        timestamp: new Date().toISOString()
      })
      
      console.log('🔍 [DEBUG] Setting stats state:', statsData)
      setStats(statsData)
      
      console.log('🔍 [DEBUG] Stats state should be updated now')
      
    } catch (error) {
      console.error('🔍 [DEBUG] Error in fetchDashboardStats:', error)
      setError(error instanceof Error ? error.message : 'Unknown error')
      setDebugInfo({
        error: error,
        timestamp: new Date().toISOString()
      })
    } finally {
      setLoading(false)
      console.log('🔍 [DEBUG] fetchDashboardStats completed')
    }
  }

  if (user?.role !== 'hr') {
    return <div>Access Denied - HR role required</div>
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">HR Dashboard (DEBUG VERSION)</h1>
        <p>Welcome, {user?.email}</p>
        <Button onClick={logout} className="mt-2">Logout</Button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          Error: {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Properties</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? 'Loading...' : stats.totalProperties}
            </div>
            <div className="text-sm text-gray-500">
              Raw value: {JSON.stringify(stats.totalProperties)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Managers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? 'Loading...' : stats.totalManagers}
            </div>
            <div className="text-sm text-gray-500">
              Raw value: {JSON.stringify(stats.totalManagers)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Employees</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? 'Loading...' : stats.totalEmployees}
            </div>
            <div className="text-sm text-gray-500">
              Raw value: {JSON.stringify(stats.totalEmployees)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pending Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {loading ? 'Loading...' : stats.pendingApplications}
            </div>
            <div className="text-sm text-gray-500">
              Raw value: {JSON.stringify(stats.pendingApplications)}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Debug Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <strong>Loading State:</strong> {loading ? 'true' : 'false'}
            </div>
            <div>
              <strong>Error State:</strong> {error || 'None'}
            </div>
            <div>
              <strong>Stats State:</strong>
              <pre className="bg-gray-100 p-2 rounded mt-1 text-sm">
                {JSON.stringify(stats, null, 2)}
              </pre>
            </div>
            {debugInfo && (
              <div>
                <strong>Debug Info:</strong>
                <pre className="bg-gray-100 p-2 rounded mt-1 text-sm max-h-64 overflow-y-auto">
                  {JSON.stringify(debugInfo, null, 2)}
                </pre>
              </div>
            )}
          </div>
          <Button onClick={fetchDashboardStats} className="mt-4">
            Refresh Stats
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}'''
    
    # Write the debug component
    with open('hotel-onboarding-frontend/src/pages/HRDashboardDebug.tsx', 'w') as f:
        f.write(debug_component)
    
    print("✅ Debug component created at: hotel-onboarding-frontend/src/pages/HRDashboardDebug.tsx")
    print("💡 To use this debug component:")
    print("   1. Import it in your App.tsx or routing file")
    print("   2. Add a route like: <Route path='/hr-debug' element={<HRDashboardDebug />} />")
    print("   3. Navigate to http://localhost:3000/hr-debug")
    print("   4. Check the browser console for detailed debug logs")

def provide_troubleshooting_steps():
    """Provide troubleshooting steps"""
    print("\n🔧 TROUBLESHOOTING STEPS:")
    print("=" * 50)
    
    print("\n1. CHECK BROWSER CONSOLE:")
    print("   - Open browser dev tools (F12)")
    print("   - Go to Console tab")
    print("   - Look for any JavaScript errors")
    print("   - Look for the debug logs: '[DEBUG] Starting fetchDashboardStats...'")
    
    print("\n2. CHECK NETWORK TAB:")
    print("   - Open browser dev tools (F12)")
    print("   - Go to Network tab")
    print("   - Refresh the HR Dashboard page")
    print("   - Look for the /hr/dashboard-stats request")
    print("   - Check if it returns 200 status and correct data")
    
    print("\n3. CHECK REACT DEVTOOLS:")
    print("   - Install React Developer Tools browser extension")
    print("   - Open React DevTools")
    print("   - Find the HRDashboard component")
    print("   - Check the 'stats' state value")
    
    print("\n4. CLEAR BROWSER CACHE:")
    print("   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
    print("   - Or clear browser cache completely")
    
    print("\n5. CHECK FRONTEND BUILD:")
    print("   - Stop the frontend server")
    print("   - Delete node_modules and package-lock.json")
    print("   - Run: npm install")
    print("   - Run: npm start")
    
    print("\n6. USE DEBUG COMPONENT:")
    print("   - Use the debug component created above")
    print("   - It will show detailed information about the API calls and state")

def main():
    print("🚀 Fix Frontend KPI Display Issue")
    print("=" * 50)
    
    # Test backend API
    backend_ok = test_backend_api()
    
    # Check frontend server
    frontend_ok = check_frontend_server()
    
    # Create debug component
    create_debug_component()
    
    # Provide troubleshooting steps
    provide_troubleshooting_steps()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    
    if backend_ok and frontend_ok:
        print("✅ Backend API is working correctly")
        print("✅ Frontend server is running")
        print("💡 The issue is likely in the React component or browser")
        print("🔧 Use the debug component and troubleshooting steps above")
    elif backend_ok and not frontend_ok:
        print("✅ Backend API is working correctly")
        print("❌ Frontend server is not running")
        print("💡 Start the frontend server first")
    elif not backend_ok:
        print("❌ Backend API is not working")
        print("💡 Fix the backend issues first")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Ensure both backend and frontend servers are running")
    print("2. Use the debug component to see detailed information")
    print("3. Check browser console for JavaScript errors")
    print("4. If still not working, there might be a React state management issue")

if __name__ == "__main__":
    main()