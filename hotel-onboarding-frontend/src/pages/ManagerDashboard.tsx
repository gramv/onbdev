import React, { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import axios from 'axios'

interface Application {
  id: string
  applicant_data: {
    first_name: string
    last_name: string
    email: string
    phone: string
    department: string
    position: string
    experience: string
    availability: string
  }
  status: string
  created_at: string
}

interface Employee {
  id: string
  user_id: string
  hire_date: string
  department: string
  status: string
}

export default function ManagerDashboard() {
  const { user, logout } = useAuth()
  const [applications, setApplications] = useState<Application[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null)
  const [approvalData, setApprovalData] = useState({
    job_title: '',
    start_date: '',
    start_time: '',
    pay_rate: '',
    pay_frequency: 'bi-weekly',
    benefits_eligible: 'yes',
    direct_supervisor: '',
    special_instructions: ''
  })

  useEffect(() => {
    fetchApplications()
    fetchEmployees()
  }, [])

  const fetchApplications = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/applications')
      setApplications(response.data)
    } catch (error) {
      console.error('Failed to fetch applications:', error)
    }
  }

  const fetchEmployees = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/manager/employees')
      setEmployees(response.data)
    } catch (error) {
      console.error('Failed to fetch employees:', error)
    }
  }

  const approveApplication = async () => {
    if (!selectedApplication) return
    
    try {
      await axios.post(`http://127.0.0.1:8000/applications/${selectedApplication.id}/approve`, approvalData)
      fetchApplications()
      setSelectedApplication(null)
      setApprovalData({
        job_title: '',
        start_date: '',
        start_time: '',
        pay_rate: '',
        pay_frequency: 'bi-weekly',
        benefits_eligible: 'yes',
        direct_supervisor: '',
        special_instructions: ''
      })
    } catch (error) {
      console.error('Failed to approve application:', error)
    }
  }

  const rejectApplication = async (applicationId: string) => {
    try {
      await axios.post(`http://127.0.0.1:8000/applications/${applicationId}/reject`)
      fetchApplications()
    } catch (error) {
      console.error('Failed to reject application:', error)
    }
  }

  if (user?.role !== 'manager') {
    return <div>Access denied. Manager role required.</div>
  }

  const pendingApplications = applications.filter(app => app.status === 'pending')
  const departments = [...new Set(applications.map(app => app.applicant_data.department))]

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Manager Dashboard</h1>
        <Button onClick={logout} variant="outline">Logout</Button>
      </div>

      <Tabs defaultValue="applications" className="space-y-6">
        <TabsList>
          <TabsTrigger value="applications">
            Applications 
            {pendingApplications.length > 0 && (
              <Badge className="ml-2">{pendingApplications.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="employees">Employees</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        <TabsContent value="applications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Pending Applications</CardTitle>
              <CardDescription>Review and approve job applications</CardDescription>
            </CardHeader>
            <CardContent>
              {departments.map(department => {
                const deptApplications = pendingApplications.filter(app => app.applicant_data.department === department)
                if (deptApplications.length === 0) return null

                return (
                  <div key={department} className="mb-6">
                    <h3 className="text-lg font-semibold mb-3">{department}</h3>
                    <div className="grid gap-4">
                      {deptApplications.map((application) => (
                        <div key={application.id} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-semibold">
                                {application.applicant_data.first_name} {application.applicant_data.last_name}
                              </h4>
                              <p className="text-sm text-gray-600">{application.applicant_data.position}</p>
                              <p className="text-sm text-gray-600">{application.applicant_data.email}</p>
                              <p className="text-sm text-gray-600">Experience: {application.applicant_data.experience}</p>
                              <p className="text-sm text-gray-500">Applied: {new Date(application.created_at).toLocaleDateString()}</p>
                            </div>
                            <div className="flex space-x-2">
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button 
                                    size="sm" 
                                    onClick={() => {
                                      setSelectedApplication(application)
                                      setApprovalData({
                                        ...approvalData,
                                        job_title: application.applicant_data.position
                                      })
                                    }}
                                  >
                                    Approve
                                  </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-2xl">
                                  <DialogHeader>
                                    <DialogTitle>Approve Application</DialogTitle>
                                    <DialogDescription>
                                      Set job details for {application.applicant_data.first_name} {application.applicant_data.last_name}
                                    </DialogDescription>
                                  </DialogHeader>
                                  <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                      <Label htmlFor="job_title">Job Title</Label>
                                      <Input
                                        id="job_title"
                                        value={approvalData.job_title}
                                        onChange={(e) => setApprovalData({...approvalData, job_title: e.target.value})}
                                      />
                                    </div>
                                    <div className="space-y-2">
                                      <Label htmlFor="start_date">Start Date</Label>
                                      <Input
                                        id="start_date"
                                        type="date"
                                        value={approvalData.start_date}
                                        onChange={(e) => setApprovalData({...approvalData, start_date: e.target.value})}
                                      />
                                    </div>
                                    <div className="space-y-2">
                                      <Label htmlFor="start_time">Start Time</Label>
                                      <Input
                                        id="start_time"
                                        type="time"
                                        value={approvalData.start_time}
                                        onChange={(e) => setApprovalData({...approvalData, start_time: e.target.value})}
                                      />
                                    </div>
                                    <div className="space-y-2">
                                      <Label htmlFor="pay_rate">Pay Rate ($/hour)</Label>
                                      <Input
                                        id="pay_rate"
                                        type="number"
                                        step="0.01"
                                        value={approvalData.pay_rate}
                                        onChange={(e) => setApprovalData({...approvalData, pay_rate: e.target.value})}
                                      />
                                    </div>
                                    <div className="space-y-2">
                                      <Label htmlFor="pay_frequency">Pay Frequency</Label>
                                      <Select value={approvalData.pay_frequency} onValueChange={(value) => setApprovalData({...approvalData, pay_frequency: value})}>
                                        <SelectTrigger>
                                          <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                          <SelectItem value="weekly">Weekly</SelectItem>
                                          <SelectItem value="bi-weekly">Bi-weekly</SelectItem>
                                          <SelectItem value="monthly">Monthly</SelectItem>
                                        </SelectContent>
                                      </Select>
                                    </div>
                                    <div className="space-y-2">
                                      <Label htmlFor="direct_supervisor">Direct Supervisor</Label>
                                      <Input
                                        id="direct_supervisor"
                                        value={approvalData.direct_supervisor}
                                        onChange={(e) => setApprovalData({...approvalData, direct_supervisor: e.target.value})}
                                      />
                                    </div>
                                    <div className="col-span-2 space-y-2">
                                      <Label htmlFor="special_instructions">Special Instructions</Label>
                                      <Textarea
                                        id="special_instructions"
                                        value={approvalData.special_instructions}
                                        onChange={(e) => setApprovalData({...approvalData, special_instructions: e.target.value})}
                                        rows={3}
                                      />
                                    </div>
                                  </div>
                                  <div className="flex justify-end space-x-2">
                                    <Button variant="outline" onClick={() => setSelectedApplication(null)}>Cancel</Button>
                                    <Button onClick={approveApplication}>Send Onboarding Email</Button>
                                  </div>
                                </DialogContent>
                              </Dialog>
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => rejectApplication(application.id)}
                              >
                                Reject
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
              
              {pendingApplications.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No pending applications
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="employees">
          <Card>
            <CardHeader>
              <CardTitle>Current Employees</CardTitle>
              <CardDescription>Manage your property's employees</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {employees.map((employee) => (
                  <div key={employee.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h3 className="font-semibold">Employee #{employee.id}</h3>
                      <p className="text-sm text-gray-600">{employee.department}</p>
                      <p className="text-sm text-gray-600">Hired: {new Date(employee.hire_date).toLocaleDateString()}</p>
                    </div>
                    <Badge variant={employee.status === 'active' ? 'default' : 'secondary'}>
                      {employee.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Document Reviews</CardTitle>
              <CardDescription>Review employee onboarding documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                No documents pending review
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
