import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import axios from 'axios'

interface Property {
  id: string
  name: string
  address: string
  qr_code_url: string
}

interface Manager {
  id: string
  email: string
  property_id: string
}

export default function HRDashboard() {
  const { user, logout } = useAuth()
  const [properties, setProperties] = useState<Property[]>([])
  const [managers, setManagers] = useState<Manager[]>([])
  const [newProperty, setNewProperty] = useState({ name: '', address: '' })
  const [newManager, setNewManager] = useState({ email: '', password: '', property_id: '' })

  useEffect(() => {
    fetchProperties()
    fetchManagers()
  }, [])

  const fetchProperties = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/hr/properties')
      setProperties(response.data)
    } catch (error) {
      console.error('Failed to fetch properties:', error)
    }
  }

  const fetchManagers = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/hr/managers')
      setManagers(response.data)
    } catch (error) {
      console.error('Failed to fetch managers:', error)
    }
  }

  const createProperty = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await axios.post('http://127.0.0.1:8000/hr/properties', newProperty)
      setNewProperty({ name: '', address: '' })
      fetchProperties()
    } catch (error) {
      console.error('Failed to create property:', error)
    }
  }

  const assignManager = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await axios.post('http://127.0.0.1:8000/hr/assign-manager', newManager)
      setNewManager({ email: '', password: '', property_id: '' })
      fetchManagers()
    } catch (error) {
      console.error('Failed to assign manager:', error)
    }
  }

  if (user?.role !== 'hr') {
    return <div>Access denied. HR role required.</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">HR Dashboard</h1>
        <Button onClick={logout} variant="outline">Logout</Button>
      </div>

      <Tabs defaultValue="properties" className="space-y-6">
        <TabsList>
          <TabsTrigger value="properties">Properties</TabsTrigger>
          <TabsTrigger value="managers">Managers</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="properties" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Create New Property</CardTitle>
              <CardDescription>Add a new hotel property to the system</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createProperty} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="property-name">Property Name</Label>
                    <Input
                      id="property-name"
                      value={newProperty.name}
                      onChange={(e) => setNewProperty({ ...newProperty, name: e.target.value })}
                      placeholder="Hotel Name"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="property-address">Address</Label>
                    <Input
                      id="property-address"
                      value={newProperty.address}
                      onChange={(e) => setNewProperty({ ...newProperty, address: e.target.value })}
                      placeholder="Full Address"
                      required
                    />
                  </div>
                </div>
                <Button type="submit">Create Property</Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Existing Properties</CardTitle>
              <CardDescription>Manage your hotel properties</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {properties.map((property) => (
                  <div key={property.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">{property.name}</h3>
                      <p className="text-sm text-gray-600">{property.address}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary">QR Code Available</Badge>
                      <Button size="sm" variant="outline">View QR</Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="managers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Assign Manager</CardTitle>
              <CardDescription>Assign a manager to a property</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={assignManager} className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="manager-email">Manager Email</Label>
                    <Input
                      id="manager-email"
                      type="email"
                      value={newManager.email}
                      onChange={(e) => setNewManager({ ...newManager, email: e.target.value })}
                      placeholder="manager@hotel.com"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="manager-password">Password</Label>
                    <Input
                      id="manager-password"
                      type="password"
                      value={newManager.password}
                      onChange={(e) => setNewManager({ ...newManager, password: e.target.value })}
                      placeholder="Temporary password"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="property-select">Property</Label>
                    <Select value={newManager.property_id} onValueChange={(value) => setNewManager({ ...newManager, property_id: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select property" />
                      </SelectTrigger>
                      <SelectContent>
                        {properties.map((property) => (
                          <SelectItem key={property.id} value={property.id}>
                            {property.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button type="submit">Assign Manager</Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Current Managers</CardTitle>
              <CardDescription>View all assigned managers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {managers.map((manager) => {
                  const property = properties.find(p => p.id === manager.property_id)
                  return (
                    <div key={manager.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h3 className="font-semibold">{manager.email}</h3>
                        <p className="text-sm text-gray-600">{property?.name || 'Unknown Property'}</p>
                      </div>
                      <Badge variant="outline">Active</Badge>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle>System Analytics</CardTitle>
              <CardDescription>Overview of system usage and metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <h3 className="text-2xl font-bold">{properties.length}</h3>
                  <p className="text-sm text-gray-600">Total Properties</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <h3 className="text-2xl font-bold">{managers.length}</h3>
                  <p className="text-sm text-gray-600">Active Managers</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <h3 className="text-2xl font-bold">0</h3>
                  <p className="text-sm text-gray-600">Pending Applications</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
