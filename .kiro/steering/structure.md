# Project Structure

## Root Level Organization

```
├── hotel-onboarding-backend/    # FastAPI backend application
├── hotel-onboarding-frontend/   # React frontend application
├── official-forms/              # PDF templates (for future use)
├── .kiro/                      # Kiro IDE configuration and specs
└── testing files              # Test reports and checklists
```

## Backend Structure (`hotel-onboarding-backend/`)

```
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── main_enhanced.py     # Enhanced version with additional features
│   ├── models.py            # Pydantic data models
│   ├── auth.py              # Authentication utilities
│   └── pdf_forms.py         # PDF form processing
├── tests/                   # Test files
├── pyproject.toml          # Poetry dependencies
├── .env                    # Environment variables
└── setup scripts          # Database and test data setup
```

## Frontend Structure (`hotel-onboarding-frontend/`)

```
├── src/
│   ├── components/
│   │   ├── ui/             # Reusable UI components (Radix-based)
│   │   └── form components # Specialized form components
│   ├── pages/              # Route-level page components (HR/Manager dashboards)
│   ├── contexts/           # React contexts (AuthContext)
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── assets/             # Static assets
│   └── __tests__/          # Component tests
├── public/                 # Static files
└── config files           # Vite, TypeScript, Tailwind configs
```

## Key Architectural Patterns

### Backend Patterns
- **In-memory database**: Uses Python dictionaries for data storage (development phase)
- **Role-based access**: HR vs Manager permissions determine API access
- **Application workflow**: Submit → Review → Approve/Reject → Track status
- **Token-based auth**: Simple token system for user sessions

### Frontend Patterns
- **Context providers**: AuthContext for global authentication state
- **Component composition**: UI components built with Radix primitives
- **Form handling**: React Hook Form with Zod validation
- **Route protection**: Role-based dashboard access (HR vs Manager)
- **Dashboard architecture**: Tab-based navigation for different data views

### File Naming Conventions
- **Components**: PascalCase (e.g., `JobApplicationForm.tsx`)
- **Pages**: PascalCase with "Page" suffix (e.g., `LoginPage.tsx`)
- **Utilities**: camelCase (e.g., `utils.ts`)
- **Contexts**: PascalCase with "Context" suffix (e.g., `AuthContext.tsx`)
- **Dashboards**: PascalCase with "Dashboard" suffix (e.g., `HRDashboard.tsx`)

### Import Organization
- External libraries first
- Internal components/utilities second
- Relative imports last
- Group related imports together