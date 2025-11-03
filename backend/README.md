# Lohnkonto Data Extraction Backend

FastAPI backend for processing employee data from PDF documents.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. **IMPORTANT**: Place your Excel template file in the backend directory:
   - The template should be named `template.xlsx` (or update `TEMPLATE_PATH` in `.env`)
   - This template is used to generate the output Excel files

4. Run the server:
```bash
python api.py
```

Or with uvicorn:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/process-document
Upload and process a PDF document.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
- Success: Excel file (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
- Error: JSON with error details

**Example using curl:**
```bash
curl -X POST \
  -F "file=@employee_data.pdf" \
  http://localhost:8000/api/process-document \
  -o output.xlsx
```

### GET /health
Health check endpoint.

Returns:
```json
{
  "status": "healthy",
  "template_exists": true,
  "template_path": "template.xlsx"
}
```

### GET /
API information and available endpoints.

## Environment Variables

- `TEMPLATE_PATH`: Path to the Excel template file (default: `template.xlsx`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins (default: `*`)
  - For development: `http://localhost:5173,http://localhost:3000`
  - For production: Your frontend URL(s)

## Development

The backend uses the existing PDF processing logic from `main.py` and exposes it via a REST API.

## CORS

CORS is now configured via the `ALLOWED_ORIGINS` environment variable. Update it in your `.env` file or Railway environment variables to match your frontend URL.

## Deployment to Railway

### Prerequisites
1. Install Railway CLI: `npm i -g @railway/cli`
2. Login to Railway: `railway login`
3. Make sure your `template.xlsx` file is in the backend directory

### Deployment Steps

1. **Initialize Railway Project** (if not already done):
```bash
cd backend
railway init
```

2. **Link to existing project** (if already created on Railway):
```bash
railway link
```

3. **Set Environment Variables in Railway**:
Go to your Railway project dashboard and set:
- `TEMPLATE_PATH=template.xlsx`
- `ALLOWED_ORIGINS=https://your-frontend-url.vercel.app` (or your actual frontend URL)
- Railway automatically sets `PORT` - no need to configure

4. **Deploy**:
```bash
railway up
```

Or push via Git (if connected to GitHub):
```bash
git add .
git commit -m "Deploy to Railway"
git push
```

### Important Notes for Railway Deployment

- Railway will automatically detect the `Procfile` and use it to start the server
- Make sure `template.xlsx` is committed to your repository
- The `python-dotenv` package is required and included in `requirements.txt`
- Check Railway logs if issues occur: `railway logs`
- Update CORS origins after deploying frontend: Set `ALLOWED_ORIGINS` in Railway dashboard

### Testing Your Railway Deployment

After deployment, test your API:
```bash
# Health check
curl https://lohnkontodataextraction-production.up.railway.app/health

# Get API info
curl https://lohnkontodataextraction-production.up.railway.app/
```
