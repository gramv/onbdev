# Hotel Onboarding System - Deployment Instructions

## Quick Start Deployment Guide

This guide provides step-by-step instructions for deploying the Hotel Employee Onboarding System to production using Heroku (backend) and Vercel (frontend).

## Prerequisites

- Heroku CLI installed: `brew install heroku` (macOS)
- Vercel CLI installed: `npm i -g vercel`
- Git configured and repository ready
- Google Cloud account with Document AI enabled
- Supabase project set up

## Part 1: Backend Deployment to Heroku

### Step 1: Prepare Google Credentials

1. **Convert your Google service account JSON to base64:**
   ```bash
   base64 -i gen-lang-client-0576186929-a311cca64d6a.json | tr -d '\n' > google-creds-base64.txt
   ```

2. **Save the base64 string** from `google-creds-base64.txt` - you'll need it for Heroku config.

### Step 2: Create Heroku App

```bash
cd hotel-onboarding-backend

# Login to Heroku
heroku login

# Create new app (or use existing)
heroku create hotel-onboarding-api
# Or link existing: heroku git:remote -a ordermanagement-3c6ea581a513
```

### Step 3: Configure Environment Variables

```bash
# Database (Supabase)
heroku config:set DATABASE_URL="your-postgresql-url"
heroku config:set SUPABASE_URL="https://your-project.supabase.co"
heroku config:set SUPABASE_ANON_KEY="your-anon-key"

# Google Document AI (NEW - Primary OCR)
heroku config:set GOOGLE_PROJECT_ID="933544811759"
heroku config:set GOOGLE_PROCESSOR_ID="50c628033c5d5dde"
heroku config:set GOOGLE_PROCESSOR_LOCATION="us"
heroku config:set GOOGLE_CREDENTIALS_BASE64="$(cat google-creds-base64.txt)"

# Groq (Fallback OCR)
heroku config:set GROQ_API_KEY="your-groq-api-key"
heroku config:set GROQ_MODEL="llama-3.2-90b-vision-preview"
heroku config:set GROQ_TEMPERATURE="0.2"
heroku config:set GROQ_MAX_TOKENS="4096"

# Authentication
heroku config:set JWT_SECRET_KEY="$(openssl rand -hex 32)"
heroku config:set JWT_ACCESS_TOKEN_EXPIRE_HOURS="24"
heroku config:set ENCRYPTION_KEY="$(openssl rand -hex 32)"

# Email
heroku config:set SMTP_HOST="smtp.gmail.com"
heroku config:set SMTP_PORT="587"
heroku config:set SMTP_USE_TLS="true"
heroku config:set SMTP_USERNAME="your-email@gmail.com"
heroku config:set SMTP_PASSWORD="your-app-password"
heroku config:set FROM_EMAIL="noreply@hotelonboarding.com"
heroku config:set FROM_NAME="Hotel Onboarding System"

# Application
heroku config:set FRONTEND_URL="https://clickwise.in"
heroku config:set ENVIRONMENT="production"
heroku config:set DEBUG="false"
```

### Step 4: Verify Required Files

Ensure these files exist in `hotel-onboarding-backend/`:
- ✅ `Procfile` - Contains: `web: uvicorn app.main_enhanced:app --host 0.0.0.0 --port $PORT`
- ✅ `runtime.txt` - Contains: `python-3.12.8`
- ✅ `requirements.txt` - All dependencies including `google-cloud-documentai==2.29.0`

### Step 5: Deploy to Heroku

```bash
# Add and commit all changes
git add .
git commit -m "Prepare for Heroku deployment with Google Document AI"

# Push to Heroku
git push heroku main

# Or if using a different branch:
# git push heroku your-branch:main
```

### Step 6: Verify Backend Deployment

```bash
# Check logs
heroku logs --tail

# Open API docs
heroku open /docs

# Test health endpoint
curl https://your-app.herokuapp.com/docs
```

## Part 2: Frontend Deployment to Vercel

### Step 1: Navigate to Frontend Directory

```bash
cd hotel-onboarding-frontend
```

### Step 2: Verify Environment Configuration

Ensure `.env.production` contains:
```env
VITE_API_URL=https://ordermanagement-3c6ea581a513.herokuapp.com
VITE_APP_URL=https://clickwise.in
```

### Step 3: Build Production Version

