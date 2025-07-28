import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface BreadcrumbItem {
  label: string
  path?: string
  icon?: React.ComponentType<{ className?: string }>
  ariaLabel?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  className?: string
  maxItems?: number
  showHomeIcon?: boolean
}

export function Breadcrumb({ 
  items, 
  className, 
  maxItems = 4,
  showHomeIcon = true 
}: BreadcrumbProps) {
  // Truncate items if too many for mobile
  const displayItems = items.length > maxItems 
    ? [items[0], { label: '...', path: undefined }, ...items.slice(-2)]
    : items

  return (
    <nav 
      className={cn(
        "flex items-center text-sm text-muted-foreground overflow-hidden",
        className
      )} 
      aria-label="Breadcrumb navigation"
    >
      <ol className="flex items-center min-w-0">
        {displayItems.map((item, index) => {
          const isLast = index === displayItems.length - 1
          const isEllipsis = item.label === '...'
          const Icon = item.icon

          return (
            <li key={index} className="flex items-center min-w-0">
              {index > 0 && (
                <ChevronRight 
                  className="h-4 w-4 mx-1 text-muted-foreground/50 flex-shrink-0" 
                  aria-hidden="true"
                />
              )}
              
              {isEllipsis ? (
                <span 
                  className="px-1 text-muted-foreground/70"
                  aria-label="More breadcrumb items"
                >
                  ...
                </span>
              ) : item.path && !isLast ? (
                <Link
                  to={item.path}
                  className={cn(
                    "flex items-center gap-1 hover:text-foreground transition-colors",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 rounded-sm",
                    "truncate min-w-0"
                  )}
                  aria-label={item.ariaLabel || `Navigate to ${item.label}`}
                >
                  {Icon && showHomeIcon && (
                    <Icon className="h-4 w-4 flex-shrink-0" />
                  )}
                  <span className="truncate">{item.label}</span>
                </Link>
              ) : (
                <span 
                  className={cn(
                    "flex items-center gap-1 min-w-0",
                    isLast ? "text-foreground font-medium" : "text-muted-foreground"
                  )}
                  aria-current={isLast ? "page" : undefined}
                >
                  {Icon && showHomeIcon && (
                    <Icon className="h-4 w-4 flex-shrink-0" />
                  )}
                  <span className="truncate">{item.label}</span>
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

// Convenience component for dashboard breadcrumbs
interface DashboardBreadcrumbProps {
  role: 'hr' | 'manager'
  currentSection: string
  className?: string
  propertyName?: string
}

export function DashboardBreadcrumb({ 
  role, 
  currentSection, 
  className,
  propertyName 
}: DashboardBreadcrumbProps) {
  const sectionLabels: Record<string, { label: string; description: string }> = {
    properties: { 
      label: 'Properties', 
      description: 'Manage hotel properties and locations' 
    },
    managers: { 
      label: 'Managers', 
      description: 'Manage property managers and assignments' 
    },
    employees: { 
      label: 'Employees', 
      description: 'View and manage employees' 
    },
    applications: { 
      label: 'Applications', 
      description: 'Review job applications' 
    },
    analytics: { 
      label: 'Analytics', 
      description: 'View system analytics and reports' 
    }
  }

  const sectionInfo = sectionLabels[currentSection] || { 
    label: currentSection, 
    description: `Navigate to ${currentSection}` 
  }

  const items: BreadcrumbItem[] = [
    {
      label: 'Home',
      path: '/',
      icon: Home,
      ariaLabel: 'Navigate to home page'
    },
    {
      label: role === 'hr' ? 'HR Dashboard' : 'Manager Dashboard',
      path: `/${role}`,
      ariaLabel: `Navigate to ${role === 'hr' ? 'HR' : 'Manager'} dashboard`
    }
  ]

  // Add property context for managers
  if (role === 'manager' && propertyName) {
    items.push({
      label: propertyName,
      ariaLabel: `Property: ${propertyName}`
    })
  }

  // Add current section
  items.push({
    label: sectionInfo.label,
    ariaLabel: sectionInfo.description
  })

  return <Breadcrumb items={items} className={className} />
}