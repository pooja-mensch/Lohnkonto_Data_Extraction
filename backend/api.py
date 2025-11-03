import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from main import process_pdf

# Load environment variables
load_dotenv()

app = FastAPI(title="Lohnkonto Data Extraction API")

# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")] if allowed_origins_str != "*" else ["*"]

# Add CORS middleware to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the Excel template - convert to absolute path
TEMPLATE_PATH = os.path.abspath(os.getenv("TEMPLATE_PATH", "template.xlsx"))

@app.get("/")
async def root():
    return {
        "message": "Lohnkonto Data Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "/api/process-document": "POST - Upload and process PDF document"
        }
    }
@app.get("/api/data")
def get_data():
    return {"data": "This is from the API"}

@app.post("/api/process-document")
async def process_document(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None)
):
    """
    Process an uploaded PDF document and return the processed Excel file.

    Args:
        file: The PDF file to process
        password: Optional password for encrypted PDFs

    Returns:
        FileResponse: The processed Excel file
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp()
    pdf_path = None
    output_path = None

    try:
        # Save uploaded file temporarily
        pdf_path = os.path.join(temp_dir, file.filename)
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Check if template exists
        if not os.path.exists(TEMPLATE_PATH):
            raise HTTPException(
                status_code=500,
                detail=f"Template file not found at {TEMPLATE_PATH}. Please set TEMPLATE_PATH environment variable."
            )

        # Change to temp directory for processing (output files are created in current dir)
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        # Process the PDF
        try:
            output_filename, people_count, processing_time = process_pdf(pdf_path, TEMPLATE_PATH, password)
            output_path = os.path.join(temp_dir, output_filename)

            # Debug logging
            print(f"[DEBUG] Output filename: {output_filename}")
            print(f"[DEBUG] Output path: {output_path}")
            print(f"[DEBUG] Output file exists: {os.path.exists(output_path)}")
            print(f"[DEBUG] Files in temp dir: {os.listdir(temp_dir)}")

            # Check if output file was created
            if not os.path.exists(output_path):
                raise HTTPException(
                    status_code=500,
                    detail=f"Processing completed but output file was not created. Expected: {output_filename}"
                )

            # Verify it's an Excel file
            if not output_filename.endswith('.xlsx'):
                raise HTTPException(
                    status_code=500,
                    detail=f"Output file is not an Excel file: {output_filename}"
                )

            # Return the processed Excel file
            print(f"[DEBUG] Returning Excel file: {output_filename}")
            return FileResponse(
                path=output_path,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=output_filename,
                headers={
                    "X-Processing-Time": str(processing_time),
                    "X-People-Count": str(people_count),
                    "Content-Disposition": f'attachment; filename="{output_filename}"'
                }
            )

        finally:
            # Restore original directory
            os.chdir(original_dir)

    except ValueError as e:
        error_msg = str(e)
        # Check if this is an encryption error
        if "PDF is encrypted" in error_msg or "password" in error_msg.lower():
            raise HTTPException(
                status_code=401,  # Use 401 to indicate authentication (password) required
                detail={
                    "error": "password_required",
                    "message": error_msg
                }
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # Clean up temporary files
        try:
            if temp_dir and os.path.exists(temp_dir):
                # Don't delete immediately if we're returning the file
                # The file will be cleaned up after response is sent
                pass
        except Exception as e:
            print(f"Warning: Could not clean up temporary files: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "template_exists": os.path.exists(TEMPLATE_PATH),
        "template_path": TEMPLATE_PATH
    }

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print("=" * 60)
    print("Lohnkonto Data Extraction Backend")
    print("=" * 60)
    print(f"Server: http://{host}:{port}")
    print(f"API Docs: http://localhost:{port}/docs")
    print(f"Health Check: http://localhost:{port}/health")
    print("-" * 60)
    print(f"Template path (absolute): {TEMPLATE_PATH}")
    print(f"Template exists: {os.path.exists(TEMPLATE_PATH)}")

    if not os.path.exists(TEMPLATE_PATH):
        print("-" * 60)
        print("⚠️  WARNING: Template file not found!")
        print(f"   Please place your Excel template at: {os.path.abspath(TEMPLATE_PATH)}")
        print("   The template should contain:")
        print("   - Sheet: 'IST Gehälter' (for employee data)")
        print("   - Sheet: 'Projektübersicht' (for project overview)")
        print("-" * 60)
    else:
        print("✓ Template file found")
        print("-" * 60)

    print("\nStarting server...\n")

    uvicorn.run(app, host=host, port=port)
