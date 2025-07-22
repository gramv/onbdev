import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import axios from 'axios'

export default function SecretPortal() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [secretKey, setSecretKey] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const response = await axios.post(`http://127.0.0.1:8000/secret/create-hr?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&secret_key=${encodeURIComponent(secretKey)}`)
      setMessage(`HR user created successfully: ${response.data.user.email}`)
      setEmail('')
      setPassword('')
      setSecretKey('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create HR user')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-red-600">🔒 Secret HR Portal</CardTitle>
          <CardDescription>
            Create HR administrator accounts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            {message && (
              <Alert>
                <AlertDescription className="text-green-600">{message}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">HR Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="admin@hr.com"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter password"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="secretKey">Secret Key</Label>
              <Input
                id="secretKey"
                type="password"
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                required
                placeholder="Enter secret key"
              />
            </div>
            
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Creating HR User...' : 'Create HR User'}
            </Button>
          </form>
          
          <div className="mt-6 text-center text-sm text-gray-600">
            <p>⚠️ This portal is for system administrators only</p>
            <p>Contact your system administrator for the secret key</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
