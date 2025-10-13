import { useState } from 'react';
import QueryInput from '../components/QueryInpuut';
import ResultsDisplay from '../components/ResultsDisplay';
import SampleQuestions from '../components/SampleQuestions';
import type { AnalysisResult } from '../types';

const AskQuestionPage = () => {
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-6">
        {/* Page Header */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Ask a Question
          </h1>
          <p className="text-gray-600">
            Query HUL's financial data using natural language. Get instant SQL generation, data results, and AI-powered insights.
          </p>
        </div>

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
    </div>
  );
};

export default AskQuestionPage;
