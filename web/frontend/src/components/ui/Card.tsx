import React from 'react';
import { cn } from '../../lib/utils';
import { Button } from './Button';
import { FileInfo, TaskStatus } from '../../lib/types';
import { getFileDownloadUrl } from '../../lib/api';

// Card container
const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-lg border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md',
      className
    )}
    {...props}
  />
));
Card.displayName = 'Card';

// Card header
const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-4', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

// Card title
const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-lg font-semibold', className)}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

// Card description
const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-500', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

// Card content
const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-4 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

// Card footer
const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-4 pt-0', className)}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

// Status badge for file cards
export interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: TaskStatus | string;
}

const StatusBadge = React.forwardRef<HTMLSpanElement, StatusBadgeProps>(
  ({ status, className, ...props }, ref) => {
    const statusStyles = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      processing: 'bg-blue-100 text-blue-800 border-blue-200',
      completed: 'bg-green-100 text-green-800 border-green-200',
      failed: 'bg-red-100 text-red-800 border-red-200',
    }[status as TaskStatus] || 'bg-gray-100 text-gray-800 border-gray-200';

    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold',
          statusStyles,
          className
        )}
        {...props}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  }
);
StatusBadge.displayName = 'StatusBadge';

// File preview card
export interface FileCardProps {
  file: FileInfo;
  onDownload?: (file: FileInfo) => void;
  status?: TaskStatus | string;
  className?: string;
}

const FileCard = React.forwardRef<HTMLDivElement, FileCardProps>(
  ({ file, onDownload, status = 'completed', className, ...props }, ref) => {
    const handleDownload = () => {
      if (onDownload) {
        onDownload(file);
      } else {
        window.open(file.url || getFileDownloadUrl(file.id), '_blank');
      }
    };

    const formatFileSize = (bytes: number) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Different icon based on file format
    const renderFormatIcon = () => {
      switch (file.format.toLowerCase()) {
        case 'png':
          return (
            <svg className="h-8 w-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14 8V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2v-2" />
            </svg>
          );
        case 'svg':
          return (
            <svg className="h-8 w-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
            </svg>
          );
        case 'pdf':
          return (
            <svg className="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          );
        default:
          return (
            <svg className="h-8 w-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          );
      }
    };

    return (
      <Card ref={ref} className={cn('w-full', className)} {...props}>
        <CardHeader className="flex-row items-start justify-between space-y-0 pb-2">
          <div className="flex items-center space-x-2">
            {renderFormatIcon()}
            <div>
              <CardTitle className="text-base">{file.name}</CardTitle>
              <CardDescription className="text-xs">{file.format.toUpperCase()} • {formatFileSize(file.size)}</CardDescription>
            </div>
          </div>
          <StatusBadge status={status} />
        </CardHeader>
        <CardContent>
          {file.format.toLowerCase() === 'png' && file.url && (
            <div className="overflow-hidden rounded border border-gray-200 bg-gray-50">
              <img 
                src={file.url} 
                alt={file.name} 
                className="h-32 w-full object-contain" 
              />
            </div>
          )}
        </CardContent>
        <CardFooter className="justify-between">
          <Button 
            size="sm" 
            variant="outline"
            onClick={handleDownload}
            disabled={status === 'pending' || status === 'processing'}
          >
            <svg className="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download
          </Button>
        </CardFooter>
      </Card>
    );
  }
);
FileCard.displayName = 'FileCard';

export { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter,
  FileCard,
  StatusBadge
};

