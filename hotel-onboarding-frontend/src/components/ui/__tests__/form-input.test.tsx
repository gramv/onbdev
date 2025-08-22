import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormInput } from '../form-input'

describe('FormInput Component', () => {
  const defaultProps = {
    label: 'Test Label',
    id: 'test-input',
  }

  describe('Basic Rendering', () => {
    it('renders with label', () => {
      render(<FormInput {...defaultProps} />)
      expect(screen.getByText('Test Label')).toBeInTheDocument()
    })

    it('renders required asterisk when required', () => {
      render(<FormInput {...defaultProps} required />)
      expect(screen.getByText('*')).toBeInTheDocument()
    })

    it('renders with floating label by default', () => {
      render(<FormInput {...defaultProps} />)
      const label = screen.getByText('Test Label')
      expect(label).toHaveClass('absolute')
    })

    it('renders with static label when floatingLabel is false', () => {
      render(<FormInput {...defaultProps} floatingLabel={false} />)
      const label = screen.getByText('Test Label')
      expect(label).not.toHaveClass('absolute')
    })

    it('renders help text tooltip when provided', () => {
      render(<FormInput {...defaultProps} helpText="This is help text" />)
      const infoIcon = screen.getByRole('button')
      expect(infoIcon).toBeInTheDocument()
    })

    it('renders with custom icon', () => {
      const icon = <span data-testid="custom-icon">Icon</span>
      render(<FormInput {...defaultProps} icon={icon} />)
      expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
    })
  })

  describe('Validation States', () => {
    it('shows error message when error prop is provided and field is touched', () => {
      const { rerender } = render(<FormInput {...defaultProps} error="This is an error" />)
      
      // Error shouldn't show initially
      expect(screen.queryByText('This is an error')).not.toBeInTheDocument()
      
      // After blur (touching the field), error should show
      const input = screen.getByRole('textbox')
      fireEvent.blur(input)
      
      rerender(<FormInput {...defaultProps} error="This is an error" />)
      expect(screen.getByText('This is an error')).toBeInTheDocument()
    })

    it('shows success indicator when success prop is true', () => {
      render(<FormInput {...defaultProps} success />)
      const successIcon = document.querySelector('.text-green-500')
      expect(successIcon).toBeInTheDocument()
    })

    it('shows loading indicator when loading prop is true', () => {
      render(<FormInput {...defaultProps} loading />)
      const loadingIcon = document.querySelector('.animate-spin')
      expect(loadingIcon).toBeInTheDocument()
    })

    it('calls onValidate and shows validation error on blur', async () => {
      const onValidate = jest.fn().mockReturnValue('Validation error')
      render(<FormInput {...defaultProps} onValidate={onValidate} />)
      
      const input = screen.getByRole('textbox')
      await userEvent.type(input, 'test value')
      fireEvent.blur(input)
      
      expect(onValidate).toHaveBeenCalledWith('test value')
      await waitFor(() => {
        expect(screen.getByText('Validation error')).toBeInTheDocument()
      })
    })

    it('performs real-time validation after field is touched', async () => {
      const onValidate = jest.fn()
        .mockReturnValueOnce('Still invalid')
        .mockReturnValueOnce(null)
      
      render(<FormInput {...defaultProps} onValidate={onValidate} />)
      
      const input = screen.getByRole('textbox')
      
      // First blur to mark as touched
      await userEvent.type(input, 'bad')
      fireEvent.blur(input)
      
      // Now real-time validation should occur
      await userEvent.clear(input)
      await userEvent.type(input, 'good value')
      
      await waitFor(() => {
        expect(onValidate).toHaveBeenCalledTimes(3) // blur + 2 changes
      })
    })
  })

  describe('Auto-Formatting', () => {
    it('formats phone numbers correctly', async () => {
      const onChange = jest.fn()
      render(<FormInput {...defaultProps} autoFormat="phone" onChange={onChange} />)
      
      const input = screen.getByRole('textbox')
      await userEvent.type(input, '5551234567')
      
      expect(onChange).toHaveBeenLastCalledWith(
        expect.objectContaining({
          target: expect.objectContaining({
            value: '(555) 123-4567'
          })
        })
      )
    })

    it('formats SSN correctly', async () => {
      const onChange = jest.fn()
      render(<FormInput {...defaultProps} autoFormat="ssn" onChange={onChange} />)
      
      const input = screen.getByRole('textbox')
      await userEvent.type(input, '123456789')
      
      expect(onChange).toHaveBeenLastCalledWith(
        expect.objectContaining({
          target: expect.objectContaining({
            value: '123-45-6789'
          })
        })
      )
    })

    it('formats ZIP code correctly', async () => {
      const onChange = jest.fn()
      render(<FormInput {...defaultProps} autoFormat="zipcode" onChange={onChange} />)
      
      const input = screen.getByRole('textbox')
      await userEvent.type(input, '123456789')
      
      expect(onChange).toHaveBeenLastCalledWith(
        expect.objectContaining({
          target: expect.objectContaining({
            value: '12345-6789'
          })
        })
      )
    })
  })

  describe('Password Features', () => {
    it('toggles password visibility when showPasswordToggle is true', async () => {
      render(<FormInput {...defaultProps} type="password" showPasswordToggle />)
      
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('type', 'password')
      
      // Find and click the toggle button
      const toggleButton = screen.getByRole('button')
      await userEvent.click(toggleButton)
      
      expect(input).toHaveAttribute('type', 'text')
      
      await userEvent.click(toggleButton)
      expect(input).toHaveAttribute('type', 'password')
    })
  })

  describe('Accessibility', () => {
    it('has proper aria attributes for invalid state', () => {
      render(<FormInput {...defaultProps} error="Error message" />)
      
      const input = screen.getByRole('textbox')
      fireEvent.blur(input)
      
      expect(input).toHaveAttribute('aria-invalid', 'true')
      expect(input).toHaveAttribute('aria-describedby', 'test-input-error')
    })

    it('has proper aria attributes for help text', () => {
      render(<FormInput {...defaultProps} helpText="Help text" floatingLabel={false} />)
      
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-describedby', 'test-input-help')
    })

    it('maintains minimum touch target height for mobile', () => {
      render(<FormInput {...defaultProps} />)
      
      const input = screen.getByRole('textbox')
      expect(input).toHaveClass('min-h-[44px]')
      expect(input).toHaveClass('touch-manipulation')
    })
  })

  describe('Floating Label Behavior', () => {
    it('moves label up when input is focused', () => {
      render(<FormInput {...defaultProps} floatingLabel />)
      
      const label = screen.getByText('Test Label')
      const input = screen.getByRole('textbox')
      
      // Initially positioned in middle
      expect(label).toHaveClass('top-1/2')
      
      // Focus the input
      fireEvent.focus(input)
      
      // Label should move up
      expect(label).toHaveClass('top-0')
    })

    it('keeps label up when input has value', async () => {
      render(<FormInput {...defaultProps} floatingLabel value="existing value" />)
      
      const label = screen.getByText('Test Label')
      
      // Label should be up since there's a value
      expect(label).toHaveClass('top-0')
    })
  })

  describe('Event Handlers', () => {
    it('calls onChange handler with formatted value', async () => {
      const onChange = jest.fn()
      render(<FormInput {...defaultProps} onChange={onChange} />)
      
      const input = screen.getByRole('textbox')
      await userEvent.type(input, 'test')
      
      expect(onChange).toHaveBeenCalledTimes(4) // t-e-s-t
    })

    it('calls onBlur handler', () => {
      const onBlur = jest.fn()
      render(<FormInput {...defaultProps} onBlur={onBlur} />)
      
      const input = screen.getByRole('textbox')
      fireEvent.blur(input)
      
      expect(onBlur).toHaveBeenCalled()
    })
  })

  describe('Disabled State', () => {
    it('disables input when disabled prop is true', () => {
      render(<FormInput {...defaultProps} disabled />)
      
      const input = screen.getByRole('textbox')
      expect(input).toBeDisabled()
    })

    it('disables input when loading prop is true', () => {
      render(<FormInput {...defaultProps} loading />)
      
      const input = screen.getByRole('textbox')
      expect(input).toBeDisabled()
    })
  })
})