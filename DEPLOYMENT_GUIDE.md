# Lohnkonten Data Extraction - Complete Deployment Guide

This guide covers deploying both the frontend and backend to production.

## Quick Start

### Railway Deployment (Recommended)

**Backend:**
```bash
cd backend
railway login
railway init
railway up
```

**Frontend:**
```bash
cd frontend
railway login
railway init
railway up
```

### Vercel Deployment

**Frontend:**
```bash
cd frontend
vercel
```

**Backend:** Not recommended (use Railway instead)

---

## Architecture Overview

```
┌─────────────┐         ┌──────────────┐
│  Frontend   │ ──────> │   Backend    │
│   (React)   │  HTTPS  │  (FastAPI)   │
│             │ <────── │   + Java     │
└─────────────┘         └──────────────┘
  Vercel/Railway         Railway/Docker
```

---

## Deployment Options

### Frontend Deployment

| Platform | Difficulty | Cost | Speed | Recommended |
|----------|-----------|------|-------|-------------|
| **Vercel** | Easy | Free tier | Fast | ✅ Yes |
| **Netlify** | Easy | Free tier | Fast | ✅ Yes |
| **Railway** | Easy | $5/mo | Fast | ✅ Yes |
| **GitHub Pages** | Medium | Free | Medium | ⚠️ Static only |

### Backend Deployment

| Platform | Difficulty | Cost | Java Support | Recommended |
|----------|-----------|------|--------------|-------------|
| **Railway** | Easy | $5/mo | ✅ Yes | ✅ **Best Choice** |
| **Docker** | Medium | Varies | ✅ Yes | ✅ Good |
| **Heroku** | Easy | $7/mo | ✅ Yes | ⚠️ OK |
| **Vercel** | Easy | Free | ❌ No | ❌ Not suitable |

---

## Step-by-Step Deployment

### Step 1: Deploy Backend to Railway

1. **Create Railway Account**:
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy via Dashboard**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select `backend` as the root directory
   - Railway will auto-detect configuration

3. **Or Deploy via CLI**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Navigate to backend
   cd backend

   # Initialize and deploy
   railway init
   railway up
   ```

4. **Set Environment Variables** (in Railway dashboard):
   ```env
   TEMPLATE_PATH=template.xlsx
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   ```

5. **Get Backend URL**:
   - Copy the generated URL (e.g., `https://your-app.railway.app`)
   - You'll need this for the frontend

### Step 2: Deploy Frontend to Vercel

1. **Update Frontend Environment**:

   Edit `frontend/.env.production`:
   ```env
   VITE_API_URL=https://your-backend.railway.app
   VITE_APP_VERSION=1.0.0
   ```

2. **Deploy via Vercel Dashboard**:
   - Go to https://vercel.com
   - Click "Import Project"
   - Select your GitHub repository
   - Set Root Directory to `frontend`
   - Click Deploy

3. **Or Deploy via CLI**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Navigate to frontend
   cd frontend

   # Deploy
   vercel --prod
   ```

4. **Configure Environment Variables** (in Vercel dashboard):
   ```env
   VITE_API_URL=https://your-backend.railway.app
   VITE_APP_VERSION=1.0.0
   ```

### Step 3: Update CORS on Backend

Once you have the frontend URL, update the backend CORS:

In Railway dashboard, set:
```env
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Step 4: Verify Deployment

1. **Test Backend**:
   ```bash
   curl https://your-backend.railway.app/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "template_exists": true,
     "java_installed": true
   }
   ```

2. **Test Frontend**:
   - Visit `https://your-frontend.vercel.app`
   - Upload a test PDF
   - Verify file processing works
   - Check download functionality

---

## Configuration Files Created

### Backend Files

- ✅ **`nixpacks.toml`** - Railway configuration with Java support
- ✅ **`railway.json`** - Railway deployment settings
- ✅ **`Dockerfile`** - Docker containerization
- ✅ **`.dockerignore`** - Docker ignore rules
- ✅ **`Procfile`** - Process configuration (fixed to use `api:app`)
- ✅ **`vercel.json`** - Vercel config (not recommended)

### Frontend Files

- ✅ **`vercel.json`** - Vercel deployment configuration
- ✅ **`railway.toml`** - Railway deployment configuration
- ✅ **`.env.production`** - Production environment variables
- ✅ **`.env.example`** - Environment template
- ✅ **`public/_headers`** - Security headers

---

## Environment Variables Reference

### Backend

```env
# Server Configuration
PORT=8000                              # Auto-set by platform
HOST=0.0.0.0                          # Bind to all interfaces

# Application Settings
TEMPLATE_PATH=template.xlsx            # Excel template path
ALLOWED_ORIGINS=https://your-frontend.vercel.app  # Frontend URL(s)

# Optional
OUTPUT_DIR=output                      # Output directory
```

