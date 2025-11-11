import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import TextParser from './TextParser';

const UploadPanel = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [mode, setMode] = useState('upload'); // 'upload' | 'parse'

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check if it's a PDF
    if (file.type !== 'application/pdf') {
      setUploadStatus({
        type: 'error',
        message: 'Please upload a PDF file'
      });
      return;
    }

    setUploading(true);
    setUploadStatus(null);

    try {
      // Simulate upload process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setUploadStatus({
        type: 'success',
        message: 'Question paper uploaded successfully! Processing will start shortly.'
      });
      
      // Reset file input
      event.target.value = '';
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: 'Upload failed. Please try again.'
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 border-b">
        <h2 className="text-xl font-semibold text-gray-900">Upload Question Papers</h2>
        <p className="text-gray-600 mt-1">
          Upload SSC question papers in PDF format to add them to the search database
        </p>
      </div>

      <div className="p-6">
        {/* Mode Toggle */}
        <div className="mb-4 flex items-center space-x-3" role="tablist" aria-label="Upload or Quick Parse">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'upload'}
            onClick={() => setMode('upload')}
            className={`px-3 py-1 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
              mode === 'upload' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'
            }`}
          >
            Upload PDF
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'parse'}
            onClick={() => setMode('parse')}
            className={`px-3 py-1 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
              mode === 'parse' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'
            }`}
          >
            Quick Parse
          </button>
        </div>

        {/* Upload Area */}
        <div className={`${mode === 'upload' ? '' : 'hidden'}`}>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors">
          <input
            type="file"
            id="file-upload"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
          
          <label
            htmlFor="file-upload"
            className="cursor-pointer block"
          >
            <div className="flex flex-col items-center space-y-4">
              {uploading ? (
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              ) : (
                <Upload className="h-12 w-12 text-gray-400" />
              )}
              
              <div>
                <p className="text-lg font-medium text-gray-900">
                  {uploading ? 'Uploading...' : 'Upload PDF File'}
                </p>
                <p className="text-gray-600 mt-1">
                  Drag and drop or click to browse
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Supported format: PDF (Max 10MB)
                </p>
              </div>
            </div>
          </label>
        </div>

          {/* Upload Status */}
          {uploadStatus && (
          <div className={`mt-4 p-4 rounded-lg ${
            uploadStatus.type === 'success' 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center space-x-2">
              {uploadStatus.type === 'success' ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600" />
              )}
              <span className={
                uploadStatus.type === 'success' 
                  ? 'text-green-800' 
                  : 'text-red-800'
              }>
                {uploadStatus.message}
              </span>
            </div>
          </div>
          )}
        </div>

        {/* Quick Parse (manual text input) */}
        <div className={`${mode === 'parse' ? '' : 'hidden'} mt-2`}>
          <TextParser />
        </div>

        {/* Instructions */}
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">How it works:</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <FileText className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Upload PDF</h4>
              <p className="text-sm text-gray-600 mt-1">
                Upload your SSC question papers in PDF format
              </p>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="h-8 w-8 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-white text-sm font-bold">AI</span>
              </div>
              <h4 className="font-medium text-gray-900">AI Processing</h4>
              <p className="text-sm text-gray-600 mt-1">
                Our system extracts and indexes all questions automatically
              </p>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Upload className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Ready to Search</h4>
              <p className="text-sm text-gray-600 mt-1">
                Questions become searchable within minutes
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPanel;
