import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { generateArtwork } from '../lib/api';
import { GenerateOptions, GenerateResponse, GPXUploadFormData } from '../lib/types';
import { validateGpxFile, formatFileSize } from '../lib/utils';
import { Button } from './ui/Button';

interface UploadFormProps {
  onSuccess: (response: GenerateResponse) => void;
  onError: (error: Error) => void;
}

const initialOptions: GenerateOptions = {
  color: '#0066CC',
  background: '#FFFFFF',
  thickness: 'medium',
  style: 'solid',
  markers: false,
  markers_unit: 'km',
  overlay: ['name', 'distance'],
  overlay_position: 'top-right',
  formats: ['png'],
};

const UploadForm: React.FC<UploadFormProps> = ({ onSuccess, onError }) => {
  // State
  const [formData, setFormData] = useState<GPXUploadFormData>({
    file: null,
    options: initialOptions,
  });
  const [loading, setLoading] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);

  // File handling
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      const validation = validateGpxFile(file);
      
      if (!validation.valid) {
        setFileError(validation.message || 'Invalid file');
        return;
      }
      
      setFormData((prev) => ({ ...prev, file }));
      setFileError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/gpx+xml': ['.gpx'],
      'text/xml': ['.gpx'],
    },
    maxFiles: 1,
  });

  // Option changes
  const handleOptionChange = useCallback(
    (key: keyof GenerateOptions, value: any) => {
      setFormData((prev) => ({
        ...prev,
        options: {
          ...prev.options,
          [key]: value,
        },
      }));
    },
    []
  );

  // Form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.file) {
      setFileError('Please select a GPX file to upload');
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await generateArtwork(formData.file, formData.options);
      onSuccess(response);
    } catch (error) {
      onError(error as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Upload Area */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          GPX File
        </label>
        
        <div
          {...getRootProps()}
          className={
            isDragActive
              ? "border-2 border-dashed border-blue-500 bg-blue-50 p-6 rounded-lg cursor-pointer"
              : "border-2 border-dashed border-gray-300 p-6 rounded-lg cursor-pointer hover:bg-gray-50"
          }
        >
          <input {...getInputProps()} />
          
          <div className="text-center">
            {formData.file ? (
              <div className="space-y-1">
                <p className="text-sm font-semibold">{formData.file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(formData.file.size)}</p>
              </div>
            ) : (
              <div>
                <p className="text-sm">
                  {isDragActive 
                    ? "Drop your GPX file here..." 
                    : "Drag & drop your GPX file here, or click to browse"}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Only .gpx files are supported
                </p>
              </div>
            )}
          </div>
        </div>
        
        {fileError && (
          <p className="text-red-500 text-sm mt-1">{fileError}</p>
        )}
      </div>
      
      {/* Form sections for options */}
      <div className="space-y-6 bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Artwork Options</h3>
        
        {/* Format Options */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Export Formats
          </label>
          <div className="flex flex-wrap gap-2">
            {['png', 'svg', 'pdf'].map((format) => (
              <label key={format} className="inline-flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  checked={formData.options.formats.includes(format as 'png' | 'svg' | 'pdf')}
                  onChange={(e) => {
                    const formats = e.target.checked
                      ? [...formData.options.formats, format as 'png' | 'svg' | 'pdf']
                      : formData.options.formats.filter(f => f !== format);
                    handleOptionChange('formats', formats);
                  }}
                />
                <span className="ml-2 text-sm text-gray-700 uppercase">{format}</span>
              </label>
            ))}
          </div>
        </div>
        
        {/* Color Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Track Color
            </label>
            <div className="flex items-center">
              <input
                type="color"
                className="h-10 w-10 border border-gray-300 rounded"
                value={formData.options.color}
                onChange={(e) => handleOptionChange('color', e.target.value)}
              />
              <span className="ml-2 text-sm text-gray-600">{formData.options.color}</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Background Color
            </label>
            <div className="flex items-center">
              <input
                type="color"
                className="h-10 w-10 border border-gray-300 rounded"
                value={formData.options.background}
                onChange={(e) => handleOptionChange('background', e.target.value)}
              />
              <span className="ml-2 text-sm text-gray-600">{formData.options.background}</span>
            </div>
          </div>
        </div>
        
        {/* Line Style Options */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Line Style
            </label>
            <select
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              value={formData.options.style}
              onChange={(e) => handleOptionChange('style', e.target.value)}
            >
              <option value="solid">Solid</option>
              <option value="dashed">Dashed</option>
              <option value="dotted">Dotted</option>
            </select>
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Line Thickness
            </label>
            <select
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              value={formData.options.thickness}
              onChange={(e) => handleOptionChange('thickness', e.target.value)}
            >
              <option value="thin">Thin</option>
              <option value="medium">Medium</option>
              <option value="thick">Thick</option>
            </select>
          </div>
        </div>
        
        {/* Markers Options */}
        <div className="space-y-2">
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="checkbox"
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                checked={formData.options.markers}
                onChange={(e) => handleOptionChange('markers', e.target.checked)}
                id="markers"
              />
            </div>
            <div className="ml-3 text-sm">
              <label htmlFor="markers" className="font-medium text-gray-700">Show Distance Markers</label>
              <p className="text-gray-500">Display markers at regular distances along the route</p>
            </div>
          </div>
          
          {formData.options.markers && (
            <div className="ml-7 mt-2">
              <label className="block text-sm font-medium text-gray-700">
                Markers Unit
              </label>
              <div className="mt-1 flex items-center space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio text-blue-600"
                    name="markers_unit"
                    value="km"
                    checked={formData.options.markers_unit === 'km'}
                    onChange={() => handleOptionChange('markers_unit', 'km')}
                  />
                  <span className="ml-2">Kilometers</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio text-blue-600"
                    name="markers_unit"
                    value="mi"
                    checked={formData.options.markers_unit === 'mi'}
                    onChange={() => handleOptionChange('markers_unit', 'mi')}
                  />
                  <span className="ml-2">Miles</span>
                </label>
              </div>
              
              <div className="mt-2">
                <label className="block text-sm font-medium text-gray-700">
                  Markers Frequency
                </label>
                <div className="mt-1 flex items-center space-x-2">
                  <input
                    type="number"
                    className="w-24 rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    min="1"
                    max="50"
                    value={formData.options.markers_frequency || 1}
                    onChange={(e) => handleOptionChange('markers_frequency', parseInt(e.target.value, 10))}
                  />
                  <span className="text-sm text-gray-600">
                    {formData.options.markers_unit} between markers
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Overlay Options */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            Overlay Information
          </label>
          <div className="flex flex-wrap gap-2">
            {['name', 'distance', 'elevation'].map((overlay) => (
              <label key={overlay} className="inline-flex items-center">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  checked={formData.options.overlay?.includes(overlay)}
                  onChange={(e) => {
                    const overlays = e.target.checked
                      ? [...(formData.options.overlay || []), overlay]
                      : (formData.options.overlay || []).filter(o => o !== overlay);
                    handleOptionChange('overlay', overlays);
                  }}
                />
                <span className="ml-2 text-sm text-gray-700 capitalize">{overlay}</span>
              </label>
            ))}
          </div>
          
          <div className="mt-3">
            <label className="block text-sm font-medium text-gray-700">
              Overlay Position
            </label>
            <select
              className="mt-1 w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              value={formData.options.overlay_position || 'top-right'}
              onChange={(e) => handleOptionChange('overlay_position', e.target.value)}
            >
              <option value="top-left">Top Left</option>
              <option value="top-right">Top Right</option>
              <option value="bottom-left">Bottom Left</option>
              <option value="bottom-right">Bottom Right</option>
            </select>
          </div>
        </div>
        
        {/* Advanced Options */}
        <div className="space-y-2">
          <details className="group">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 flex items-center">
              <span>Advanced Options</span>
              <svg
                className="ml-1 h-4 w-4 text-gray-500 group-open:rotate-180 transition-transform"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            
            <div className="mt-3 space-y-4 pl-3 border-l-2 border-gray-100">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  DPI (for raster formats)
                </label>
                <input
                  type="number"
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  min="72"
                  max="600"
                  step="1"
                  value={formData.options.dpi || 300}
                  onChange={(e) => handleOptionChange('dpi', parseInt(e.target.value, 10))}
                />
              </div>
              
              <div className="space-y-2">
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      type="checkbox"
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      checked={formData.options.simplify}
                      onChange={(e) => handleOptionChange('simplify', e.target.checked)}
                      id="simplify"
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="simplify" className="font-medium text-gray-700">Simplify Route</label>
                    <p className="text-gray-500">Reduce the number of points for smoother output</p>
                  </div>
                </div>
                
                {formData.options.simplify && (
                  <div className="ml-7 mt-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Simplification Tolerance
                    </label>
                    <input
                      type="range"
                      className="w-full"
                      min="0.0001"
                      max="0.01"
                      step="0.0001"
                      value={formData.options.simplify_tolerance || 0.0005}
                      onChange={(e) => handleOptionChange('simplify_tolerance', parseFloat(e.target.value))}
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>More Details</span>
                      <span>Less Details</span>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Padding (%)
                </label>
                <input
                  type="number"
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  min="0"
                  max="30"
                  value={formData.options.padding || 5}
                  onChange={(e) => handleOptionChange('padding', parseInt(e.target.value, 10))}
                />
              </div>
            </div>
          </details>
        </div>
      </div>
      
      {/* Submit Button */}
      <div className="flex justify-end">
        <Button
          type="submit"
          variant="default"
          size="lg"
          isLoading={loading}
          disabled={!formData.file || loading}
        >
          Generate Artwork
        </Button>
      </div>
    </form>
  );
};

export default UploadForm;

