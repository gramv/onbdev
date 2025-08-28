import { useState, useEffect } from 'react'

/**
 * Custom hook for debouncing a value.
 * Delays updating the debounced value until after the specified delay
 * has passed without the value changing.
 * 
 * @param value - The value to debounce
 * @param delay - The debounce delay in milliseconds
 * @returns The debounced value
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    // Set up a timer to update the debounced value after the delay
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // Clean up the timer if value changes before the delay is complete
    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}