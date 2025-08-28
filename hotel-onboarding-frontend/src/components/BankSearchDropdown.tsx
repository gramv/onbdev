import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Building, Search, Star, Check, AlertTriangle } from 'lucide-react'
import routingValidationService, { BankInfo } from '@/services/routingValidationService'
import { useDebounce } from '@/hooks/useDebounce'

interface BankSearchDropdownProps {
  value?: string
  onSelect: (bank: BankInfo) => void
  placeholder?: string
  label?: string
  error?: string
  required?: boolean
  disabled?: boolean
  className?: string
}

export default function BankSearchDropdown({
  value = '',
  onSelect,
  placeholder = 'Search for your bank...',
  label = 'Bank Name',
  error,
  required = false,
  disabled = false,
  className = ''
}: BankSearchDropdownProps) {
  const [searchTerm, setSearchTerm] = useState(value)
  const [isOpen, setIsOpen] = useState(false)
  const [searchResults, setSearchResults] = useState<BankInfo[]>([])
  const [popularBanks, setPopularBanks] = useState<BankInfo[]>([])
  const [selectedBank, setSelectedBank] = useState<BankInfo | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // Debounce search term
  const debouncedSearchTerm = useDebounce(searchTerm, 300)
  
  // Load popular banks on mount
  useEffect(() => {
    const popular = routingValidationService.getPopularBanks()
    setPopularBanks(popular)
  }, [])
  
  // Search banks when debounced search term changes
  useEffect(() => {
    if (debouncedSearchTerm && debouncedSearchTerm.length >= 2) {
      setIsSearching(true)
      const results = routingValidationService.searchBanksByName(debouncedSearchTerm)
      setSearchResults(results)
      setIsSearching(false)
    } else {
      setSearchResults([])
    }
  }, [debouncedSearchTerm])
  
  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
    setIsOpen(true)
    
    // Clear selection if user is typing
    if (selectedBank) {
      setSelectedBank(null)
    }
  }
  
  const handleBankSelect = (bank: BankInfo) => {
    setSelectedBank(bank)
    setSearchTerm(bank.bank_name)
    setIsOpen(false)
    onSelect(bank)
  }
  
  const getBankBadges = (bank: BankInfo) => {
    const badges = []
    
    if (bank.ach_supported && bank.wire_supported) {
      badges.push(
        <Badge key="all" variant="default" className="text-xs">
          ACH & Wire
        </Badge>
      )
    } else if (bank.ach_supported) {
      badges.push(
        <Badge key="ach" variant="secondary" className="text-xs">
          ACH Only
        </Badge>
      )
    } else if (bank.wire_supported) {
      badges.push(
        <Badge key="wire" variant="outline" className="text-xs">
          Wire Only
        </Badge>
      )
    }
    
    if (bank.bank_name.toLowerCase().includes('credit union')) {
      badges.push(
        <Badge key="cu" variant="outline" className="text-xs text-blue-600">
          Credit Union
        </Badge>
      )
    }
    
    return badges
  }
  
  const displayBanks = searchTerm.length >= 2 ? searchResults : popularBanks
  
  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {label && (
        <Label htmlFor="bank-search" className="text-sm mb-1">
          {label} {required && '*'}
        </Label>
      )}
      
      <div className="relative">
        <Input
          ref={inputRef}
          id="bank-search"
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          disabled={disabled}
          className={`pr-10 ${error ? 'border-red-500' : ''}`}
        />
        
        {selectedBank ? (
          <Check className="absolute right-3 top-3 h-4 w-4 text-green-600" />
        ) : (
          <Search className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
        )}
      </div>
      
      {error && (
        <p className="text-red-600 text-xs mt-1">{error}</p>
      )}
      
      {isOpen && !disabled && (
        <Card className="absolute z-50 w-full mt-1 p-2 shadow-lg">
          <ScrollArea className="max-h-60">
            {!searchTerm && (
              <div className="px-2 py-1 text-xs text-gray-500 font-medium">
                Popular Banks
              </div>
            )}
            
            {isSearching && (
              <div className="px-2 py-3 text-sm text-gray-500 text-center">
                Searching...
              </div>
            )}
            
            {!isSearching && displayBanks.length === 0 && searchTerm.length >= 2 && (
              <div className="px-2 py-3 text-sm text-gray-500 text-center">
                No banks found
              </div>
            )}
            
            {!isSearching && displayBanks.map((bank) => (
              <div
                key={bank.routing}
                className="flex items-start justify-between px-2 py-2 hover:bg-gray-50 cursor-pointer rounded"
                onClick={() => handleBankSelect(bank)}
              >
                <div className="flex items-start space-x-2">
                  <Building className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="text-sm font-medium">{bank.short_name || bank.bank_name}</div>
                    {bank.short_name && (
                      <div className="text-xs text-gray-500">{bank.bank_name}</div>
                    )}
                    <div className="text-xs text-gray-400">
                      Routing: {bank.routing} • {bank.state || 'USA'}
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end space-y-1">
                  {popularBanks.includes(bank) && (
                    <Star className="h-3 w-3 text-yellow-500 fill-yellow-500" />
                  )}
                  {getBankBadges(bank)}
                </div>
              </div>
            ))}
            
            {!searchTerm && (
              <div className="px-2 py-2 mt-2 border-t">
                <div className="text-xs text-gray-500">
                  Can't find your bank? Enter the routing number to detect it automatically.
                </div>
              </div>
            )}
          </ScrollArea>
        </Card>
      )}
    </div>
  )
}