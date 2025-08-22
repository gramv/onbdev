# Hotel Employee Onboarding System - Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Backend Deployment (Heroku)](#backend-deployment-heroku)
- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Testing the Deployment](#testing-the-deployment)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Overview

The Hotel Employee Onboarding System is a comprehensive digital platform for managing employee onboarding with federal compliance (I-9, W-4 forms). The system consists of:
- **Backend API**: FastAPI application deployed on Heroku
- **Frontend**: React/TypeScript application deployed on Vercel
- **Database**: Supabase (managed PostgreSQL)

### Live URLs

#### Current Deployment
- **Frontend**: https://hotel-onboarding-frontend.vercel.app
- **Backend API**: https://ordermanagement-3c6ea581a513.herokuapp.com
- **API Documentation**: https://ordermanagement-3c6ea581a513.herokuapp.com/docs

#### Custom Domain (clickwise.in)
- **Frontend**: https://clickwise.in (Vercel CDN)
- **Backend API**: https://api.clickwise.in (Heroku)
- **API Documentation**: https://api.clickwise.in/docs

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│                     │         │                     │
│   Vercel (CDN)      │◄────────┤   Users/Browsers    │
│   React Frontend    │         │                     │
│                     │         └─────────────────────┘
└──────────┬──────────┘
           │
           │ HTTPS API Calls
           │
┌──────────▼──────────┐         ┌─────────────────────┐
│                     │         │                     │
│   Heroku            │◄────────┤   Supabase         │
│   FastAPI Backend   │         │   PostgreSQL DB     │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘
```

## Prerequisites

### Required Tools
- **Git**: Version control
- **Node.js**: v20 LTS or higher
- **Python**: 3.12 or higher
- **Heroku CLI**: For backend deployment
- **Vercel CLI**: For frontend deployment (`npm i -g vercel`)

### Required Accounts
- **Heroku Account**: https://heroku.com
- **Vercel Account**: https://vercel.com
- **Supabase Account**: https://supabase.com
- **Email Service**: SMTP credentials for sending emails

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DELTA=1440  # 24 hours in minutes

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@hotelonboarding.com
FROM_NAME=Hotel Onboarding System

# Frontend URL (for emails and QR codes)
FRONTEND_URL=https://hotel-onboarding-frontend.vercel.app

# External Services
GROQ_API_KEY=your-groq-api-key  # For OCR/vision processing
```

### Frontend (.env.production)
```bash
# API Configuration
VITE_API_URL=https://ordermanagement-3c6ea581a513.herokuapp.com
VITE_APP_URL=https://hotel-onboarding-frontend.vercel.app
```

## Backend Deployment (Heroku)

### Initial Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd hotel-onboarding-backend
```

2. **Create Heroku app**
```bash
heroku create your-app-name
```

3. **Add Python buildpack**
```bash
heroku buildpacks:set heroku/python
```

4. **Configure environment variables**
```bash
heroku config:set DATABASE_URL="your-database-url"
heroku config:set SUPABASE_URL="your-supabase-url"
heroku config:set SUPABASE_KEY="your-supabase-key"
heroku config:set JWT_SECRET_KEY="your-secret-key"
heroku config:set SMTP_HOST="smtp.gmail.com"
heroku config:set SMTP_PORT="587"
heroku config:set SMTP_USERNAME="your-email"
heroku config:set SMTP_PASSWORD="your-password"
heroku config:set FROM_EMAIL="noreply@hotelonboarding.com"
heroku config:set FRONTEND_URL="https://hotel-onboarding-frontend.vercel.app"
heroku config:set GROQ_API_KEY="your-groq-key"
```

### Deployment Files

Ensure these files exist in the backend directory:

**Procfile**
```
web: uvicorn app.main_enhanced:app --host 0.0.0.0 --port $PORT
```

**runtime.txt**
```
python-3.12.8
```

**requirements.txt**
Generate from Poetry (if using) or maintain manually:
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Deploy to Heroku

```bash
git add .
git commit -m "Deploy backend to Heroku"
git push heroku main
```

### Verify Deployment
```bash
heroku logs --tail
heroku open
```

## Frontend Deployment (Vercel)

### Initial Setup

1. **Navigate to frontend directory**
```bash
cd hotel-onboarding-frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Create production environment file**
Create `.env.production` with the appropriate values (see Environment Variables section)

4. **Create Vercel configuration**
Ensure `vercel.json` exists with SPA routing configuration:
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

### Build for Production

```bash
npm run build
```

### Deploy to Vercel

1. **Using Vercel CLI**
```bash
vercel --prod
```

2. **Follow the prompts**
- Select your account
- Link to existing project or create new
- Configure project settings
- Deploy

### Alternative: GitHub Integration

1. Push code to GitHub
2. Import project in Vercel dashboard
3. Configure build settings:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Add environment variables in Vercel dashboard
5. Deploy

## Post-Deployment Configuration

### 1. Database Setup

Run database migrations if needed:
```sql
-- Example: Create indexes for performance
CREATE INDEX idx_employees_property_id ON employees(property_id);
CREATE INDEX idx_applications_property_status ON job_applications(property_id, status);
CREATE INDEX idx_managers_property ON property_managers(property_id);
```

### 2. Create Initial Data

```bash
# SSH into Heroku
heroku run bash

# Run setup script
python3 setup_test_data.py
```

### 3. Configure CORS

Ensure backend allows frontend origin:
```python
# In app/main_enhanced.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hotel-onboarding-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing the Deployment

### 1. Test Backend Health
```bash
curl https://ordermanagement-3c6ea581a513.herokuapp.com/docs
```

### 2. Test Authentication
```bash
curl -X POST https://ordermanagement-3c6ea581a513.herokuapp.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

### 3. Test Frontend
- Visit https://hotel-onboarding-frontend.vercel.app
- Try logging in with test credentials
- Test job application flow
- Verify QR codes and links

### 4. Test Critical Flows
- [ ] HR/Manager login
- [ ] Job application submission
- [ ] Application approval
- [ ] Employee onboarding
- [ ] Document generation (I-9, W-4)
- [ ] Email notifications

## Troubleshooting

### Common Issues

#### 1. Frontend 404 Errors on Routes
**Problem**: Direct navigation to routes like `/apply/123` returns 404
**Solution**: Ensure `vercel.json` exists with proper rewrite rules

#### 2. API Connection Errors
**Problem**: Frontend can't connect to backend
**Solutions**:
- Check VITE_API_URL in `.env.production`
- Verify CORS configuration in backend
- Check Heroku logs: `heroku logs --tail`

#### 3. Email Not Sending
**Problem**: Email notifications not working
**Solutions**:
- Verify SMTP credentials in Heroku config
- Check email service limits
- Review email logs in Heroku

#### 4. Database Connection Issues
**Problem**: Backend can't connect to database
**Solutions**:
- Verify DATABASE_URL in Heroku config
- Check Supabase service status
- Review connection pool settings

#### 5. File Upload Issues
**Problem**: Documents not uploading
**Solutions**:
- Check Heroku's ephemeral filesystem limitations
- Verify Supabase storage configuration
- Check file size limits

### Debug Commands

```bash
# Check Heroku logs
heroku logs --tail --app your-app-name

# Check Heroku config
heroku config --app your-app-name

# Restart Heroku app
heroku restart --app your-app-name

# Check Vercel deployment
vercel ls
vercel inspect [deployment-url]

# Test API endpoints
curl -X GET https://your-backend.herokuapp.com/api/health
```

## Maintenance

### Regular Tasks

#### Daily
- Monitor error logs
- Check email delivery status
- Verify backup completion

#### Weekly
- Review performance metrics
- Check disk usage
- Update dependencies (security patches)

#### Monthly
- Full system backup
- Performance optimization review
- Security audit
- Update documentation

### Updating the Application

#### Backend Updates
```bash
git add .
git commit -m "Update description"
git push heroku main
```

#### Frontend Updates
```bash
npm run build
vercel --prod
```

### Scaling Considerations

#### Heroku Scaling
```bash
# Scale dynos
heroku ps:scale web=2

# Upgrade dyno type
heroku ps:resize web=standard-2x
```

#### Database Optimization
- Add indexes for frequently queried columns
- Implement connection pooling
- Consider read replicas for high traffic

### Monitoring

#### Recommended Tools
- **Heroku Metrics**: Built-in monitoring
- **Vercel Analytics**: Frontend performance
- **Supabase Dashboard**: Database metrics
- **External Monitoring**: Datadog, New Relic, or Sentry

### Backup Strategy

1. **Database Backups**
   - Supabase automatic daily backups
   - Additional manual backups before major updates

2. **Code Backups**
   - Git repository (GitHub/GitLab)
   - Tagged releases for each deployment

3. **Environment Backups**
   - Document all environment variables
   - Store securely (not in repo)

## Security Best Practices

1. **Keep dependencies updated**
```bash
# Backend
pip list --outdated
pip install --upgrade [package]

# Frontend
npm outdated
npm update
```

2. **Rotate secrets regularly**
   - JWT secret keys
   - API keys
   - Database passwords

3. **Enable 2FA**
   - Heroku account
   - Vercel account
   - Supabase account

4. **Monitor for vulnerabilities**
```bash
# Frontend
npm audit
npm audit fix

# Backend
pip-audit
```

## Custom Domain Configuration (clickwise.in)

### Architecture Overview
We're using a split architecture for optimal performance:
- **Frontend (clickwise.in)**: Served via Vercel's global CDN
- **Backend API (api.clickwise.in)**: Hosted on Heroku compute instances

### Step 1: Configure Backend Domain in Heroku

The backend is already configured with:
```bash
# Already added to Heroku:
api.clickwise.in
www.clickwise.in
```

### Step 2: Configure Frontend Domain in Vercel

1. **Add Domain in Vercel Dashboard**
   - Go to your project in Vercel Dashboard
   - Navigate to Settings → Domains
   - Add `clickwise.in` as your domain
   - Vercel will provide DNS records to configure

2. **Expected DNS Records from Vercel**
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

### Step 3: DNS Configuration at Your Domain Registrar

Configure these DNS records at your domain registrar (GoDaddy, Namecheap, etc.):

```
# For Frontend (Vercel)
Type: A
Name: @ (or blank, represents clickwise.in)
Value: 76.76.21.21
TTL: 3600

Type: CNAME  
Name: www
Value: cname.vercel-dns.com
TTL: 3600

# For Backend API (Heroku)
Type: CNAME
Name: api
Value: ordermanagement-3c6ea581a513.herokuapp.com
TTL: 3600
```

### Step 4: Verify DNS Propagation

After updating DNS records, verify propagation:

```bash
# Check frontend domain
nslookup clickwise.in
dig clickwise.in

# Check API subdomain
nslookup api.clickwise.in
dig api.clickwise.in

# Check www subdomain
nslookup www.clickwise.in
dig www.clickwise.in
```

### Step 5: SSL Certificate Configuration

Both Heroku and Vercel automatically provision SSL certificates:

- **Heroku**: Automated Certificate Management (ACM) handles api.clickwise.in
- **Vercel**: Automatically provisions Let's Encrypt certificates for clickwise.in and www.clickwise.in

### Step 6: Update Environment Variables

Ensure all environment variables are updated:

#### Backend (Heroku)
```bash
heroku config:set FRONTEND_URL=https://clickwise.in
```

#### Frontend (.env.production)
```bash
VITE_API_URL=https://api.clickwise.in
VITE_APP_URL=https://clickwise.in
```

### DNS Propagation Timeline

- **Initial Changes**: 5-10 minutes
- **Global Propagation**: Up to 48 hours (usually much faster)
- **SSL Certificates**: 10-30 minutes after DNS verification

### Troubleshooting Domain Issues

#### Issue: "Domain Not Found" Error
- Wait for DNS propagation (can take up to 48 hours)
- Verify DNS records are correctly configured
- Check with: `nslookup clickwise.in 8.8.8.8`

#### Issue: SSL Certificate Warnings
- Certificates provision automatically after DNS verification
- May take 10-30 minutes after domain is accessible
- Force refresh with: `heroku certs:auto:refresh` (for API)

#### Issue: API Calls Failing
- Verify CORS includes new domain in backend
- Check VITE_API_URL in frontend build
- Ensure api.clickwise.in CNAME is correct

#### Issue: Redirect Loops
- Check Heroku doesn't have forced SSL redirect conflicting with Vercel
- Verify no duplicate redirect rules

### Testing the Complete Setup

1. **Test Frontend Access**
   ```bash
   curl -I https://clickwise.in
   curl -I https://www.clickwise.in
   ```

2. **Test API Access**
   ```bash
   curl https://api.clickwise.in/docs
   ```

3. **Test Cross-Origin Requests**
   - Open https://clickwise.in
   - Check browser console for CORS errors
   - Verify login functionality works

### Current Status

- ✅ Backend configured with api.clickwise.in in Heroku
- ✅ Frontend deployed to Vercel
- ✅ Environment variables updated
- ✅ CORS configured for clickwise.in domains
- ⏳ Awaiting DNS configuration at domain registrar
- ⏳ Awaiting domain addition in Vercel dashboard

## Support and Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **React Documentation**: https://react.dev
- **Heroku Dev Center**: https://devcenter.heroku.com
- **Vercel Documentation**: https://vercel.com/docs
- **Supabase Documentation**: https://supabase.com/docs

## License

[Your License Here]

---

Last Updated: August 2025