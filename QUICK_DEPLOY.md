# Quick Deployment Guide - I-9 OCR Ready

## ✅ Pre-Deployment Checklist
- [x] CORS configured for production domains
- [x] requirements.txt includes google-cloud-documentai==2.29.0
- [x] Google Document AI ONLY (no Groq fallback for government IDs)
- [x] Section 2 auto-population from OCR
- [x] Complete I-9 saves to database

## 🚀 Backend Deployment to Heroku

### 1. Prepare Google Credentials Base64
```bash
# If you haven't already, convert your Google service account JSON to base64:
base64 -i gen-lang-client-0576186929-a311cca64d6a.json | tr -d '\n' > google-creds-base64.txt
```

### 2. Set Heroku Environment Variables
```bash
cd hotel-onboarding-backend

# Login to Heroku
heroku login

# Link to existing app (or create new)
heroku git:remote -a ordermanagement-3c6ea581a513

# Set all required environment variables
heroku config:set GOOGLE_PROJECT_ID="933544811759"
heroku config:set GOOGLE_PROCESSOR_ID="50c628033c5d5dde"
heroku config:set GOOGLE_PROCESSOR_LOCATION="us"
heroku config:set GOOGLE_CREDENTIALS_BASE64="$(cat google-creds-base64.txt)"

# Database (use your actual values)
heroku config:set SUPABASE_URL="your-supabase-url"
heroku config:set SUPABASE_KEY="your-anon-key"

# JWT Secret (generate new one)
heroku config:set JWT_SECRET_KEY="$(openssl rand -hex 32)"
heroku config:set JWT_ACCESS_TOKEN_EXPIRE_HOURS="24"

# Email (use your actual values)
heroku config:set SMTP_HOST="smtp.gmail.com"
heroku config:set SMTP_PORT="587"
heroku config:set SMTP_USERNAME="your-email@gmail.com"
heroku config:set SMTP_PASSWORD="your-app-password"
heroku config:set FROM_EMAIL="noreply@hotelonboarding.com"

# Frontend URL
heroku config:set FRONTEND_URL="https://clickwise.in"
heroku config:set ENVIRONMENT="production"
```

### 3. Deploy to Heroku
```bash
# Add all changes
git add .
git commit -m "Deploy with Google Document AI only for I-9 OCR"

# Push to Heroku
git push heroku main

# Check logs
heroku logs --tail

# Verify deployment
heroku open /docs
```

## 🎨 Frontend Deployment to Vercel

### 1. Build and Deploy
```bash
cd hotel-onboarding-frontend

# Build production version
npm run build

# Deploy to Vercel
vercel --prod

# Follow prompts:
# - Set up and deploy: Y
# - Scope: Your account
# - Project name: hotel-onboarding-frontend
# - Directory: ./
```

### 2. Set Environment Variables in Vercel Dashboard
Go to https://vercel.com/dashboard → Your Project → Settings → Environment Variables

Add:
- `VITE_API_URL`: `https://ordermanagement-3c6ea581a513.herokuapp.com`
- `VITE_APP_URL`: `https://clickwise.in`

## ✅ What Will Work in Production

1. **Employee Onboarding Flow**:
   - Employee completes I-9 Section 1 ✅
   - Employee uploads driver's license ✅
   - Google Document AI extracts:
     - Document Number
     - Expiration Date
     - Issuing Authority
   - Section 2 auto-populates from OCR ✅
   - Complete I-9 saved to database ✅
   - PDF generated with both sections ✅

2. **Security Compliance**:
   - ONLY Google Document AI for government IDs ✅
   - No Groq fallback ✅
   - Base64 credentials for Heroku ✅

## 🧪 Post-Deployment Testing

### Test OCR Flow
1. Go to https://clickwise.in/apply/test-prop-001
2. Complete application
3. Upload a driver's license during I-9
4. Verify Section 2 auto-populates
5. Check PDF has both sections filled

### Verify Backend Logs
```bash
heroku logs --tail | grep "Google Document AI"
# Should see: "✅ Using Google Document AI for OCR processing"
# Should NOT see any Groq fallback messages
```

## ⚠️ Important Notes

- **NO GROQ FALLBACK**: We removed Groq fallback for government IDs per security requirements
- **Google Document AI Required**: OCR will not work without proper Google credentials
- **Section 2 Auto-Population**: Happens during employee submission, not manager review
- **Database Save**: Complete I-9 with both sections saves to `i9_forms` table

## 🆘 Troubleshooting

If OCR fails:
```bash
# Check Google credentials are set
heroku config:get GOOGLE_CREDENTIALS_BASE64

# Check logs for initialization
heroku logs --tail | grep "OCR"

# Verify no Groq fallback
heroku logs --tail | grep "Groq"  # Should be empty
```

---

**Last Updated**: August 2025
**I-9 OCR Status**: ✅ Production Ready