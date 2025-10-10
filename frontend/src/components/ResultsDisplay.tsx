import { useState } from 'react';
import type { AnalysisResult } from '../types';
import { 
  AlertCircle, 
  CheckCircle, 
  Code, 
  Table as TableIcon, 
  Lightbulb, 
  BarChart3,
  Download,
  Eye,
  EyeOff
} from 'lucide-react';

interface ResultsDisplayProps {
  result: AnalysisResult;
}

const ResultsDisplay = ({ result }: ResultsDisplayProps) => {
  const [showSQL, setShowSQL] = useState(false);
  const [activeTab, setActiveTab] = useState<'data' | 'insights' | 'charts'>('data');

  if (result.status === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
            <p className="mt-1 text-sm text-red-700">{result.error}</p>
          </div>
        </div>
      </div>
    );
  }

  const exportToCSV = () => {
    if (!result.results) return;

    const headers = result.columns?.join(',') || '';
    const rows = result.results.map(row => 
      result.columns?.map(col => row[col]).join(',')
    ).join('\n');
    
    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis_${result.analysis_id}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <div>
            <p className="text-sm font-medium text-green-900">
              Analysis Complete
            </p>
            <p className="text-xs text-green-700 mt-0.5">
              Found {result.row_count} {result.row_count === 1 ? 'row' : 'rows'} of data
            </p>
          </div>
        </div>
      </div>

      {/* SQL Query Section */}
      {result.sql_query && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <button
            onClick={() => setShowSQL(!showSQL)}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <Code className="h-5 w-5 text-gray-600" />
              <span className="font-medium text-gray-900">Generated SQL Query</span>
            </div>
            {showSQL ? <EyeOff className="h-5 w-5 text-gray-400" /> : <Eye className="h-5 w-5 text-gray-400" />}
          </button>
          {showSQL && (
            <div className="px-6 pb-4">
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{result.sql_query}</code>
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('data')}
              className={`flex items-center space-x-2 px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'data'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <TableIcon className="h-5 w-5" />
              <span>Data Table</span>
              <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                {result.row_count}
              </span>
            </button>
            
            <button
              onClick={() => setActiveTab('insights')}
              className={`flex items-center space-x-2 px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'insights'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Lightbulb className="h-5 w-5" />
              <span>Insights</span>
            </button>
            
            {result.visualizations?.visualized && (
              <button
                onClick={() => setActiveTab('charts')}
                className={`flex items-center space-x-2 px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'charts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BarChart3 className="h-5 w-5" />
                <span>Visualizations</span>
                <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                  {result.visualizations.charts.length}
                </span>
              </button>
            )}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Data Tab */}
          {activeTab === 'data' && result.results && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <p className="text-sm text-gray-600">
                  Showing {result.row_count} {result.row_count === 1 ? 'row' : 'rows'}
                </p>
                <button
                  onClick={exportToCSV}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm"
                >
                  <Download className="h-4 w-4" />
                  <span>Export CSV</span>
                </button>
              </div>
              
              <div className="overflow-x-auto border border-gray-200 rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {result.columns?.map((col) => (
                        <th
                          key={col}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {result.results.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {result.columns?.map((col) => (
                          <td
                            key={col}
                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                          >
                            {typeof row[col] === 'number' 
                              ? row[col].toLocaleString(undefined, { maximumFractionDigits: 2 })
                              : row[col] ?? 'N/A'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Insights Tab */}
          {activeTab === 'insights' && result.insights && (
            <div className="prose max-w-none">
              {result.insights.split('\n').map((line, idx) => {
                // H2 headers (##)
                if (line.startsWith('## ')) {
                  return (
                    <h2 key={idx} className="text-xl font-bold text-gray-900 mt-6 mb-3 first:mt-0">
                      {line.replace('## ', '')}
                    </h2>
                  );
                }
                // H3 headers (###)
                if (line.startsWith('### ')) {
                  return (
                    <h3 key={idx} className="text-lg font-semibold text-gray-900 mt-4 mb-2">
                      {line.replace('### ', '')}
                    </h3>
                  );
                }
                // List items
                if (line.startsWith('- ')) {
                  const content = line.replace('- ', '');
                  // Handle bold text within list items
                  const parts = content.split(/(\*\*.*?\*\*)/g);
                  return (
                    <li key={idx} className="ml-6 mb-2 text-gray-700">
                      {parts.map((part, i) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                          return <strong key={i} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
                        }
                        return part;
                      })}
                    </li>
                  );
                }
                // Regular paragraphs
                if (line.trim() !== '') {
                  // Handle bold text in paragraphs
                  const parts = line.split(/(\*\*.*?\*\*)/g);
                  return (
                    <p key={idx} className="mb-3 text-gray-700 leading-relaxed">
                      {parts.map((part, i) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                          return <strong key={i} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
                        }
                        return part;
                      })}
                    </p>
                  );
                }
                // Empty lines (spacing)
                return <div key={idx} className="h-2" />;
              })}
            </div>
          )}

          {/* Charts Tab */}
          {activeTab === 'charts' && result.visualizations?.visualized && (
            <div className="space-y-6">
              {result.visualizations.charts.map((chart, idx) => (
                <div key={idx} className="space-y-3">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {chart.title}
                    </h3>
                    {chart.description && (
                      <p className="text-sm text-gray-600 mt-1">
                        {chart.description}
                      </p>
                    )}
                    <span className="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                      {chart.type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <div className="border border-gray-200 rounded-lg overflow-hidden bg-white p-4">
                    <img
                      src={`http://localhost:8000/api/chart/${chart.path.includes('/') || chart.path.includes('\\') ? chart.path.split(/[/\\]/).pop() : chart.path}`}
                      alt={chart.title}
                      className="w-full h-auto"
                      onError={(e) => {
                        console.error('Failed to load chart:', chart.path);
                        e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="%23f3f4f6"/><text x="50%" y="50%" text-anchor="middle" fill="%236b7280">Image not available</text></svg>';
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* No Visualization Message */}
          {activeTab === 'charts' && !result.visualizations?.visualized && (
            <div className="text-center py-12">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No Visualizations Created
              </h3>
              <p className="text-sm text-gray-600">
                {result.visualizations?.reason || 'Visualization was not needed for this query'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;