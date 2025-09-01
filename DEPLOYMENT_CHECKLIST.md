# 🚀 Hotel Onboarding System - Production Deployment Checklist

## 📋 Overview

This checklist covers deploying the latest changes including:
- ✅ **PDF Preview After Signing Fix** - Fixed URL patterns and state management
- ✅ **Signature Date Feature** - Added date display on signed PDFs  
- ✅ **Enhanced Error Handling** - Improved debugging and error recovery
- ✅ **Performance Optimizations** - Better PDF processing and state transitions

## 🔧 Prerequisites

### Required Tools
- [ ] **Heroku CLI** installed (`brew install heroku`)
- [ ] **Vercel CLI** installed (`npm i -g vercel`)
- [ ] **Git** configured with repository access
- [ ] **Node.js** 20+ and **Python** 3.12+ installed

### Authentication
- [ ] Logged into Heroku (`heroku login`)
- [ ] Logged into Vercel (`vercel login`)
- [ ] Git repository access confirmed

### Environment Variables Ready
- [ ] **Google Document AI** credentials (base64 encoded)
- [ ] **Supabase** connection details
- [ ] **SMTP** email configuration
- [ ] **Groq API** key for OCR fallback

## 🎯 Deployment Steps

### Option 1: Automated Deployment (Recommended)

```bash
# Run the automated deployment script
./deploy_to_production.sh
```

### Option 2: Manual Deployment

#### Step 1: Backend Deployment to Heroku

```bash
cd hotel-onboarding-backend

# Verify deployment files exist
ls -la Procfile runtime.txt requirements.txt

# Commit latest changes
git add .
git commit -m "Deploy latest changes: PDF preview fix and signature date"

# Set Heroku remote (if not already set)
heroku git:remote -a ordermanagement-3c6ea581a513

# Deploy to Heroku
git push heroku main

# Verify deployment
heroku logs --tail
heroku open /docs
```

#### Step 2: Frontend Deployment to Vercel

```bash
cd hotel-onboarding-frontend

# Create/verify production environment
cat > .env.production << EOF
VITE_API_URL=https://ordermanagement-3c6ea581a513.herokuapp.com
VITE_APP_URL=https://clickwise.in
EOF

# Install dependencies and build
npm install
npm run build

# Deploy to Vercel
vercel --prod
```

## 🔍 Post-Deployment Verification

### Backend Health Checks
- [ ] **API Documentation**: https://ordermanagement-3c6ea581a513.herokuapp.com/docs
- [ ] **Health Endpoint**: https://ordermanagement-3c6ea581a513.herokuapp.com/healthz
- [ ] **PDF Generation**: Test health insurance PDF endpoint
- [ ] **Signature Addition**: Test signature API endpoint

### Frontend Health Checks  
- [ ] **Main Site**: https://clickwise.in
- [ ] **Onboarding Flow**: https://clickwise.in/onboard
- [ ] **Manager Dashboard**: https://clickwise.in/manager
- [ ] **HR Dashboard**: https://clickwise.in/hr

### Feature-Specific Testing

#### PDF Preview After Signing (NEW)
- [ ] Fill out health insurance form
- [ ] Click "Review and Sign"
- [ ] Sign the document
- [ ] **Verify**: PDF preview appears immediately after signing
- [ ] **Verify**: Can navigate back to review or complete
- [ ] **Verify**: No console errors in browser DevTools

#### Signature Date Feature (NEW)
- [ ] Complete health insurance form and sign
- [ ] Download the signed PDF
- [ ] **Verify**: Date appears next to signature (MM/DD/YYYY format)
- [ ] **Verify**: Date matches signing timestamp
- [ ] **Verify**: Date positioning is correct (right of signature)

#### Existing Features
- [ ] Job application submission
- [ ] I-9 form completion with OCR
- [ ] W-4 form completion
- [ ] Manager approval workflow
- [ ] HR dashboard functionality
- [ ] Email notifications
- [ ] WebSocket real-time updates

## 🚨 Rollback Procedures

