import React from 'react';

function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className="flex items-center justify-center">
      <div className="flex items-center space-x-2">
        <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-green-600 ${sizeClasses[size]}`}></div>
        {text && <span className="text-sm text-gray-600">{text}</span>}
      </div>
    </div>
  );
}

export default LoadingSpinner;