```bash
# Clean previous builds
rm -rf dist

# Build for production
npm run build
```

### Step 4: Deploy to Vercel

```bash
# Login to Vercel (first time only)
vercel login

# Deploy to production
vercel --prod

# Follow prompts:
# - Set up and deploy: Y
# - Which scope: Your account
# - Link to existing project?: N (first time) or Y
# - Project name: hotel-onboarding-frontend
# - Directory: ./
# - Override settings?: N
```

### Step 5: Configure Environment Variables in Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
   - `VITE_API_URL`: `https://ordermanagement-3c6ea581a513.herokuapp.com`
   - `VITE_APP_URL`: `https://clickwise.in`

### Step 6: Configure Custom Domain (Optional)

1. In Vercel Dashboard → Settings → Domains
2. Add `clickwise.in`
3. Configure DNS at your registrar:
   ```
   A Record: @ → 76.76.21.21
   CNAME: www → cname.vercel-dns.com
   ```

## Part 3: Post-Deployment Verification

### 1. Test Critical Flows

```bash
# Test backend API
curl https://your-backend.herokuapp.com/docs

# Test frontend
open https://your-frontend.vercel.app
```

### 2. Verify OCR Service

Test that Google Document AI is working:
```bash
# Check backend logs for OCR initialization
heroku logs --tail | grep "Google Document AI"

# Should see:
# ✅ Using Google Document AI for OCR processing
# Using base64-encoded credentials (production mode)
```

### 3. Test Complete Flow

1. **Job Application**: https://your-frontend/apply/test-prop-001
2. **Manager Login**: Use test credentials
3. **Document Upload**: Test I-9 document OCR
4. **PDF Generation**: Verify all PDFs generate correctly

## Troubleshooting

### Google Document AI Issues

If OCR fails, check:
```bash
# Verify credentials are set
heroku config:get GOOGLE_CREDENTIALS_BASE64

# Check logs for errors
heroku logs --tail | grep "OCR"

# Verify fallback to Groq works
heroku config:get GROQ_API_KEY
```

### CORS Issues

If frontend can't connect to backend:
1. Verify `FRONTEND_URL` in Heroku config
2. Check CORS origins in `main_enhanced.py`
3. Ensure production URLs are in `allowed_origins`

### Build Failures

For Heroku:
```bash
# Clear build cache
heroku plugins:install heroku-builds
heroku builds:cache:purge

# Rebuild
git commit --allow-empty -m "Force rebuild"
git push heroku main
```

For Vercel:
```bash
# Clear cache and rebuild
vercel --force
```

## Security Checklist

- [ ] All `.env` files are in `.gitignore`
- [ ] Google credentials JSON is NOT in repository
- [ ] JWT secret keys are strong and unique
- [ ] SMTP uses app-specific password, not account password
- [ ] Debug mode is set to `false` in production
- [ ] All test accounts have strong passwords

## Monitoring

### Heroku Monitoring
```bash
# View metrics
heroku ps
heroku logs --tail

# Add monitoring (optional)
heroku addons:create papertrail
heroku addons:create newrelic
```

### Google Document AI Monitoring
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to Document AI
3. Check processor usage and quotas

## Maintenance

### Update Backend
```bash
cd hotel-onboarding-backend
git add .
git commit -m "Update message"
git push heroku main
```

### Update Frontend
```bash
cd hotel-onboarding-frontend
npm run build
vercel --prod
```

### Database Migrations
```bash
# SSH into Heroku
heroku run bash

# Run migrations
python -c "from app.supabase_service_enhanced import EnhancedSupabaseService; 
service = EnhancedSupabaseService(); 
# Run your migration code here"
```

## Rollback Procedures

### Heroku Rollback
```bash
# View releases
heroku releases

# Rollback to previous
heroku rollback v10
```

### Vercel Rollback
1. Go to Vercel Dashboard
2. Navigate to Deployments
3. Find previous stable deployment
4. Click "..." → "Promote to Production"

## Support Contacts

- **Heroku Support**: https://help.heroku.com
- **Vercel Support**: https://vercel.com/support
- **Google Cloud Support**: https://cloud.google.com/support

## Next Steps

1. Set up monitoring and alerts
2. Configure backup strategies
3. Implement CI/CD pipeline
4. Set up staging environment
5. Document API endpoints for team

---

**Last Updated**: August 2025
**Version**: 1.0.0