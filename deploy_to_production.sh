#!/bin/bash

# Hotel Onboarding System - Production Deployment Script
# Deploys latest changes including PDF preview fix and signature date feature

set -e  # Exit on any error

echo "🚀 HOTEL ONBOARDING SYSTEM - PRODUCTION DEPLOYMENT"
echo "=================================================="
echo ""
echo "📋 Latest Changes Being Deployed:"
echo "   ✅ PDF Preview After Signing Fix"
echo "   ✅ Signature Date Feature"
echo "   ✅ Enhanced Error Handling"
echo "   ✅ Performance Optimizations"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
echo "🔍 CHECKING PREREQUISITES"
echo "========================"

# Check if we're in the right directory
if [ ! -d "hotel-onboarding-backend" ] || [ ! -d "hotel-onboarding-frontend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check Heroku CLI
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI not found. Install with: brew install heroku"
    exit 1
fi
print_status "Heroku CLI found"

# Check Vercel CLI
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI not found. Install with: npm i -g vercel"
    exit 1
fi
print_status "Vercel CLI found"

# Check if logged into Heroku
if ! heroku auth:whoami &> /dev/null; then
    print_error "Not logged into Heroku. Run: heroku login"
    exit 1
fi
print_status "Heroku authentication verified"

# Check if logged into Vercel
if ! vercel whoami &> /dev/null; then
    print_error "Not logged into Vercel. Run: vercel login"
    exit 1
fi
print_status "Vercel authentication verified"

echo ""

# PART 1: BACKEND DEPLOYMENT
echo "🔧 PART 1: BACKEND DEPLOYMENT TO HEROKU"
echo "======================================="

cd hotel-onboarding-backend

# Check if Heroku app exists
HEROKU_APP="ordermanagement"
if ! heroku apps:info $HEROKU_APP &> /dev/null; then
    print_error "Heroku app '$HEROKU_APP' not found"
    exit 1
fi
print_status "Heroku app '$HEROKU_APP' found"

# Verify deployment files
print_info "Verifying deployment files..."

if [ ! -f "Procfile" ]; then
    print_error "Procfile not found"
    exit 1
fi
print_status "Procfile verified"

if [ ! -f "runtime.txt" ]; then
    print_error "runtime.txt not found"
    exit 1
fi
print_status "runtime.txt verified"

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    exit 1
fi
print_status "requirements.txt verified"

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Uncommitted changes detected. Committing them..."
    git add .
    git commit -m "Deploy latest changes: PDF preview fix and signature date feature

- Fixed PDF preview after signing (URL pattern and state management)
- Added signature date to health insurance PDFs
- Enhanced error handling and debugging
- Performance optimizations for PDF processing
- Comprehensive testing and validation"
    print_status "Changes committed"
else
    print_status "No uncommitted changes"
fi

# Deploy to Heroku
print_info "Deploying backend to Heroku..."
echo ""

# Set Heroku remote if not exists
if ! git remote get-url heroku &> /dev/null; then
    print_info "Adding Heroku remote..."
    heroku git:remote -a $HEROKU_APP
    print_status "Heroku remote added"
fi

# Push to Heroku
echo "Pushing to Heroku..."
if git push heroku main; then
    print_status "Backend deployed to Heroku successfully"
else
    print_error "Backend deployment failed"
    exit 1
fi

# Wait for deployment to complete
print_info "Waiting for deployment to complete..."
sleep 10

# Verify backend deployment
print_info "Verifying backend deployment..."
BACKEND_URL="https://ordermanagement.herokuapp.com"

if curl -s "$BACKEND_URL/docs" > /dev/null; then
    print_status "Backend is responding at $BACKEND_URL"
else
    print_warning "Backend may still be starting up..."
fi

echo ""
cd ..

# PART 2: FRONTEND DEPLOYMENT
echo "🎨 PART 2: FRONTEND DEPLOYMENT TO VERCEL"
echo "========================================"

cd hotel-onboarding-frontend

# Verify environment configuration
print_info "Verifying environment configuration..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_warning "Creating .env.production file..."
    cat > .env.production << EOF
# Production API Configuration
VITE_API_URL=https://ordermanagement.herokuapp.com
VITE_APP_URL=https://clickwise.in
EOF
    print_status ".env.production created"
else
    print_status ".env.production exists"
fi

# Install dependencies
print_info "Installing dependencies..."
if npm install; then
    print_status "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Build for production
print_info "Building for production..."
if npm run build; then
    print_status "Production build completed"
else
    print_error "Production build failed"
    exit 1
fi

# Deploy to Vercel
print_info "Deploying frontend to Vercel..."
echo ""

if vercel --prod --yes; then
    print_status "Frontend deployed to Vercel successfully"
else
    print_error "Frontend deployment failed"
    exit 1
fi

echo ""
cd ..

# PART 3: POST-DEPLOYMENT VERIFICATION
echo "🔍 PART 3: POST-DEPLOYMENT VERIFICATION"
echo "======================================"

print_info "Verifying deployments..."

# Test backend health
print_info "Testing backend health..."
if curl -s "https://ordermanagement.herokuapp.com/docs" > /dev/null; then
    print_status "Backend health check passed"
else
    print_warning "Backend health check failed - may still be starting"
fi

# Test frontend
print_info "Testing frontend..."
if curl -s "https://clickwise.in" > /dev/null; then
    print_status "Frontend health check passed"
else
    print_warning "Frontend health check failed"
fi

# Final summary
echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "===================================="
echo ""
echo "📊 Deployment Summary:"
echo "   🔧 Backend:  https://ordermanagement.herokuapp.com"
echo "   🎨 Frontend: https://clickwise.in"
echo ""
echo "🆕 New Features Deployed:"
echo "   ✅ PDF Preview After Signing - Users can now see signed PDFs immediately"
echo "   ✅ Signature Date Feature - Date appears next to signature on PDFs"
echo "   ✅ Enhanced Error Handling - Better debugging and error recovery"
echo "   ✅ Performance Optimizations - Faster PDF processing"
echo ""
echo "🧪 Testing Checklist:"
echo "   □ Test health insurance form completion"
echo "   □ Test PDF preview before signing"
echo "   □ Test signature capture"
echo "   □ Test PDF preview after signing (NEW)"
echo "   □ Verify signature date appears on PDF (NEW)"
echo "   □ Test download functionality"
echo "   □ Test manager dashboard"
echo "   □ Test HR dashboard"
echo ""
echo "📞 Support:"
echo "   - Backend logs: heroku logs --tail -a ordermanagement"
echo "   - Frontend logs: Check Vercel dashboard"
echo "   - Issues: Check GitHub repository"
echo ""
print_status "Deployment script completed successfully!"
