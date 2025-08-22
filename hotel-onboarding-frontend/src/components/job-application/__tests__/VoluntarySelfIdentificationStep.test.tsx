import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import VoluntarySelfIdentificationStep from '../VoluntarySelfIdentificationStep';

// Mock the translation hook
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock the enhanced components
jest.mock('@/components/ui/enhanced/StepCard', () => ({
  StepCard: ({ children, title, subtitle, ...props }: any) => (
    <div data-testid="step-card" {...props}>
      <h3>{title}</h3>
      {subtitle && <p>{subtitle}</p>}
      {children}
    </div>
  ),
}));

jest.mock('@/components/ui/enhanced/EnhancedSelect', () => ({
  EnhancedSelect: ({ name, label, value, onChange, options, ...props }: any) => (
    <div data-testid="enhanced-select">
      <label>{label}</label>
      <select 
        name={name} 
        value={value} 
        onChange={(e) => onChange(e.target.value)}
        aria-label={label}
      >
        <option value="">Select an option</option>
        {options?.map((opt: any) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  ),
}));

describe('VoluntarySelfIdentificationStep', () => {
  const defaultProps = {
    formData: {
      property_name: 'Test Hotel',
    },
    updateFormData: jest.fn(),
    validationErrors: {},
    onComplete: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all main sections correctly', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Check for main header
    expect(screen.getByText('Voluntary Self-Identification')).toBeInTheDocument();
    
    // Check for decline option
    expect(screen.getByText('I prefer not to provide any demographic information')).toBeInTheDocument();
    
    // Check for section cards when not declined
    expect(screen.getByText('Equal Employment Opportunity Information')).toBeInTheDocument();
    expect(screen.getByText('Veteran Status')).toBeInTheDocument();
    expect(screen.getByText('Disability Status')).toBeInTheDocument();
    expect(screen.getByText('How Did You Hear About Us?')).toBeInTheDocument();
  });

  it('marks step as complete on mount', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    expect(defaultProps.onComplete).toHaveBeenCalledWith(true);
  });

  it('hides demographic sections when decline is checked', async () => {
    const { rerender } = render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Initially sections should be visible
    expect(screen.getByText('Equal Employment Opportunity Information')).toBeInTheDocument();
    
    // Click decline checkbox
    const declineCheckbox = screen.getByRole('checkbox', { 
      name: /prefer not to provide any demographic information/i 
    });
    fireEvent.click(declineCheckbox);
    
    // Wait for update
    await waitFor(() => {
      expect(defaultProps.updateFormData).toHaveBeenCalledWith({
        decline_to_identify: true,
        race_ethnicity: '',
        gender: '',
        referral_source: ''
      });
    });
    
    // Rerender with declined state
    const updatedProps = {
      ...defaultProps,
      formData: {
        ...defaultProps.formData,
        decline_to_identify: true
      }
    };
    rerender(<VoluntarySelfIdentificationStep {...updatedProps} />);
    
    // Sections should be hidden
    expect(screen.queryByText('Equal Employment Opportunity Information')).not.toBeInTheDocument();
  });

  it('handles gender selection correctly', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Find and click male radio button
    const maleRadio = screen.getByRole('radio', { name: /male/i });
    fireEvent.click(maleRadio);
    
    expect(defaultProps.updateFormData).toHaveBeenCalledWith({
      gender: 'male'
    });
  });

  it('handles race/ethnicity checkbox selections', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Find and click a race checkbox
    const asianCheckbox = screen.getByRole('checkbox', { name: /asian/i });
    fireEvent.click(asianCheckbox);
    
    expect(defaultProps.updateFormData).toHaveBeenCalledWith({
      race_asian: true
    });
  });

  it('handles veteran status selection', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Find and click veteran status radio
    const notVeteranRadio = screen.getByRole('radio', { name: /not a protected veteran/i });
    fireEvent.click(notVeteranRadio);
    
    expect(defaultProps.updateFormData).toHaveBeenCalledWith({
      veteran_status: 'not_veteran'
    });
  });

  it('handles disability status selection', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Find and click disability status radio
    const noDisabilityRadio = screen.getByRole('radio', { 
      name: /no, i do not have a disability/i 
    });
    fireEvent.click(noDisabilityRadio);
    
    expect(defaultProps.updateFormData).toHaveBeenCalledWith({
      disability_status: 'no'
    });
  });

  it('displays privacy information when button is clicked', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Initially privacy details should not be visible
    expect(screen.queryByText('Privacy & Compliance Information')).not.toBeInTheDocument();
    
    // Click the help button
    const helpButton = screen.getByRole('button', { name: /privacy information/i });
    fireEvent.click(helpButton);
    
    // Privacy details should now be visible
    expect(screen.getByText('Privacy & Compliance Information')).toBeInTheDocument();
  });

  it('includes all required federal compliance language', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Check for key compliance phrases
    expect(screen.getByText(/equal opportunity employer/i)).toBeInTheDocument();
    expect(screen.getByText(/voluntary and confidential/i)).toBeInTheDocument();
    expect(screen.getByText(/will not affect your application/i)).toBeInTheDocument();
  });

  it('renders all race/ethnicity options with descriptions', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Check for federal race categories
    expect(screen.getByText('Hispanic or Latino')).toBeInTheDocument();
    expect(screen.getByText('White (Not Hispanic or Latino)')).toBeInTheDocument();
    expect(screen.getByText('Black or African American (Not Hispanic or Latino)')).toBeInTheDocument();
    expect(screen.getByText('Asian (Not Hispanic or Latino)')).toBeInTheDocument();
    expect(screen.getByText('American Indian or Alaska Native (Not Hispanic or Latino)')).toBeInTheDocument();
    expect(screen.getByText('Native Hawaiian or Other Pacific Islander (Not Hispanic or Latino)')).toBeInTheDocument();
    expect(screen.getByText('Two or More Races (Not Hispanic or Latino)')).toBeInTheDocument();
  });

  it('maintains accessibility standards', () => {
    render(<VoluntarySelfIdentificationStep {...defaultProps} />);
    
    // Check for proper ARIA labels
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toHaveAccessibleName();
    });
    
    const radioButtons = screen.getAllByRole('radio');
    radioButtons.forEach(radio => {
      expect(radio).toHaveAccessibleName();
    });
  });
});