# Backend Deployment Guide

This guide provides instructions for deploying the Lohnkonten Data Extraction backend to various platforms.

## Prerequisites

- Python 3.11+
- Java Runtime Environment (JRE) 8+
- The `Lohnkonten-1.0.0.jar` file
- The `template.xlsx` file

## Platform Support

### ✅ **Railway** (Recommended)
- Full Java support
- Easy deployment
- Automatic HTTPS
- **Best choice for this application**

### ✅ **Docker** (Any platform supporting Docker)
- Heroku
- DigitalOcean App Platform
- Google Cloud Run
- AWS ECS/Fargate
- Azure Container Apps

### ⚠️ **Vercel** (Limited)
- Serverless functions (60s timeout limit)
- May not work well with large PDFs
- No native Java support (requires workarounds)
- **Not recommended for production**

---

## Option 1: Railway Deployment (Recommended)

Railway provides excellent support for applications requiring Java.

### Method A: Using Nixpacks (Automatic)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project** (from backend directory):
   ```bash
   cd backend
   railway init
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

Railway will automatically:
- Detect `nixpacks.toml` configuration
- Install Python 3.11 and Java Runtime
- Install Python dependencies
- Start the application

### Method B: Using Dockerfile

1. **Create a new Railway project** via the dashboard

2. **Connect your GitHub repository**

3. **Railway will automatically**:
   - Detect the Dockerfile
   - Build the Docker image
   - Deploy the application

### Environment Variables for Railway

Set these in the Railway dashboard:

```env
PORT=8000                    # Automatically set by Railway
TEMPLATE_PATH=template.xlsx  # Path to Excel template
ALLOWED_ORIGINS=*            # Or specific frontend URL
```

### Verify Deployment

Once deployed, check the health endpoint:
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "template_exists": true,
  "java_installed": true,
  "java_version": "openjdk version..."
}
```

---

## Option 2: Docker Deployment

Use this method for any platform that supports Docker containers.

### Build Docker Image

```bash
cd backend
docker build -t lohnkonto-backend .
```

### Run Locally for Testing

```bash
docker run -p 8000:8000 \
  -e ALLOWED_ORIGINS="*" \
  lohnkonto-backend
```

Test the API:
```bash
curl http://localhost:8000/health
```

### Deploy to Container Platforms

#### Heroku

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Set stack to container
heroku stack:set container

# Deploy
git push heroku main
```

#### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/lohnkonto-backend

# Deploy to Cloud Run
gcloud run deploy lohnkonto-backend \
  --image gcr.io/PROJECT-ID/lohnkonto-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300s
```

#### DigitalOcean App Platform

1. Connect your GitHub repository
2. Select the `backend` directory
3. Choose **Dockerfile** as build method
4. Set environment variables
5. Deploy

---

## Option 3: Vercel Deployment (Not Recommended)

⚠️ **Important Limitations:**
- 60-second timeout for serverless functions
- No native Java support
- May fail with large PDFs
- **Use Railway or Docker instead**

### If you still want to try Vercel:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   cd backend
   vercel
   ```

3. **Note**: You'll need to modify the code to work around Java limitations, which is not ideal.

---

## File Structure for Deployment

Ensure these files are present in the `backend` directory:

```
backend/
├── api.py                    # FastAPI application
├── jar_processor.py          # JAR processing service
├── Lohnkonten-1.0.0.jar     # Java application (23MB)
├── template.xlsx             # Excel template (215KB)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── .dockerignore            # Docker ignore rules
├── nixpacks.toml            # Railway/Nixpacks config
├── railway.json             # Railway configuration
├── Procfile                 # Process configuration
└── vercel.json              # Vercel configuration (if using)
```

---

## Environment Variables

Configure these on your deployment platform:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Server port | 8000 | No (auto-set by platform) |
| `HOST` | Server host | 0.0.0.0 | No |
| `TEMPLATE_PATH` | Path to Excel template | template.xlsx | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | * | No |

### Production CORS Configuration

For production, set `ALLOWED_ORIGINS` to your specific frontend URLs:

```env
# Single origin
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Multiple origins
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://www.your-domain.com
```

---

## Post-Deployment Checklist

- [ ] Health check endpoint returns `200 OK`
- [ ] Java version is detected (check `/health`)
- [ ] Template file is found (check `/health`)
- [ ] CORS is configured correctly
- [ ] Test file upload with a sample PDF
- [ ] Test password-protected PDF
- [ ] Verify Excel file download works
- [ ] Check logs for any errors
- [ ] Set up monitoring/alerts

---

## Troubleshooting

### Issue: "Java not found" error

**Solution**:
- Railway: Ensure `nixpacks.toml` includes `jre_headless`
- Docker: Java is included in the Dockerfile
- Vercel: Not supported natively

### Issue: "JAR file not found"

**Solution**:
- Verify `Lohnkonten-1.0.0.jar` is in the backend directory
- Check it's not in `.gitignore` or `.dockerignore`
- File size is ~23MB, ensure it's uploaded

### Issue: "Template file not found"

**Solution**:
- Verify `template.xlsx` exists in backend directory
- Set `TEMPLATE_PATH` environment variable
- Check file permissions

### Issue: CORS errors from frontend

**Solution**:
- Set `ALLOWED_ORIGINS` to your frontend URL
- Or use `*` for development (not recommended for production)

### Issue: Timeout errors with large PDFs

**Solution**:
- Railway/Docker: Increase timeout settings
- Vercel: Not suitable for large files (use Railway)

### Issue: Memory errors

**Solution**:
- Increase memory allocation in platform settings
- Railway: Upgrade plan if needed
- Docker: Set memory limits in docker-compose or platform

---

## Monitoring and Logs

### Railway

View logs in the Railway dashboard or CLI:
```bash
railway logs
```

### Docker/Heroku

```bash
heroku logs --tail
```

### Google Cloud Run

```bash
gcloud logging read "resource.type=cloud_run_revision"
```

---

## Scaling Considerations

For production deployments:

1. **Railway**:
   - Horizontal scaling available on Pro plan
   - Monitor memory and CPU usage

2. **Docker Platforms**:
   - Configure auto-scaling based on CPU/memory
   - Set min/max instances

3. **Load Handling**:
   - Each PDF processing can take 5-30 seconds
   - Plan capacity accordingly
   - Consider queue system for high traffic

---

## Security Best Practices

- [ ] Use specific CORS origins in production
- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Set up rate limiting
- [ ] Monitor for abuse
- [ ] Keep dependencies updated
- [ ] Regular security audits
- [ ] Use secrets management for sensitive data

---

## Cost Estimates

### Railway
- Hobby: $5/month (500 hours)
- Pro: $20/month (unlimited)
- Good for: Small to medium traffic

### Heroku
- Hobby: $7/month (1 dyno)
- Standard: $25-50/month
- Performance: $250-500/month

### Google Cloud Run
- Pay per request
- ~$0.00002400 per request
- Free tier: 2 million requests/month

---

## Support

For deployment issues:
- Railway: https://railway.app/help
- Check application logs
- Review health check endpoint
- Verify all files are deployed

---

**Last Updated**: 2025-01-17
**Backend Version**: 1.0.0
