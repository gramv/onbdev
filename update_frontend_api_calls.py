#!/usr/bin/env python3
"""
Update the frontend to use real backend API calls
"""
import re
import os

def update_enhanced_onboarding_portal():
    """Update EnhancedOnboardingPortal to use real API calls"""
    
    portal_path = "/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-frontend/src/pages/EnhancedOnboardingPortal.tsx"
    
    with open(portal_path, 'r') as f:
        content = f.read()
    
    # 1. Update verifyToken to use real API
    # Find the verifyToken function and replace the mock implementation
    verify_token_pattern = r"const verifyToken = async \(tokenToVerify = token\) => \{[\s\S]*?// Uncomment below for real backend integration:[\s\S]*?\*/"
    
    verify_token_replacement = """const verifyToken = async (tokenToVerify = token) => {
    try {
      setLoading(true)
      
      // Try to verify token with backend
      try {
        const response = await axios.get(`http://127.0.0.1:8000/onboard/verify?token=${tokenToVerify}`)
        
        if (response.data.success) {
          const onboardingData = response.data.data
          setOnboardingData(onboardingData)
          setLanguage(onboardingData.session.language_preference || 'en')
          
          // Load any saved progress from localStorage
          const savedSession = autoFillManager.getSessionData()
          if (savedSession.formData) {
            setFormData(savedSession.formData)
          }
          
          // Set current step index based on session data
          const stepIndex = ONBOARDING_STEPS.findIndex(step => step.id === onboardingData.session.current_step)
          if (stepIndex >= 0) {
            setCurrentStepIndex(stepIndex)
          }
        } else {
          setError(response.data.message || 'Invalid or expired onboarding link.')
        }
      } catch (apiError) {
        // Fallback to demo mode for testing if API fails
        if (tokenToVerify === 'test-token' || tokenToVerify === 'demo-token' || !token) {
          const mockOnboardingData = {
            valid: true,
            session: {
              id: 'test-session-1',
              status: 'in_progress',
              current_step: 'welcome',
              progress_percentage: 0,
              language_preference: 'en',
              expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
            },
            employee: {
              id: 'demo-emp-1',
              name: 'Demo Employee',
              email: 'demo.employee@hoteltest.com',
              position: 'Front Desk Agent',
              department: 'Guest Services',
              hire_date: new Date().toISOString(),
              personal_info: {}
            },
            property: {
              name: 'Grand Vista Hotel',
              address: '123 Main Street, Demo City, DC 12345'
            },
            onboarding_steps: ONBOARDING_STEPS.map(s => s.id)
          }
          
          setOnboardingData({
            session: mockOnboardingData.session,
            employee: mockOnboardingData.employee,
            property: mockOnboardingData.property,
            onboarding_steps: mockOnboardingData.onboarding_steps
          })
          setLanguage('en')
        } else {
          console.error('Token verification error:', apiError)
          setError('Unable to verify onboarding link. Please try again later.')
        }
      }"""
    
    # Replace the verifyToken function
    content = re.sub(verify_token_pattern, verify_token_replacement, content, flags=re.DOTALL)
    
    # 2. Update saveProgress to use real API
    # Find the saveProgress function
    save_progress_pattern = r"const saveProgress = async \(stepId: string, data\?: any\) => \{[\s\S]*?// Uncomment for real backend integration:[\s\S]*?\*/"
    
    save_progress_replacement = """const saveProgress = async (stepId: string, data?: any) => {
    if (!onboardingData) return
    
    try {
      // Save to backend
      const response = await axios.post('http://127.0.0.1:8000/onboard/update-progress', {
        token: token || 'demo-token',
        step: stepId,
        data: JSON.stringify(data || {}),
        signature_data: data?.signature ? JSON.stringify({
          signatureData: data.signature,
          timestamp: new Date().toISOString()
        }) : null
      })
      
      if (response.data.success) {
        // Update local state with new progress
        const updatedSession = response.data.data.session
        setOnboardingData(prev => prev ? {
          ...prev,
          session: updatedSession
        } : null)
      }
    } catch (error) {
      console.error('Failed to save progress:', error)
      // Still save to localStorage as backup
    }
    
    // Always save to localStorage
    autoFillManager.updateFormData(stepId, data)
    autoFillManager.updateProgress({
      currentStep: stepId,
      progressPercentage: Math.round(((currentStepIndex + 1) / ONBOARDING_STEPS.length) * 100)
    })
    
    // Update form data state
    setFormData(prev => ({
      ...prev,
      [stepId]: data
    }))"""
    
    # Replace the saveProgress function
    content = re.sub(save_progress_pattern, save_progress_replacement, content, flags=re.DOTALL)
    
    # 3. Update markStepComplete to use real API
    mark_complete_pattern = r"const markStepComplete = async \(stepId: string, data\?: any\) => \{[\s\S]*?\n  \}"
    
    # Find the existing markStepComplete and update it
    if "markStepComplete" in content:
        mark_complete_replacement = """const markStepComplete = async (stepId: string, data?: any) => {
    if (!onboardingData) return
    
    await saveProgress(stepId, data)
    
    // Move to next step
    const nextIndex = currentStepIndex + 1
    if (nextIndex < ONBOARDING_STEPS.length) {
      setCurrentStepIndex(nextIndex)
      
      // Submit step data to backend
      try {
        await axios.post(`http://127.0.0.1:8000/api/onboarding/${onboardingData.session.id}/step/${stepId}`, {
          form_data: data || {},
          signature_data: data?.signature ? {
            signatureData: data.signature,
            timestamp: new Date().toISOString()
          } : null
        })
      } catch (error) {
        console.error('Failed to submit step data:', error)
      }
    } else {
      // All steps completed - submit final completion
      try {
        const response = await axios.post(`http://127.0.0.1:8000/api/onboarding/${onboardingData.session.id}/complete`)
        if (response.data.success) {
          // Show completion message
          alert('Onboarding completed! Your information has been submitted for manager review.')
        }
      } catch (error) {
        console.error('Failed to complete onboarding:', error)
        alert('Failed to submit onboarding. Please try again.')
      }
    }
  }"""
        
        # Find and replace markStepComplete
        content = re.sub(mark_complete_pattern, mark_complete_replacement, content, flags=re.DOTALL)
    
    # Write back the updated content
    with open(portal_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated EnhancedOnboardingPortal.tsx with real API calls")
    print("   - Token verification now calls /onboard/verify")
    print("   - Progress saving now calls /onboard/update-progress")
    print("   - Step completion now calls /api/onboarding/{session_id}/step/{step_id}")
    print("   - Final completion now calls /api/onboarding/{session_id}/complete")
    print("   - Demo mode still works as fallback")

if __name__ == "__main__":
    update_enhanced_onboarding_portal()