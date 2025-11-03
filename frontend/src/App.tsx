import { useState, useRef } from 'react';
import { Upload, Download, FileText, CheckCircle2, Loader2 } from 'lucide-react';

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'complete';

function App() {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [fileName, setFileName] = useState('');
  const [processedFileUrl, setProcessedFileUrl] = useState<string>('');
  const [processedFileName, setProcessedFileName] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const processFile = (file: File) => {
    setFileName(file.name);
    uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setUploadStatus('uploading');
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    // Get API URL from environment variable
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Use XMLHttpRequest for upload progress tracking
    const xhr = new XMLHttpRequest();

    // Track upload progress
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        setProgress(percentComplete);
      }
    });

    // Handle upload completion
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        // Upload complete, now processing in backend
        setUploadStatus('processing');
        setProgress(0);

        // The response should contain the processed file
        try {
          const blob = xhr.response;
          const url = URL.createObjectURL(blob);

          // Get filename from Content-Disposition header
          const contentDisposition = xhr.getResponseHeader('Content-Disposition');
          let excelFileName = 'processed_data.xlsx';

          if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
            if (filenameMatch && filenameMatch[1]) {
              excelFileName = filenameMatch[1].replace(/"/g, '');
            }
          }

          setProcessedFileUrl(url);
          setProcessedFileName(excelFileName);
          setUploadStatus('complete');
          setProgress(100);
        } catch (error) {
          console.error('Error processing response:', error);
          alert('Failed to process the file. Please try again.');
          handleReset();
        }
      } else {
        console.error('Upload failed:', xhr.status, xhr.statusText);

        // Try to parse error message from response
        try {
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const errorData = JSON.parse(reader.result as string);
              alert(`Upload failed: ${errorData.detail || xhr.statusText}`);
            } catch {
              alert(`Upload failed (${xhr.status}): ${xhr.statusText}`);
            }
          };
          reader.readAsText(xhr.response);
        } catch {
          alert(`Upload failed (${xhr.status}): ${xhr.statusText}`);
        }

        handleReset();
      }
    });

    // Handle errors
    xhr.addEventListener('error', () => {
      console.error('Upload error');
      alert('Upload failed. Please check your connection and try again.');
      handleReset();
    });

    // Configure and send request
    xhr.responseType = 'blob';
    xhr.open('POST', `${apiUrl}/api/process-document`);
    xhr.send(formData);
  };

  const handleDownload = () => {
    if (processedFileUrl && processedFileName) {
      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = processedFileUrl;
      link.download = processedFileName;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();

      // Clean up
      setTimeout(() => {
        document.body.removeChild(link);
      }, 100);
    }
  };

  const handleReset = () => {
    setUploadStatus('idle');
    setProgress(0);
    setFileName('');
    setProcessedFileName('');
    if (processedFileUrl) {
      URL.revokeObjectURL(processedFileUrl);
      setProcessedFileUrl('');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Lohnkonten Data Extraction
          </h1>
          <p className="text-gray-600">
            Upload a PDF to extract and process employee data
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-lg shadow-md p-8">

          {/* Upload Area */}
          {uploadStatus === 'idle' && (
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onClick={handleUploadClick}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf"
                onChange={handleFileSelect}
              />

              <div className="flex flex-col items-center gap-4">
                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>

                <div>
                  <p className="text-lg font-medium text-gray-900 mb-1">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-sm text-gray-500">
                    PDF files only
                  </p>
                </div>

                <button
                  type="button"
                  className="mt-5 px-10 py-8 bg-blue-700 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUploadClick();
                  }}
                >
                  Select File
                </button>
              </div>
            </div>
          )}

          {/* Processing State */}
          {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-blue-600" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{fileName}</p>
                  <p className="text-sm text-gray-500">
                    {uploadStatus === 'uploading' ? 'Uploading...' : 'Processing...'}
                  </p>
                </div>
                <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
              </div>

              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600">
                    {uploadStatus === 'uploading' ? 'Upload' : 'Processing'} Progress
                  </span>
                  <span className="font-medium text-blue-600">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Success State */}
          {uploadStatus === 'complete' && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
                <div className="flex-1">
                  <p className="font-medium text-green-900">Processing Complete!</p>
                  <p className="text-sm text-green-700">Your file is ready to download</p>
                </div>
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-4">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{processedFileName}</p>
                    <p className="text-sm text-gray-500">Excel Spreadsheet</p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleDownload}
                    className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 font-medium"
                  >
                    <Download className="w-5 h-5" />
                    Download File
                  </button>

                  <button
                    onClick={handleReset}
                    className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                  >
                    Upload Another
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;
