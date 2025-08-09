# Technical Stack

## Backend
FastAPI 0.116.1
PostgreSQL via Supabase
Python 3.12+
Uvicorn ASGI server
SQLAlchemy with Supabase client
JWT authentication
Pydantic V2 validation
ReportLab + PyPDF2 for PDF generation
PyMuPDF for PDF manipulation
Groq API for OCR processing
aiosmtplib for email notifications

## Frontend
React 18.3.1
TypeScript 5.6.2
Vite 6.0.1
npm package manager
React Router v7.7.0
React Hook Form 7.60.0
Zod 4.0.5 validation
Axios 1.10.0 HTTP client
pdf-lib 1.17.1 for client-side PDF
React Signature Canvas 1.1.0

## UI/Styling
Tailwind CSS 3.4.16
Radix UI primitives
Lucide React icons
System fonts
Mobile-first responsive design
Light/Dark mode support via next-themes

## Testing
pytest for backend
Jest 30.0.5 for frontend
React Testing Library 16.3.0
80% coverage target for critical paths

## Development Tools
Git version control
ESLint + Prettier
Black for Python formatting
TypeScript strict mode
Husky pre-commit hooks

## Deployment & Infrastructure
Test Database: Supabase (kzommszdhapvqpekpvnt.supabase.co)
Production Database: Supabase (separate instance)
File Storage: Supabase Storage
Environment Management: .env files
Docker-ready architecture
Gunicorn for production

## Security & Compliance
HTTPS required
CORS configured for frontend
JWT tokens with 72-hour expiry
Field-level encryption for PII
ESIGN Act compliant signatures
I-9 and W-4 federal compliance

## Performance Targets
API Response: <200ms average
Page Load: <3s on 3G
Concurrent Users: 50+ for MVP
Database Connections: Pool of 20
PDF Generation: <5s per document

## External Services
Groq API for document OCR
SMTP (Gmail) for email notifications
Supabase for database and storage

## Code Repository
https://github.com/[to-be-configured]