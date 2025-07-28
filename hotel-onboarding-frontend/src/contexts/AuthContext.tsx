import React, { createContext, useContext, useState, useEffect } from 'react'
import axios, { AxiosError } from 'axios'

interface User {
  id: string
  email: string
  role: 'hr' | 'manager' | 'employee'
  first_name?: string
  last_name?: string
  property_id?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string, returnUrl?: string) => Promise<void>
  logout: () => void
  loading: boolean
  isAuthenticated: boolean
  hasRole: (role: string) => boolean
  returnUrl: string | null
  setReturnUrl: (url: string | null) => void
}

interface LoginResponse {
  token: string
  user: User
  expires_at: string
}

interface AuthError {
  message: string
  code?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const API_BASE_URL = 'http://127.0.0.1:8000'

// Configure axios defaults
axios.defaults.timeout = 10000 // 10 second timeout
axios.defaults.headers.common['Content-Type'] = 'application/json'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [returnUrl, setReturnUrl] = useState<string | null>(null)

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const storedToken = localStorage.getItem('token')
        const storedUser = localStorage.getItem('user')
        const storedReturnUrl = localStorage.getItem('returnUrl')
        
        if (storedToken && storedUser) {
          const userData = JSON.parse(storedUser)
          
          // Check if token is expired
          const expiresAt = localStorage.getItem('token_expires_at')
          if (expiresAt && new Date(expiresAt) <= new Date()) {
            // Token expired, clear auth data
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            localStorage.removeItem('token_expires_at')
            localStorage.removeItem('returnUrl')
          } else {
            setToken(storedToken)
            setUser(userData)
            axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
          }
        }
        
        if (storedReturnUrl) {
          setReturnUrl(storedReturnUrl)
        }
      } catch (error) {
        console.error('Failed to initialize auth from localStorage:', error)
        // Clear corrupted data
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('token_expires_at')
        localStorage.removeItem('returnUrl')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  // Set up axios interceptor for token expiration
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid, store current URL as return URL and logout
          const currentPath = window.location.pathname
          if (currentPath !== '/login' && currentPath !== '/') {
            setReturnUrl(currentPath)
            localStorage.setItem('returnUrl', currentPath)
          }
          logout()
        }
        return Promise.reject(error)
      }
    )

    return () => {
      axios.interceptors.response.eject(interceptor)
    }
  }, [])

  const login = async (email: string, password: string, providedReturnUrl?: string): Promise<void> => {
    try {
      // Send as JSON body to match updated backend
      const response = await axios.post<LoginResponse>(`${API_BASE_URL}/auth/login`, {
        email,
        password
      })
      
      const { token: newToken, user: userData, expires_at } = response.data
      
      // Store auth data
      setToken(newToken)
      setUser(userData)
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('token_expires_at', expires_at)
      
      // Set axios authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      
      // Handle return URL
      const targetReturnUrl = providedReturnUrl || returnUrl
      if (targetReturnUrl) {
        // Clear return URL from state and storage
        setReturnUrl(null)
        localStorage.removeItem('returnUrl')
        
        // Navigate to return URL after successful login
        window.location.href = targetReturnUrl
      }
      
    } catch (error) {
      console.error('Login failed:', error)
      
      // Handle different error types
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ detail: string }>
        
        if (error.code === 'ECONNREFUSED' || error.code === 'NETWORK_ERROR') {
          throw new Error('Unable to connect to server. Please check your connection and try again.')
        }
        
        if (axiosError.response?.status === 401) {
          throw new Error('Invalid email or password')
        }
        
        if (axiosError.response?.status === 400) {
          throw new Error(axiosError.response.data?.detail || 'Invalid request')
        }
        
        if (axiosError.response?.status && axiosError.response.status >= 500) {
          throw new Error('Server error. Please try again later.')
        }
        
        throw new Error(axiosError.response?.data?.detail || 'Login failed')
      }
      
      throw new Error('An unexpected error occurred')
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('token_expires_at')
    // Don't clear returnUrl on logout - it should persist for re-login
    delete axios.defaults.headers.common['Authorization']
  }

  const hasRole = (role: string): boolean => {
    return user?.role === role
  }

  const isAuthenticated = Boolean(token && user)

  const value = {
    user,
    token,
    login,
    logout,
    loading,
    isAuthenticated,
    hasRole,
    returnUrl,
    setReturnUrl
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
