# UI/UX Specification

This is the UI/UX specification for the spec detailed in @.agent-os/specs/2025-08-20-job-application-ux-improvements/spec.md

## Visual Design Requirements

### Layout Structure

#### Mobile Layout (< 640px)
- **Container**: Full width with 16px padding
- **Section Spacing**: 24px between card sections
- **Field Spacing**: 16px between form fields
- **All fields stack vertically** - no side-by-side fields
- **Navigation**: Fixed bottom bar with 3 buttons
- **Progress Bar**: Sticky top with simplified step dots

#### Tablet Layout (640px - 1024px)
- **Container**: Max-width 768px, centered
- **Section Spacing**: 32px between sections
- **Field Layout**: 2-column grid where appropriate
- **Navigation**: Inline at bottom of form

#### Desktop Layout (> 1024px)
- **Container**: Max-width 1024px, centered
- **Section Spacing**: 40px between sections
- **Field Layout**: 2-3 column grids for related fields
- **Navigation**: Inline with additional quick-save button

### Component Design

#### Input Fields
- **Height**: 44px minimum (11 Tailwind units)
- **Padding**: 12px horizontal, 10px vertical
- **Font Size**: 16px on mobile (prevents zoom), 14px desktop
- **Border**: 1px solid gray-300, 2px on focus
- **Border Radius**: 6px (rounded-md)
- **Background**: White, light gray on disabled
- **Icons**: 20px, positioned 12px from left

#### Buttons
- **Primary**: Blue-600 background, white text
- **Secondary**: White background, gray-700 border
- **Height**: 48px (12 Tailwind units)
- **Padding**: 24px horizontal
- **Font Weight**: 500 (medium)
- **Hover State**: Darken by 10%
- **Active State**: Scale 0.98
- **Disabled**: Opacity 50%

#### Cards
- **Background**: White
- **Border**: 1px solid gray-200
- **Shadow**: shadow-sm (0 1px 2px rgba(0,0,0,0.05))
- **Border Radius**: 8px (rounded-lg)
- **Padding**: 16px mobile, 24px desktop

### Color Palette

#### Primary Colors
- **Primary Blue**: #2563EB (blue-600)
- **Primary Hover**: #1D4ED8 (blue-700)
- **Primary Light**: #DBEAFE (blue-100)

#### Status Colors
- **Success Green**: #10B981 (green-500)
- **Success Background**: #D1FAE5 (green-100)
- **Error Red**: #EF4444 (red-500)
- **Error Background**: #FEE2E2 (red-100)
- **Warning Amber**: #F59E0B (amber-500)
- **Warning Background**: #FEF3C7 (amber-100)

#### Neutral Colors
- **Text Primary**: #111827 (gray-900)
- **Text Secondary**: #6B7280 (gray-500)
- **Border Default**: #E5E7EB (gray-300)
- **Background**: #F9FAFB (gray-50)

### Typography

#### Headings
- **Page Title**: 24px mobile, 30px desktop, font-bold
- **Section Title**: 18px mobile, 20px desktop, font-semibold
- **Subsection**: 16px, font-medium

#### Body Text
- **Base**: 14px mobile, 15px desktop
- **Small**: 12px mobile, 13px desktop
- **Line Height**: 1.5 for body, 1.2 for headings

#### Form Labels
- **Size**: 14px
- **Weight**: 500 (medium)
- **Color**: gray-700
- **Required Indicator**: Red asterisk, 12px

### Icons and Visual Elements

#### Section Icons
- **Size**: 24px in headers, 20px inline
- **Color**: Matches section theme color
- **Positioning**: Left of section title with 12px gap

#### Status Indicators
- **Checkmark**: Green-500, 20px, inside circle
- **Error**: Red-500, 16px, with shake animation
- **Info**: Blue-500, 16px, for tooltips
- **Loading**: Animated spinner, 20px

#### Progress Indicators
- **Progress Bar**: 12px height, blue-600 fill
- **Step Dots**: 32px diameter, numbered
- **Completed**: Green background, white checkmark
- **Current**: Blue background, white number
- **Upcoming**: Gray background, gray number

### Interactive States

#### Focus States
- **Input Fields**: 2px blue-500 border, blue-100 glow
- **Buttons**: 2px blue-500 outline with 2px offset
- **Links**: Underline on focus

#### Hover States
- **Buttons**: Darken background by 10%
- **Cards**: Slight shadow elevation
- **Links**: Underline appears
- **Step Indicators**: Slight scale (1.05)

#### Error States
- **Field Border**: 2px solid red-500
- **Background**: Light red-50 tint
- **Error Icon**: Red exclamation in circle
- **Error Message**: Red-600 text, 12px

#### Success States
- **Field Border**: 2px solid green-500
- **Checkmark Icon**: Green-500, right-aligned
- **Success Message**: Green-600 text

### Animations and Transitions

#### Transitions
- **Duration**: 200ms for most transitions
- **Easing**: ease-in-out
- **Properties**: background, border, transform

#### Animations
- **Shake**: For error attention (0.5s duration)
- **Fade In**: For success messages (0.3s)
- **Slide Down**: For expanding sections (0.3s)
- **Pulse**: For save indicator (1s infinite)

### Mobile-Specific UI

#### Touch Targets
- **Minimum Size**: 44x44px
- **Spacing**: 8px minimum between targets
- **Tap Highlight**: Light blue on touch

#### Scrolling
- **Smooth Scroll**: For navigation between sections
- **Momentum Scrolling**: iOS rubber-band effect
- **No Horizontal Scroll**: Strictly enforced

#### Mobile Navigation Bar
```
[Previous] [Save Draft] [Next/Submit]
```
- **Fixed Position**: Bottom of viewport
- **Background**: White with top border
- **Button Sizing**: Equal width, 44px height

### Accessibility Features

#### Color Contrast
- **Normal Text**: 4.5:1 minimum ratio
- **Large Text**: 3:1 minimum ratio
- **Interactive Elements**: 3:1 minimum

#### Focus Indicators
- **Visible Focus**: Never remove outline
- **Custom Focus**: 2px solid border
- **Skip Links**: Hidden but accessible

#### Screen Reader Support
- **ARIA Labels**: On all interactive elements
- **Error Announcements**: role="alert"
- **Progress Updates**: aria-live regions

### Loading and Skeleton States

#### Skeleton Components
- **Color**: Gray-200 background
- **Animation**: Shimmer effect left to right
- **Shape**: Match actual content shape

#### Loading Indicators
- **Inline Spinner**: For button actions
- **Full Page**: For initial load
- **Section Loader**: For lazy-loaded content

### Error Handling UI

#### Inline Errors
- **Position**: Below field
- **Icon**: 16px exclamation circle
- **Text**: 12px, red-600
- **Animation**: Fade in with shake

#### Error Summary
- **Position**: Top of form or section
- **Background**: Red-50 with red border
- **Icon**: Red exclamation triangle
- **Action**: Click to scroll to error

#### Network Errors
- **Toast Notification**: Bottom right
- **Retry Button**: Inline with error
- **Timeout**: 5 seconds auto-dismiss

### Success Feedback

#### Field Success
- **Checkmark**: Green, right-aligned in field
- **Border**: Brief green highlight

#### Step Completion
- **Animation**: Checkmark draws in
- **Progress Update**: Smooth fill animation
- **Sound**: Optional success chime

#### Form Submission
- **Full Screen**: Success message
- **Confetti**: Brief celebration animation
- **Next Steps**: Clear CTA buttons