### If Backend Deployment Fails
```bash
# Check Heroku releases
heroku releases -a ordermanagement-3c6ea581a513

# Rollback to previous version
heroku rollback v[PREVIOUS_VERSION] -a ordermanagement-3c6ea581a513
```

### If Frontend Deployment Fails
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to the project deployments
3. Find the last stable deployment
4. Click "..." → "Promote to Production"

## 📊 Environment Variables

### Backend (Heroku)
```bash
# Core Configuration
heroku config:set ENVIRONMENT="production"
heroku config:set DEBUG="false"
heroku config:set FRONTEND_URL="https://clickwise.in"

# Database (Supabase)
heroku config:set SUPABASE_URL="your-supabase-url"
heroku config:set SUPABASE_ANON_KEY="your-anon-key"
heroku config:set SUPABASE_SERVICE_ROLE_KEY="your-service-key"

# Google Document AI
heroku config:set GOOGLE_PROJECT_ID="933544811759"
heroku config:set GOOGLE_PROCESSOR_ID="50c628033c5d5dde"
heroku config:set GOOGLE_PROCESSOR_LOCATION="us"
heroku config:set GOOGLE_CREDENTIALS_BASE64="$(cat google-creds-base64.txt)"

# Authentication
heroku config:set JWT_SECRET_KEY="$(openssl rand -hex 32)"
heroku config:set JWT_ACCESS_TOKEN_EXPIRE_HOURS="24"

# Email Configuration
heroku config:set SMTP_HOST="smtp.gmail.com"
heroku config:set SMTP_PORT="587"
heroku config:set SMTP_USERNAME="your-email@gmail.com"
heroku config:set SMTP_PASSWORD="your-app-password"
heroku config:set FROM_EMAIL="noreply@hotelonboarding.com"

# OCR Fallback
heroku config:set GROQ_API_KEY="your-groq-api-key"
```

### Frontend (Vercel)
```bash
# Set in Vercel Dashboard or .env.production
VITE_API_URL=https://ordermanagement-3c6ea581a513.herokuapp.com
VITE_APP_URL=https://clickwise.in
```

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
heroku logs --tail -a ordermanagement-3c6ea581a513

# Common fixes
heroku restart -a ordermanagement-3c6ea581a513
heroku ps:scale web=1 -a ordermanagement-3c6ea581a513
```

#### Frontend Build Fails
```bash
# Clear cache and rebuild
rm -rf node_modules/.vite dist
npm install
npm run build
```

#### PDF Preview Not Working
- Check browser console for JavaScript errors
- Verify API endpoints are responding
- Test signature API endpoint directly
- Check network tab for failed requests

#### Signature Date Missing
- Verify backend logs for PDF processing errors
- Check if signature_date is being sent in API request
- Test PDF generation endpoint directly

## 📞 Support Contacts

### Monitoring Commands
```bash
# Backend logs
heroku logs --tail -a ordermanagement-3c6ea581a513

# Backend metrics
heroku ps -a ordermanagement-3c6ea581a513

# Frontend logs
# Check Vercel dashboard: https://vercel.com/dashboard
```

### Key URLs
- **Backend API**: https://ordermanagement-3c6ea581a513.herokuapp.com
- **Frontend**: https://clickwise.in
- **API Docs**: https://ordermanagement-3c6ea581a513.herokuapp.com/docs
- **Heroku Dashboard**: https://dashboard.heroku.com/apps/ordermanagement-3c6ea581a513
- **Vercel Dashboard**: https://vercel.com/dashboard

## ✅ Deployment Completion

Once all checks pass:
- [ ] **Backend deployed** and responding
- [ ] **Frontend deployed** and accessible
- [ ] **PDF preview after signing** working
- [ ] **Signature date** appearing on PDFs
- [ ] **All existing features** still functional
- [ ] **Performance** acceptable (< 2s for PDF operations)
- [ ] **Error handling** working correctly

**🎉 Deployment Complete!** The latest changes are now live in production.
