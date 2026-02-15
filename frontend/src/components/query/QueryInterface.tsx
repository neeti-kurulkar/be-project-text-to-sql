import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { type QueryMessage as QueryMessageType, type NL2SQLResponse } from '../../types/query';
import { type CachedQueryResponse } from '../../types/data';
import { processNaturalLanguageQuery } from '../../services/api';
import { QueryMessage } from './QueryMessage';
import { QueryInput } from './QueryInput';
import { SuggestedQuestions } from './SuggestedQuestions';
import { useQueryHistory } from '../../hooks/useQueryHistory';

export function QueryInterface() {
  const [messages, setMessages] = useState<QueryMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [initialQuestion, setInitialQuestion] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const { addQuery } = useQueryHistory();

  // Handle navigation from history or suggested questions
  useEffect(() => {
    if (location.state?.question) {
      const question = location.state.question;
      const cachedResponse = location.state.cachedResponse as CachedQueryResponse | undefined;
      const fromCache = location.state.fromCache;

      // Clear the state after using it
      window.history.replaceState({}, document.title);

      // If we have a cached response and user clicked "View", display it directly
      if (fromCache && cachedResponse) {
        displayCachedResponse(question, cachedResponse);
      } else {
        // Otherwise, set as initial question for re-run
        setInitialQuestion(question);
      }
    }
  }, [location]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Display cached response without API call
  const displayCachedResponse = (question: string, cached: CachedQueryResponse) => {
    const userMessage: QueryMessageType = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    const explanation = cached.insights?.summary ||
      `Found ${cached.results?.rowCount || 0} results for your question.`;

    const assistantMessage: QueryMessageType = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: explanation,
      timestamp: new Date(),
      sql: cached.sql,
      results: cached.results ? {
        columns: cached.results.columns,
        rows: cached.results.rows,
        rowCount: cached.results.rowCount,
        explanation: explanation
      } : undefined,
      insights: cached.insights,
      visualization: cached.visualization
    };

    // Replace messages instead of appending to prevent duplicates
    setMessages([userMessage, assistantMessage]);
  };

  const handleSubmit = async (question: string) => {
    // Add user message
    const userMessage: QueryMessageType = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Use NL2SQL API for natural language processing
      const response: NL2SQLResponse = await processNaturalLanguageQuery(question);

      // Log agent trace for debugging
      if (response.agent_trace) {
        console.log('Agent Trace:', response.agent_trace);
      }

      if (!response.success) {
        throw new Error(response.error || 'Query processing failed');
      }

      // Build explanation from insights
      const explanation = response.insights?.summary ||
        `Found ${response.results?.row_count || 0} results for your question.`;

      // Add assistant message with NL2SQL response data
      const assistantMessage: QueryMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: explanation,
        timestamp: new Date(),
        sql: response.sql?.query,
        results: response.results ? {
          columns: response.results.columns,
          rows: response.results.rows,
          rowCount: response.results.row_count,
          explanation: explanation
        } : undefined,
        insights: response.insights,
        visualization: response.visualization,
        agentTrace: response.agent_trace,
        executionTime: response.total_time
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Add to query history with cached response
      const cachedResponse: CachedQueryResponse = {
        sql: response.sql?.query,
        results: response.results ? {
          columns: response.results.columns,
          rows: response.results.rows,
          rowCount: response.results.row_count
        } : undefined,
        insights: response.insights,
        visualization: response.visualization
      };
      addQuery(question, Math.round(response.total_time * 1000), cachedResponse);

    } catch (error: any) {
      // Handle error
      const errorMessage: QueryMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Failed to process query'}. Please try rephrasing your question.`,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    handleSubmit(question);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center min-h-[60vh]">
              <div className="max-w-2xl w-full">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-ocean-900 dark:text-slate-100 mb-2 font-sans">
                    Ask a Question
                  </h2>
                  <p className="text-ocean-600 dark:text-slate-400">
                    Start by selecting a suggested question or type your own
                  </p>
                </div>
                <SuggestedQuestions onQuestionClick={handleSuggestedQuestion} />
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <QueryMessage key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 bg-white dark:bg-slate-800 rounded-2xl rounded-tl-sm p-4 shadow-sm border border-slate-200 dark:border-slate-700">
                    <div className="flex items-center gap-3">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                      <span className="text-sm text-slate-500 dark:text-slate-400">Analyzing your question...</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <QueryInput
        onSubmit={handleSubmit}
        isLoading={isLoading}
        initialValue={initialQuestion}
      />
    </div>
  );
}
