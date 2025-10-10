import { useState } from 'react';
import QueryInput from './components/QueryInpuut';
import ResultsDisplay from './components/ResultsDisplay';
import SampleQuestions from './components/SampleQuestions';
import type { AnalysisResult } from './types';

function App() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (question: string, enableVisualization: boolean) => {
    setLoading(true);
    setAnalysisResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          enable_visualization: enableVisualization,
        }),
      });

      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Error analyzing question:', error);
      setAnalysisResult({
        analysis_id: '',
        question,
        sql_query: null,
        results: null,
        columns: null,
        row_count: 0,
        insights: null,
        summary: null,
        visualizations: null,
        error: 'Failed to connect to the server',
        status: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                HUL Financial Analysis
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                AI-powered financial data analysis with intelligent visualization
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">System Active</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Query Input Section */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <QueryInput onAnalyze={handleAnalyze} loading={loading} />
          </div>

          {/* Sample Questions */}
          {!analysisResult && !loading && (
            <SampleQuestions onSelectQuestion={(q) => handleAnalyze(q, true)} />
          )}

          {/* Loading State */}
          {loading && (
            <div className="bg-white rounded-lg shadow-md p-12">
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
                  <div className="w-16 h-16 border-4 border-blue-600 rounded-full absolute top-0 left-0 animate-spin border-t-transparent"></div>
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Analyzing Your Question
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    Our AI agents are working on your request...
                  </p>
                  <div className="mt-4 space-y-2 text-xs text-gray-400">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <span>Generating SQL query</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce delay-75"></div>
                      <span>Executing database query</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-150"></div>
                      <span>Generating insights</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce delay-200"></div>
                      <span>Creating visualizations</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results Display */}
          {analysisResult && !loading && (
            <ResultsDisplay result={analysisResult} />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>© 2025 HUL Financial Analysis System</p>
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>4 AI Agents Active</span>
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;