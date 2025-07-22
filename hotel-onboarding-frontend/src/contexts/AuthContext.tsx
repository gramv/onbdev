import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

interface User {
  id: string
  email: string
  role: 'hr' | 'manager' | 'employee'
  property_id?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
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

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common['Authorization']
    }
    setLoading(false)
  }, [token])

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`)
      
      const { token: newToken, user: userData } = response.data
      setToken(newToken)
      setUser(userData)
      localStorage.setItem('token', newToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const value = {
    user,
    token,
    login,
    logout,
    loading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
