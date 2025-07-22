import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Hotel Employee Onboarding System
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Streamlined hiring and onboarding for hotel properties
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>HR Portal</CardTitle>
            <CardDescription>
              Manage properties, assign managers, and oversee all operations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/login?role=hr">
              <Button className="w-full">HR Login</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Manager Portal</CardTitle>
            <CardDescription>
              Review applications, manage employees, and approve documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/login?role=manager">
              <Button className="w-full">Manager Login</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Apply for Jobs</CardTitle>
            <CardDescription>
              Scan QR code at property or use direct link to apply
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/apply/demo">
              <Button variant="outline" className="w-full">Demo Application</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="mt-12 text-center">
        <h2 className="text-2xl font-semibold mb-4">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-4 max-w-6xl mx-auto">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
              <span className="text-blue-600 font-bold">1</span>
            </div>
            <h3 className="font-semibold">Scan QR Code</h3>
            <p className="text-sm text-gray-600">Candidates scan QR code at property</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
              <span className="text-blue-600 font-bold">2</span>
            </div>
            <h3 className="font-semibold">Submit Application</h3>
            <p className="text-sm text-gray-600">Fill out mobile-friendly application form</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
              <span className="text-blue-600 font-bold">3</span>
            </div>
            <h3 className="font-semibold">Manager Review</h3>
            <p className="text-sm text-gray-600">Manager reviews and approves applications</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-2">
              <span className="text-blue-600 font-bold">4</span>
            </div>
            <h3 className="font-semibold">Complete Onboarding</h3>
            <p className="text-sm text-gray-600">Employee completes documents with OCR assistance</p>
          </div>
        </div>
      </div>
    </div>
  )
}
