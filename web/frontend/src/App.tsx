import { useState } from 'react'
import { Button } from './components/ui/Button'

function App() {
  const [isLoading, setIsLoading] = useState(false)

  const handleClick = () => {
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <h1 className="text-3xl font-bold mb-6">GPX Art Generator</h1>
      <div className="flex space-x-4 mb-8">
        <Button 
          variant="default" 
          onClick={handleClick}
          isLoading={isLoading}
        >
          Default Button
        </Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
      </div>
      
      <div className="flex space-x-4">
        <Button size="sm">Small</Button>
        <Button size="md">Medium</Button>
        <Button size="lg">Large</Button>
      </div>
    </div>
  )
}

export default App

import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import { GenerateResponse, GenerationResult, FileInfo } from './lib/types';
import { getFileDownloadUrl } from './lib/api';
import { Button } from './components/ui/Button';

const App: React.FC = () => {
  // State for generation results
  const [result, setResult] = useState<GenerationResult>({
    isLoading: false,
    data: undefined,
    error: undefined,
  });

  // Handle successful generation
  const handleSuccess = (response: GenerateResponse) => {
    setResult({
      isLoading: false,
      data: response,
      error: undefined,
    });
  };

  // Handle errors
  const handleError = (error: Error) => {
    setResult({
      isLoading: false,
      data: undefined,
      error: error.message,
    });
  };

  // Reset the form and results
  const handleReset = () => {
    setResult({
      isLoading: false,
      data: undefined,
      error: undefined,
    });
  };

  // Render a file preview card
  const renderFilePreview = (file: FileInfo) => {
    return (
      <div key={file.id} className="flex flex-col border rounded-lg overflow-hidden bg-white shadow-sm">
        {file.format === 'png' && (
          <div className="p-2 flex justify-center bg-gray-50 border-b">
            <img 
              src={getFileDownloadUrl(file.id)} 
              alt={file.name} 
              className="max-h-64 object-contain"
            />
          </div>
        )}
        
        <div className="p-4 flex flex-col">
          <h3 className="font-medium">{file.name}</h3>
          <span className="text-sm text-gray-500 mb-2">{(file.size / 1024).toFixed(1)} KB</span>
          
          <div className="mt-auto pt-2">
            <a 
              href={getFileDownloadUrl(file.id)} 
              download={file.name}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Download {file.format.toUpperCase()}
            </a>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">GPX Art Generator</h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {!result.data ? (
            <div className="bg-white shadow rounded-lg p-6">
              {result.error && (
                <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                  <h3 className="font-medium">Error</h3>
                  <p>{result.error}</p>
                </div>
              )}
              
              <UploadForm 
                onSuccess={handleSuccess} 
                onError={handleError} 
              />
            </div>
          ) : (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-900">Generated Artwork</h2>
                  <Button 
                    variant="secondary" 
                    onClick={handleReset}
                  >
                    Create New
                  </Button>
                </div>
                
                {result.data.status === 'completed' ? (
                  <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {result.data.files.map(renderFilePreview)}
                  </div>
                ) : result.data.status === 'failed' ? (
                  <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                    <h3 className="font-medium">Generation Failed</h3>
                    <p>{result.data.message || 'An unknown error occurred'}</p>
                  </div>
                ) : (
                  <div className="mt-4 flex flex-col items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p className="text-gray-600">Processing your GPX file...</p>

