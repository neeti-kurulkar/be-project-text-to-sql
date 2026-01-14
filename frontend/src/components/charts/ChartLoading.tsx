import { Loader2 } from 'lucide-react';

export function ChartLoading() {
  return (
    <div className="h-80 flex items-center justify-center">
      <div className="flex flex-col items-center gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <p className="text-sm text-ocean-600 dark:text-slate-400">Loading chart data...</p>
      </div>
    </div>
  );
}
