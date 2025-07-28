# Technology Stack

## Backend (FastAPI + Python)

- **Framework**: FastAPI with Python 3.12+
- **Package Manager**: Poetry
- **Data Storage**: In-memory dictionaries (development phase)
- **Authentication**: Simple token-based authentication
- **File Processing**: 
  - OCR: Groq AI for document processing (when needed)
  - PDF: PyPDF2, PyMuPDF, pdf2image
  - Images: Pillow
- **PDF Generation**: ReportLab
- **Environment**: python-dotenv for configuration

## Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router DOM v7
- **UI Components**: Radix UI primitives with custom components
- **Styling**: Tailwind CSS with tailwindcss-animate
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **State Management**: React Context (AuthContext)
- **Testing**: Jest with React Testing Library

## Development Tools

- **Linting**: ESLint with TypeScript support
- **Code Quality**: TypeScript strict mode
- **Package Management**: npm (frontend), Poetry (backend)

## Common Commands

### Backend
```bash
cd hotel-onboarding-backend
poetry install          # Install dependencies
poetry run python -m app.main  # Run development server
poetry add <package>     # Add new dependency
```

### Frontend
```bash
cd hotel-onboarding-frontend
npm install             # Install dependencies
npm run dev            # Start development server
npm run build          # Build for production
npm run test           # Run tests
npm run lint           # Run linter
```

## Environment Configuration

Backend uses `.env` file for:
- Groq API key for OCR processing
- Application secrets
- File storage configuration