# Hotel Employee Onboarding System - Frontend

## Overview

React/TypeScript frontend for the Hotel Employee Onboarding System, providing a comprehensive digital platform for managing employee onboarding with federal compliance (I-9, W-4 forms).

## Features

### Three-Phase Workflow
1. **Employee Phase**: Job application → Onboarding completion
2. **Manager Phase**: Application review → I-9 Section 2 verification
3. **HR Phase**: System oversight → Compliance monitoring

### Key Capabilities
- 📝 Digital job applications with QR code support
- 📋 Federal form compliance (I-9, W-4)
- 🌐 Bilingual support (English/Spanish)
- 📱 Mobile-responsive design
- 🔐 Role-based access control
- 📊 Real-time analytics dashboard
- 📧 Automated email notifications
- 🖊️ Digital signature capture

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + shadcn/ui
- **State Management**: React Context API
- **Form Handling**: React Hook Form + Zod
- **HTTP Client**: Axios
- **PDF Generation**: pdf-lib
- **Charts**: Recharts
- **Routing**: React Router v6

## Getting Started

### Prerequisites
- Node.js 20 LTS or higher
- npm (comes with Node.js)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd hotel-onboarding-frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**

Create `.env` file for development:
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
```

Create `.env.production` for production:
```bash
# API Configuration
VITE_API_URL=https://your-backend-api.herokuapp.com
VITE_APP_URL=https://your-frontend.vercel.app
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

The build output will be in the `dist` directory.

### Testing

Run tests:
```bash
npm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (shadcn/ui)
│   ├── forms/          # Form components
│   ├── job-application/# Job application components
│   └── onboarding/     # Onboarding flow components
├── contexts/           # React Context providers
├── hooks/              # Custom React hooks
├── pages/              # Page components
├── services/           # API services
├── utils/              # Utility functions
├── types/              # TypeScript type definitions
└── App.tsx            # Main application component
```

## Key Routes

- `/` - Home page
- `/login` - Login page (HR/Manager)
- `/apply/:propertyId` - Job application form
- `/onboard` - Employee onboarding portal
- `/manager` - Manager dashboard
- `/hr` - HR dashboard

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode

## Component Patterns

### Form Step Components
All onboarding form steps follow this pattern:
```typescript
interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}
```

### API Integration
Services use the centralized API client:
```typescript
import { apiClient } from '@/services/api'

const response = await apiClient.post('/endpoint', data)
```

## Environment Configuration

### Development
- API runs on http://localhost:8000
- Frontend runs on http://localhost:3000
- Hot Module Replacement (HMR) enabled

### Production
- Frontend deployed to Vercel
- Backend API on Heroku
- Static assets served via CDN

## Deployment

### Vercel Deployment

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
vercel --prod
```

### Important: SPA Routing Configuration

For single-page application routing to work on Vercel, ensure `vercel.json` exists:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check VITE_API_URL in environment variables
   - Ensure backend is running
   - Verify CORS configuration

2. **404 Errors on Routes**
   - Ensure vercel.json is configured for SPA routing
   - Check React Router configuration

3. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npx tsc --noEmit`

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please create an issue in the repository.