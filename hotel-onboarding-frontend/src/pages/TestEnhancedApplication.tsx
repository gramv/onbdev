/**
 * Test page for enhanced job application form
 * This page allows testing of the improved UX features
 */

import React from 'react'
import { useParams } from 'react-router-dom'
import JobApplicationFormV2Enhanced from './JobApplicationFormV2.enhanced'

export default function TestEnhancedApplication() {
  const { propertyId } = useParams<{ propertyId?: string }>()
  
  // Use a test property ID if none provided
  const testPropertyId = propertyId || 'test-property-001'
  
  return (
    <div className="min-h-screen">
      <JobApplicationFormV2Enhanced />
    </div>
  )
}