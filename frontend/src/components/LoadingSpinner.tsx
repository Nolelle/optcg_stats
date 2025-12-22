interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

export function LoadingSpinner({ size = 'md' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex items-center justify-center">
      <div
        className={`
          ${sizeClasses[size]}
          border-2 border-indigo-500/30 border-t-indigo-500
          rounded-full animate-spin
        `}
      />
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <LoadingSpinner size="lg" />
      <p className="text-gray-400">Loading...</p>
    </div>
  );
}

