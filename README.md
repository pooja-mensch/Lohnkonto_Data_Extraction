# Lohnkonto Data Extraction

Full-stack application for extracting and processing employee data from PDF documents.

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── api.py       # API server
│   ├── main.py      # PDF processing logic
│   ├── classes.py   # Data classes
│   ├── data_extractors/  # Data extraction modules
│   └── meta_detectors/   # Meta information detectors
│
└── frontend/        # React + TypeScript frontend
    ├── src/
    │   ├── App.tsx  # Main application component
    │   └── ...
    └── package.json
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Excel template file (required for backend)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. **IMPORTANT**: Place your Excel template file (`template.xlsx`) in the backend directory

5. Start the backend server:
```bash
python api.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Update `.env` file with backend URL:
```env
VITE_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

## Usage

1. Open the frontend in your browser
2. Upload a PDF document by:
   - Clicking "Upload Document" button
   - Or dragging and dropping a file
3. Wait for the upload and processing to complete
4. Download the processed Excel file

## Features

### Backend
- FastAPI REST API
- PDF processing with multiple format support
- Excel file generation
- Progress tracking
- Error handling

### Frontend
- Modern, responsive UI
- Drag & drop file upload
- Real-time upload/processing progress
- File download management
- Error notifications

## API Documentation

Once the backend is running, visit:
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Production Deployment

### Backend
- Update CORS settings in `api.py` to allow only your frontend domain
- Set environment variables for `TEMPLATE_PATH`, `HOST`, and `PORT`
- Use a production ASGI server (uvicorn with workers)

### Frontend
- Update `VITE_API_URL` in `.env` to your production backend URL
- Build the frontend: `npm run build`
- Serve the `dist` folder with a static file server

## Troubleshooting

### Backend Issues

**Template not found:**
- Ensure `template.xlsx` exists in the backend directory
- Check `TEMPLATE_PATH` in `.env`

**Port already in use:**
- Change `PORT` in `.env`
- Or specify port when running: `python api.py`

### Frontend Issues

**CORS errors:**
- Verify backend CORS settings allow your frontend URL
- Check that `VITE_API_URL` is correct

**Upload fails:**
- Check backend is running and accessible
- Verify file format is supported (.pdf)
- Check browser console for detailed errors

## License

[Your License Here]
