import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PersonalInformationStep from '../PersonalInformationStep.enhanced'
import { I18nextProvider } from 'react-i18next'
import i18n from '@/i18n/i18n'

describe('PersonalInformationStep Enhanced', () => {
  const mockUpdateFormData = jest.fn()
  const mockOnComplete = jest.fn()
  
  const defaultProps = {
    formData: {
      first_name: '',
      middle_name: '',
      last_name: '',
      email: '',
      phone: '',
      phone_is_cell: false,
      phone_is_home: false,
      address: '',
      apartment_unit: '',
      city: '',
      state: '',
      zip_code: '',
      age_verification: false,
      work_authorized: '',
      sponsorship_required: '',
      reliable_transportation: '',
      transportation_method: '',
      transportation_other: ''
    },
    updateFormData: mockUpdateFormData,
    validationErrors: {},
    onComplete: mockOnComplete
  }

  const renderComponent = (props = {}) => {
    return render(
      <I18nextProvider i18n={i18n}>
        <PersonalInformationStep {...defaultProps} {...props} />
      </I18nextProvider>
    )
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Card-Based Layout', () => {
    it('renders personal information in a card with icon', () => {
      renderComponent()
      
      // Check for card structure
      const cards = screen.getAllByRole('article')
      expect(cards.length).toBeGreaterThan(0)
      
      // Check for section headers with icons
      expect(screen.getByText(/personal information/i)).toBeInTheDocument()
    })

    it('renders contact information in a separate card', () => {
      renderComponent()
      
      expect(screen.getByText(/contact information/i)).toBeInTheDocument()
    })

    it('renders eligibility information in a separate card', () => {
      renderComponent()
      
      expect(screen.getByText(/eligibility/i)).toBeInTheDocument()
    })
  })

  describe('FormInput Integration', () => {
    it('uses FormInput component for text fields with floating labels', () => {
      renderComponent()
      
      const firstNameInput = screen.getByLabelText(/first name/i)
      expect(firstNameInput).toBeInTheDocument()
      expect(firstNameInput).toHaveClass('min-h-[44px]') // Mobile touch target
    })

    it('shows real-time validation on blur', async () => {
      renderComponent()
      
      const emailInput = screen.getByLabelText(/email/i)
      await userEvent.type(emailInput, 'invalid-email')
      fireEvent.blur(emailInput)
      
      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument()
      })
    })

    it('shows success indicator for valid fields', async () => {
      renderComponent()
      
      const emailInput = screen.getByLabelText(/email/i)
      await userEvent.type(emailInput, 'valid@email.com')
      fireEvent.blur(emailInput)
      
      await waitFor(() => {
        const successIcon = document.querySelector('.text-green-500')
        expect(successIcon).toBeInTheDocument()
      })
    })

    it('auto-formats phone numbers', async () => {
      renderComponent()
      
      const phoneInput = screen.getByLabelText(/phone/i)
      await userEvent.type(phoneInput, '5551234567')
      
      expect(phoneInput).toHaveValue('(555) 123-4567')
    })

    it('auto-formats ZIP codes', async () => {
      renderComponent()
      
      const zipInput = screen.getByLabelText(/zip code/i)
      await userEvent.type(zipInput, '123456789')
      
      expect(zipInput).toHaveValue('12345-6789')
    })
  })

  describe('Mobile Responsiveness', () => {
    it('applies mobile-first grid layouts', () => {
      renderComponent()
      
      const container = screen.getByTestId('personal-info-step')
      expect(container).toHaveClass('space-y-6')
      
      // Check for responsive grid classes
      const grids = container.querySelectorAll('[class*="grid-cols"]')
      expect(grids.length).toBeGreaterThan(0)
    })

    it('ensures minimum touch target size of 44px', () => {
      renderComponent()
      
      const inputs = screen.getAllByRole('textbox')
      inputs.forEach(input => {
        expect(input).toHaveClass('min-h-[44px]')
        expect(input).toHaveClass('touch-manipulation')
      })
    })

    it('stacks form fields vertically on mobile', () => {
      renderComponent()
      
      const nameSection = screen.getByTestId('name-section')
      expect(nameSection).toHaveClass('grid-cols-1')
      expect(nameSection).toHaveClass('md:grid-cols-3')
    })
  })

  describe('Visual Feedback', () => {
    it('shows error state with red border and icon', async () => {
      renderComponent()
      
      const emailInput = screen.getByLabelText(/email/i)
      await userEvent.type(emailInput, 'bad')
      fireEvent.blur(emailInput)
      
      await waitFor(() => {
        expect(emailInput).toHaveClass('border-destructive')
        const errorIcon = document.querySelector('.text-destructive')
        expect(errorIcon).toBeInTheDocument()
      })
    })

    it('shows loading state when validating', () => {
      const formDataWithLoading = {
        ...defaultProps.formData,
        _loading_email: true
      }
      
      renderComponent({ formData: formDataWithLoading })
      
      const loadingIcon = document.querySelector('.animate-spin')
      expect(loadingIcon).toBeInTheDocument()
    })

    it('displays help text with info icon', () => {
      renderComponent()
      
      // Transportation method should have help text
      const helpIcons = document.querySelectorAll('[data-testid="help-icon"]')
      expect(helpIcons.length).toBeGreaterThan(0)
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels for all inputs', () => {
      renderComponent()
      
      const inputs = screen.getAllByRole('textbox')
      inputs.forEach(input => {
        expect(input).toHaveAttribute('aria-invalid')
      })
    })

    it('announces errors to screen readers', async () => {
      renderComponent()
      
      const emailInput = screen.getByLabelText(/email/i)
      await userEvent.type(emailInput, 'bad')
      fireEvent.blur(emailInput)
      
      await waitFor(() => {
        const error = screen.getByText(/please enter a valid email/i)
        expect(error).toHaveAttribute('role', 'alert')
      })
    })

    it('maintains proper focus order', async () => {
      renderComponent()
      
      const firstNameInput = screen.getByLabelText(/first name/i)
      const lastNameInput = screen.getByLabelText(/last name/i)
      
      firstNameInput.focus()
      await userEvent.tab()
      
      expect(document.activeElement).toBe(screen.getByLabelText(/middle name/i))
    })
  })

  describe('Form Completion', () => {
    it('marks step complete when all required fields are filled', async () => {
      const completeFormData = {
        ...defaultProps.formData,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '(555) 123-4567',
        phone_is_cell: true,
        address: '123 Main St',
        city: 'New York',
        state: 'NY',
        zip_code: '10001',
        age_verification: true,
        work_authorized: 'yes',
        sponsorship_required: 'no',
        reliable_transportation: 'yes',
        transportation_method: 'car'
      }
      
      renderComponent({ formData: completeFormData })
      
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(true)
      })
    })

    it('marks step incomplete when required fields are missing', () => {
      renderComponent()
      
      expect(mockOnComplete).toHaveBeenCalledWith(false)
    })
  })

  describe('Conditional Fields', () => {
    it('shows transportation method when reliable transportation is yes', async () => {
      renderComponent()
      
      const transportYes = screen.getByLabelText(/yes.*reliable transportation/i)
      await userEvent.click(transportYes)
      
      await waitFor(() => {
        expect(screen.getByLabelText(/transportation method/i)).toBeInTheDocument()
      })
    })

    it('hides transportation method when reliable transportation is no', async () => {
      const formData = {
        ...defaultProps.formData,
        reliable_transportation: 'yes',
        transportation_method: 'car'
      }
      
      const { rerender } = renderComponent({ formData })
      
      // Should be visible initially
      expect(screen.getByLabelText(/transportation method/i)).toBeInTheDocument()
      
      // Change to no
      const transportNo = screen.getByLabelText(/no.*reliable transportation/i)
      await userEvent.click(transportNo)
      
      rerender(
        <I18nextProvider i18n={i18n}>
          <PersonalInformationStep 
            {...defaultProps} 
            formData={{ ...formData, reliable_transportation: 'no' }}
          />
        </I18nextProvider>
      )
      
      await waitFor(() => {
        expect(screen.queryByLabelText(/transportation method/i)).not.toBeInTheDocument()
      })
    })

    it('shows other field when transportation method is other', async () => {
      const formData = {
        ...defaultProps.formData,
        reliable_transportation: 'yes'
      }
      
      renderComponent({ formData })
      
      const methodSelect = screen.getByLabelText(/transportation method/i)
      await userEvent.selectOptions(methodSelect, 'other')
      
      await waitFor(() => {
        expect(screen.getByLabelText(/please specify/i)).toBeInTheDocument()
      })
    })
  })

  describe('Section Icons', () => {
    it('displays User icon for personal information section', () => {
      renderComponent()
      
      const userIcon = document.querySelector('[data-testid="user-icon"]')
      expect(userIcon).toBeInTheDocument()
    })

    it('displays Mail icon for contact section', () => {
      renderComponent()
      
      const mailIcon = document.querySelector('[data-testid="mail-icon"]')
      expect(mailIcon).toBeInTheDocument()
    })

    it('displays MapPin icon for address section', () => {
      renderComponent()
      
      const mapIcon = document.querySelector('[data-testid="map-icon"]')
      expect(mapIcon).toBeInTheDocument()
    })
  })
})