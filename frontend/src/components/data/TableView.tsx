import { useState } from 'react';
import { Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { exportToCSV } from '../../utils/exportCSV';
import { Button } from '../common/Button';

interface TableViewProps {
  tableName: string;
  data: any[];
  totalRows: number;
}

const ROWS_PER_PAGE = 50;

export function TableView({ tableName, data, totalRows }: TableViewProps) {
  const [currentPage, setCurrentPage] = useState(1);

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-ocean-600 dark:text-slate-400">
        No data available
      </div>
    );
  }

  const columns = Object.keys(data[0]);
  const totalPages = Math.ceil(totalRows / ROWS_PER_PAGE);
  const startRow = (currentPage - 1) * ROWS_PER_PAGE + 1;
  const endRow = Math.min(currentPage * ROWS_PER_PAGE, totalRows);

  const handleExport = () => {
    exportToCSV(data, `${tableName}-${Date.now()}`);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-ocean-600 dark:text-slate-400">
          Showing {startRow} to {endRow} of {totalRows.toLocaleString()} rows
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
              {columns.map((column) => (
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
            {data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={rowIndex % 2 === 0 ? '' : 'bg-slate-50 dark:bg-ocean-800/50'}
              >
                {columns.map((column) => (
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

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="flex items-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>
          <span className="text-sm text-ocean-600 dark:text-slate-400">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="flex items-center gap-2"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
