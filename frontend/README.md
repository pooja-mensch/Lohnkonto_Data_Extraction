# Lohnkonto Data Extraction Frontend

React + TypeScript + Vite frontend for uploading and processing employee data documents.

## Features

- **Drag & Drop Upload**: Drag and drop PDF files or click to upload
- **Progress Tracking**: Real-time upload and processing progress bars
- **Download Results**: Download processed Excel files
- **Responsive Design**: Clean, modern UI with Tailwind CSS

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure the API URL:
   - For **development**: Use `.env.local` (already configured)
     ```
     VITE_API_URL=http://localhost:8000
     ```
   - For **production**: Use `.env.production` (already configured with Railway backend)
     ```
     VITE_API_URL=https://lohnkontodataextraction-production.up.railway.app
     ```

3. Run the development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

The production build will use the `VITE_API_URL` from `.env.production`.

## Environment Variables

- `VITE_API_URL`: Backend API URL
  - Development (`.env.local`): `http://localhost:8000`
  - Production (`.env.production`): `https://lohnkontodataextraction-production.up.railway.app`

## Supported File Formats

Currently supported:
- PDF files (.pdf)

Note: The backend processes PDF documents and returns Excel files (.xlsx).

## Development

The frontend is built with:
- React 19
- TypeScript
- Vite
- Tailwind CSS
- Lucide React (icons)

## API Integration

The frontend communicates with the backend via:
- Endpoint: `POST ${VITE_API_URL}/api/process-document`
- Upload tracking using XMLHttpRequest for progress updates
- File download using Blob URLs
