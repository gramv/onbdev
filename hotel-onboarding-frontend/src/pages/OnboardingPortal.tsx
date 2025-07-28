import React from 'react'
import EnhancedOnboardingPortal from './EnhancedOnboardingPortal'

/**
 * OnboardingPortal - Simple wrapper component that redirects to the enhanced onboarding portal
 * This maintains backward compatibility while using the enhanced version
 */
const OnboardingPortal: React.FC = () => {
  return <EnhancedOnboardingPortal />
}

export default OnboardingPortal