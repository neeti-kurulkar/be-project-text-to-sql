import { AlertCircle, RefreshCw } from 'lucide-react';

interface ChartErrorProps {
  message: string;
  onRetry?: () => void;
}

export function ChartError({ message, onRetry }: ChartErrorProps) {
  return (
    <div className="h-80 flex items-center justify-center">
      <div className="flex flex-col items-center gap-3 text-center">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <p className="text-sm text-red-600 dark:text-red-400">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