### Frontend

```env
# API Configuration
VITE_API_URL=https://your-backend.railway.app

# Application
VITE_APP_VERSION=1.0.0
```

---

## Common Deployment Issues & Solutions

### Issue 1: "Java not found" on Railway

**Cause**: Java Runtime not installed

**Solution**: Verify `nixpacks.toml` contains:
```toml
[phases.setup]
nixPkgs = ["python311", "jre_headless"]
```

### Issue 2: "app not found" error

**Cause**: Incorrect module reference

**Solution**: Check `Procfile` and `nixpacks.toml` use `api:app` not `app:app`

### Issue 3: CORS errors

**Cause**: Frontend URL not in CORS allowed origins

**Solution**: Set `ALLOWED_ORIGINS` to frontend URL:
```env
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Issue 4: Template file not found

**Cause**: `template.xlsx` not deployed

**Solution**:
- Verify file exists in backend directory
- Check it's not in `.gitignore`
- Confirm `TEMPLATE_PATH` environment variable

### Issue 5: JAR file missing

**Cause**: `Lohnkonten-1.0.0.jar` too large or ignored

**Solution**:
- File is 23MB, ensure Git LFS is used OR
- Remove from `.gitignore`
- Verify file is in repository

---

## Production Checklist

### Before Deployment

- [ ] Backend files present: `api.py`, `jar_processor.py`, `Lohnkonten-1.0.0.jar`, `template.xlsx`
- [ ] Frontend built successfully (`npm run build`)
- [ ] Environment variables configured
- [ ] CORS origins set correctly
- [ ] All tests passing

### After Backend Deployment

- [ ] Health check returns 200 OK
- [ ] Java version detected
- [ ] Template file found
- [ ] Test PDF upload works

### After Frontend Deployment

- [ ] Site loads without errors
- [ ] API calls reach backend
- [ ] File upload functional
- [ ] File download works
- [ ] Mobile responsive
- [ ] HTTPS enabled

---

## Monitoring & Maintenance

### Railway

View logs:
```bash
railway logs
```

Monitor in dashboard:
- CPU usage
- Memory usage
- Request count
- Error rate

### Vercel

View logs:
- Vercel dashboard > Project > Logs
- Real-time function logs
- Analytics and insights

### Health Checks

Set up monitoring (recommended):
- UptimeRobot (free)
- Better Uptime
- Pingdom

Monitor endpoints:
- Backend: `https://your-backend.railway.app/health`
- Frontend: `https://your-frontend.vercel.app`

---

## Costs Estimate

### Free Tier Setup
- **Frontend**: Vercel (Free)
- **Backend**: Not possible (Java required)
- **Total**: Cannot deploy on free tier

### Budget Setup ($5/month)
- **Frontend**: Vercel (Free)
- **Backend**: Railway Hobby ($5/mo)
- **Total**: $5/month

### Production Setup ($20-25/month)
- **Frontend**: Vercel Pro ($20/mo) OR Netlify Pro ($19/mo)
- **Backend**: Railway Pro ($20/mo)
- **Total**: $40/month

---

## Scaling Recommendations

### Low Traffic (< 100 requests/day)
- Frontend: Vercel Free
- Backend: Railway Hobby ($5/mo)

### Medium Traffic (100-1000 requests/day)
- Frontend: Vercel Free/Pro
- Backend: Railway Pro ($20/mo)
- Consider caching strategies

### High Traffic (1000+ requests/day)
- Frontend: Vercel Pro + CDN
- Backend: Railway Pro with auto-scaling
- Implement queue system
- Add Redis caching
- Load balancing

---

## Rollback Procedures

### Railway
```bash
# List deployments
railway status

# Rollback to previous deployment
railway rollback
```

### Vercel
```bash
# List deployments
vercel ls

# Rollback
vercel rollback
```

Or use dashboard to select previous deployment.

---

## Security Recommendations

- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Set specific CORS origins (not `*`)
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Regular dependency updates
- [ ] Monitor for vulnerabilities
- [ ] Set up error tracking (Sentry)

---

## Support & Resources

### Documentation
- Backend: `backend/DEPLOYMENT.md`
- Frontend: `frontend/DEPLOYMENT.md`
- Frontend README: `frontend/README.md`

### Platform Docs
- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
- Netlify: https://docs.netlify.com

### Troubleshooting
- Check health endpoints
- Review application logs
- Verify environment variables
- Test CORS configuration

---

**Last Updated**: 2025-01-17
**Version**: 1.0.0
