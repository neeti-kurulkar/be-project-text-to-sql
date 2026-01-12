import { Download } from 'lucide-react';
import { type QueryResult } from '../../types/query';
import { exportToCSV } from '../../utils/exportCSV';
import { Button } from '../common/Button';

interface QueryResultsProps {
  results: QueryResult;
}

export function QueryResults({ results }: QueryResultsProps) {
  const handleExport = () => {
    exportToCSV(results.rows, `query-results-${Date.now()}`);
  };

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-ocean-600 dark:text-slate-400">
          {results.rowCount} row{results.rowCount !== 1 ? 's' : ''} returned
        </p>
        <Button
          variant="outline"
          size="sm"
          onClick={handleExport}
          className="flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </Button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-ocean-700">
        <table className="min-w-full divide-y divide-slate-200 dark:divide-ocean-700">
          <thead className="bg-slate-50 dark:bg-ocean-800">
            <tr>
              {results.columns.map((column) => (
                <th
                  key={column}
                  className="px-4 py-3 text-left text-xs font-semibold text-ocean-900 dark:text-slate-100 uppercase tracking-wider"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-ocean-900 divide-y divide-slate-200 dark:divide-ocean-700">
            {results.rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={rowIndex % 2 === 0 ? '' : 'bg-slate-50 dark:bg-ocean-800/50'}
              >
                {results.columns.map((column) => (
                  <td
                    key={column}
                    className="px-4 py-3 text-sm text-ocean-900 dark:text-slate-100 whitespace-nowrap"
                  >
                    {row[column] ?? '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
