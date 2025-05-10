import React from 'react';
import { cn } from '../../lib/utils';

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  showValue?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'primary' | 'secondary';
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, max = 100, showValue = false, size = 'md', variant = 'primary', ...props }, ref) => {
    const percentage = Math.min(Math.max(0, (value / max) * 100), 100);
    
    const sizeClasses = {
      sm: 'h-1',
      md: 'h-2',
      lg: 'h-3',
    }[size];

    const variantClasses = {
      default: 'bg-gray-200 dark:bg-gray-700',
      primary: 'bg-primary/20',
      secondary: 'bg-secondary/20',
    }[variant];
    
    const indicatorVariantClasses = {
      default: 'bg-gray-500 dark:bg-gray-400',
      primary: 'bg-primary',
      secondary: 'bg-secondary',
    }[variant];
    
    return (
      <div ref={ref} className={cn('relative overflow-hidden', sizeClasses, variantClasses, className)} {...props}>
        <div
          className={cn(
            'h-full w-full flex-1 transition-all', 
            indicatorVariantClasses,
            percentage > 0 ? 'animate-progress-fill' : ''
          )}
          style={{ width: `${percentage}%` }}
        />
        {showValue && (
          <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
            {Math.round(percentage)}%
          </div>
        )}
      </div>
    );
  }
);

Progress.displayName = 'Progress';

export { Progress };

