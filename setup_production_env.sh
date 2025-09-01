#!/bin/bash

# Hotel Onboarding System - Production Environment Setup
# Sets up all required environment variables for Heroku deployment

set -e

echo "🔧 PRODUCTION ENVIRONMENT SETUP"
echo "==============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if Heroku CLI is available
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI not found. Install with: brew install heroku"
    exit 1
fi

# Check if logged into Heroku
if ! heroku auth:whoami &> /dev/null; then
    print_error "Not logged into Heroku. Run: heroku login"
    exit 1
fi

HEROKU_APP="ordermanagement-3c6ea581a513"

print_info "Setting up environment variables for Heroku app: $HEROKU_APP"
echo ""

# Core Configuration
print_info "Setting core configuration..."
heroku config:set ENVIRONMENT="production" -a $HEROKU_APP
heroku config:set DEBUG="false" -a $HEROKU_APP
heroku config:set FRONTEND_URL="https://clickwise.in" -a $HEROKU_APP
print_status "Core configuration set"

# Database Configuration (Supabase)
print_info "Setting database configuration..."
print_warning "Please ensure you have the correct Supabase credentials"

# Note: These should be set manually with actual values
echo "Please set these manually with your actual Supabase credentials:"
echo "heroku config:set SUPABASE_URL=\"your-supabase-url\" -a $HEROKU_APP"
echo "heroku config:set SUPABASE_ANON_KEY=\"your-anon-key\" -a $HEROKU_APP"
echo "heroku config:set SUPABASE_SERVICE_ROLE_KEY=\"your-service-key\" -a $HEROKU_APP"
echo ""

# Google Document AI Configuration
print_info "Setting Google Document AI configuration..."

# Check if Google credentials file exists
if [ -f "hotel-onboarding-backend/gen-lang-client-0576186929-a311cca64d6a.json" ]; then
    print_info "Encoding Google credentials..."
    cd hotel-onboarding-backend
    base64 -i gen-lang-client-0576186929-a311cca64d6a.json | tr -d '\n' > google-creds-base64.txt
    
    heroku config:set GOOGLE_PROJECT_ID="933544811759" -a $HEROKU_APP
    heroku config:set GOOGLE_PROCESSOR_ID="50c628033c5d5dde" -a $HEROKU_APP
    heroku config:set GOOGLE_PROCESSOR_LOCATION="us" -a $HEROKU_APP
    heroku config:set GOOGLE_CREDENTIALS_BASE64="$(cat google-creds-base64.txt)" -a $HEROKU_APP
    
    cd ..
    print_status "Google Document AI configured"
else
    print_warning "Google credentials file not found. Please add manually:"
    echo "heroku config:set GOOGLE_PROJECT_ID=\"933544811759\" -a $HEROKU_APP"
    echo "heroku config:set GOOGLE_PROCESSOR_ID=\"50c628033c5d5dde\" -a $HEROKU_APP"
    echo "heroku config:set GOOGLE_PROCESSOR_LOCATION=\"us\" -a $HEROKU_APP"
    echo "heroku config:set GOOGLE_CREDENTIALS_BASE64=\"your-base64-credentials\" -a $HEROKU_APP"
fi

# Authentication Configuration
print_info "Setting authentication configuration..."
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

heroku config:set JWT_SECRET_KEY="$JWT_SECRET" -a $HEROKU_APP
heroku config:set JWT_ACCESS_TOKEN_EXPIRE_HOURS="24" -a $HEROKU_APP
heroku config:set ENCRYPTION_KEY="$ENCRYPTION_KEY" -a $HEROKU_APP
print_status "Authentication configured"

# Email Configuration
print_info "Setting email configuration..."
print_warning "Please update with your actual email credentials"

echo "Please set these manually with your actual email credentials:"
echo "heroku config:set SMTP_HOST=\"smtp.gmail.com\" -a $HEROKU_APP"
echo "heroku config:set SMTP_PORT=\"587\" -a $HEROKU_APP"
echo "heroku config:set SMTP_USERNAME=\"your-email@gmail.com\" -a $HEROKU_APP"
echo "heroku config:set SMTP_PASSWORD=\"your-app-password\" -a $HEROKU_APP"
echo "heroku config:set FROM_EMAIL=\"noreply@hotelonboarding.com\" -a $HEROKU_APP"
echo "heroku config:set FROM_NAME=\"Hotel Onboarding System\" -a $HEROKU_APP"
echo ""

# OCR Fallback Configuration
print_info "Setting OCR fallback configuration..."
print_warning "Please update with your actual Groq API key"

echo "Please set this manually with your actual Groq API key:"
echo "heroku config:set GROQ_API_KEY=\"your-groq-api-key\" -a $HEROKU_APP"
echo "heroku config:set GROQ_MODEL=\"llama-3.2-90b-vision-preview\" -a $HEROKU_APP"
echo "heroku config:set GROQ_TEMPERATURE=\"0.2\" -a $HEROKU_APP"
echo "heroku config:set GROQ_MAX_TOKENS=\"4096\" -a $HEROKU_APP"
echo ""

# Verify configuration
print_info "Verifying configuration..."
echo ""
echo "Current environment variables:"
heroku config -a $HEROKU_APP

echo ""
print_status "Environment setup completed!"
print_info "Please manually set the credentials marked above, then run:"
print_info "./deploy_to_production.sh"
