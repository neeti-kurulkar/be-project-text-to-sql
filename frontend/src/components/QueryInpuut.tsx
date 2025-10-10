import { useState } from 'react';
import { Search, Settings } from 'lucide-react';

interface QueryInputProps {
  onAnalyze: (question: string, enableVisualization: boolean) => void;
  loading: boolean;
}

const QueryInput = ({ onAnalyze, loading }: QueryInputProps) => {
  const [question, setQuestion] = useState('');
  const [enableVisualization, setEnableVisualization] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim()) {
      onAnalyze(question, enableVisualization);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
          Ask a question about HUL's financial data
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="E.g., What is the revenue trend over the last 5 years?"
            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            disabled={loading}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="visualization"
            checked={enableVisualization}
            onChange={(e) => setEnableVisualization(e.target.checked)}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            disabled={loading}
          />
          <label htmlFor="visualization" className="text-sm text-gray-700 flex items-center space-x-1">
            <Settings className="h-4 w-4" />
            <span>Enable automatic visualization</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
        >
          {loading ? (
            <span className="flex items-center space-x-2">
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Analyzing...</span>
            </span>
          ) : (
            'Analyze'
          )}
        </button>
      </div>
    </form>
  );
};

export default QueryInput;