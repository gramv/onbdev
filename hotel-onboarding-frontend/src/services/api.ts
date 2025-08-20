/**
 * Centralized API Service
 * Handles all API calls with proper configuration
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

// API base URL - uses Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Handle wrapped responses (data.data pattern)
    if (response.data && response.data.data !== undefined) {
      return { ...response, data: response.data.data }
    }
    return response
  },
  (error) => {
    // Handle specific error cases
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break
        case 403:
          // Forbidden - user doesn't have permission
          console.error('Access denied:', error.response.data)
          break
        case 404:
          // Not found
          console.error('Resource not found:', error.response.data)
          break
        case 500:
          // Server error
          console.error('Server error:', error.response.data)
          break
      }
    }
    return Promise.reject(error)
  }
)

// API endpoints organized by feature
export const api = {
  // Authentication
  auth: {
    login: (email: string, password: string) =>
      apiClient.post('/api/auth/login', { email, password }),
    logout: () => apiClient.post('/api/auth/logout'),
    me: () => apiClient.get('/api/auth/me'),
    refreshToken: () => apiClient.post('/api/auth/refresh'),
  },

  // HR Dashboard
  hr: {
    getDashboardStats: () => apiClient.get('/api/hr/dashboard-stats'),
    getProperties: () => apiClient.get('/api/hr/properties'),
    createProperty: (data: any) => {
      // Convert to form data for backend
      const params = new URLSearchParams()
      Object.keys(data).forEach(key => {
        if (data[key] !== undefined && data[key] !== null) {
          params.append(key, data[key].toString())
        }
      })
      return apiClient.post('/api/hr/properties', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    },
    updateProperty: (id: string, data: any) => {
      // Convert to form data for backend
      const params = new URLSearchParams()
      Object.keys(data).forEach(key => {
        if (data[key] !== undefined && data[key] !== null) {
          params.append(key, data[key].toString())
        }
      })
      return apiClient.put(`/api/hr/properties/${id}`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    },
    deleteProperty: (id: string) => apiClient.delete(`/api/hr/properties/${id}`),
    getPropertyStats: (propertyId: string) => apiClient.get(`/api/hr/properties/${propertyId}/stats`),
    getManagers: (params?: { include_inactive?: boolean }) => 
      apiClient.get('/api/hr/managers', { params }),
    createManager: (data: any) => {
      // Convert to form data for backend
      const params = new URLSearchParams()
      Object.keys(data).forEach(key => {
        if (data[key] !== undefined && data[key] !== null) {
          params.append(key, data[key].toString())
        }
      })
      return apiClient.post('/api/hr/managers', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    },
    updateManager: (id: string, data: any) => {
      // Convert to form data for backend
      const params = new URLSearchParams()
      Object.keys(data).forEach(key => {
        if (data[key] !== undefined && data[key] !== null) {
          params.append(key, data[key].toString())
        }
      })
      return apiClient.put(`/api/hr/managers/${id}`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    },
    deleteManager: (id: string) => apiClient.delete(`/api/hr/managers/${id}`),
    reactivateManager: (id: string) => apiClient.post(`/api/hr/managers/${id}/reactivate`),
    assignManagerToProperty: (propertyId: string, managerId: string) => {
      const params = new URLSearchParams()
      params.append('manager_id', managerId)
      return apiClient.post(`/api/hr/properties/${propertyId}/managers`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    },
    removeManagerFromProperty: (propertyId: string, managerId: string) =>
      apiClient.delete(`/api/hr/properties/${propertyId}/managers/${managerId}`),
    assignManager: (managerId: string, propertyId: string) => {
      const params = new URLSearchParams()
      params.append('manager_id', managerId)
      params.append('property_id', propertyId)
      return apiClient.post('/api/hr/managers/assign', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    },
    getEmployees: () => apiClient.get('/api/hr/employees'),
    getApplications: () => apiClient.get('/api/hr/applications'),
    getAnalytics: () => apiClient.get('/api/hr/analytics'),
  },

  // Manager Dashboard
  manager: {
    getDashboardStats: () => apiClient.get('/api/manager/dashboard-stats'),
    getMyProperty: () => apiClient.get('/api/manager/property'),
    getMyEmployees: () => apiClient.get('/api/manager/employees'),
    getApplications: () => apiClient.get('/api/manager/applications'),
    approveApplication: (id: string) => apiClient.post(`/api/manager/applications/${id}/approve`),
    rejectApplication: (id: string) => apiClient.post(`/api/manager/applications/${id}/reject`),
  },

  // Employee Onboarding
  onboarding: {
    validateToken: (token: string) => apiClient.post('/api/onboarding/validate-token', { token }),
    getSession: () => apiClient.get('/api/onboarding/session'),
    saveStep: (stepId: string, data: any) => apiClient.post(`/api/onboarding/step/${stepId}/save`, data),
    completeStep: (stepId: string, data: any) => apiClient.post(`/api/onboarding/step/${stepId}/complete`, data),
    submit: () => apiClient.post('/api/onboarding/submit'),
    uploadDocument: (formData: FormData) =>
      apiClient.post('/api/onboarding/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
  },

  // I-9 Forms
  i9: {
    saveSection1: (employeeId: string, data: any) =>
      apiClient.post(`/api/onboarding/${employeeId}/i9-section1`, data),
    getSection1: (employeeId: string) =>
      apiClient.get(`/api/onboarding/${employeeId}/i9-section1`),
    generatePDF: (employeeId: string, data: any) =>
      apiClient.post(`/api/onboarding/${employeeId}/i9-section1/generate-pdf`, data),
  },

  // W-4 Forms
  w4: {
    save: (employeeId: string, data: any) =>
      apiClient.post(`/api/onboarding/${employeeId}/w4-form`, data),
    get: (employeeId: string) =>
      apiClient.get(`/api/onboarding/${employeeId}/w4-form`),
    generatePDF: (employeeId: string, data: any) =>
      apiClient.post(`/api/onboarding/${employeeId}/w4-form/generate-pdf`, data),
  },

  // Job Applications
  applications: {
    submit: (data: any) => apiClient.post('/api/applications/submit', data),
    getByProperty: (propertyId: string) => apiClient.get(`/api/applications/property/${propertyId}`),
    getById: (id: string) => apiClient.get(`/api/applications/${id}`),
    updateStatus: (id: string, status: string) =>
      apiClient.put(`/api/applications/${id}/status`, { status }),
  },

  // Properties (public endpoints)
  properties: {
    getPublic: () => apiClient.get('/api/properties/public'),
    getById: (id: string) => apiClient.get(`/api/properties/${id}`),
  },

  // Document Processing
  documents: {
    processOCR: (formData: FormData) =>
      apiClient.post('/api/documents/process-ocr', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    upload: (formData: FormData) =>
      apiClient.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    download: (documentId: string) =>
      apiClient.get(`/api/documents/${documentId}/download`, { responseType: 'blob' }),
  },

  // WebSocket connection info
  websocket: {
    getConnectionInfo: () => apiClient.get('/api/ws/connection-info'),
  },

  // Notifications
  notifications: {
    getCount: () => apiClient.get('/api/notifications/count'),
    getAll: () => apiClient.get('/api/notifications'),
    markAsRead: (id: string) => apiClient.put(`/api/notifications/${id}/read`),
    markAllAsRead: () => apiClient.put('/api/notifications/read-all'),
  },
}

// Export the raw client for custom requests
export { apiClient }

// Export default API object
export default api