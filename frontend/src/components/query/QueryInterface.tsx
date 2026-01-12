import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { type QueryMessage as QueryMessageType } from '../../types/query';
import { getMockSQL } from '../../utils/mockData';
import { executeQuery } from '../../services/api';
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

  // Handle navigation from suggested questions
  useEffect(() => {
    if (location.state?.question) {
      setInitialQuestion(location.state.question);
      // Clear the state after using it
      window.history.replaceState({}, document.title);
    }
  }, [location]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (question: string) => {
    const startTime = Date.now();

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
      // Generate SQL from question (mock for now - Phase 4 will use NL2SQL agents)
      const generatedSQL = getMockSQL(question);

      // Execute SQL using real API
      const apiResponse = await executeQuery(generatedSQL);

      // Generate explanation (mock for now - Phase 4 will use AI)
      const explanation = generateExplanation(question, apiResponse);

      // Add assistant message with real data
      const assistantMessage: QueryMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: explanation,
        timestamp: new Date(),
        sql: generatedSQL,
        results: {
          columns: apiResponse.columns,
          rows: apiResponse.rows,
          rowCount: apiResponse.row_count,
          explanation: explanation
        }
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Add to query history
      const executionTime = Date.now() - startTime;
      addQuery(question, executionTime);

    } catch (error: any) {
      // Handle error
      const errorMessage: QueryMessageType = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${error.message || 'Failed to execute query'}. Please try rephrasing your question.`,
        timestamp: new Date()
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Generate a simple explanation based on the question and results
  const generateExplanation = (question: string, results: any): string => {
    const rowCount = results.row_count;
    const hasData = rowCount > 0;

    if (!hasData) {
      return `No results found for your question: "${question}". The query executed successfully but returned no data.`;
    }

    // Simple explanation based on row count
    if (rowCount === 1) {
      return `Found 1 result for your question. The data shows the specific information you requested.`;
    } else {
      return `Found ${rowCount} results for your question. The table below shows all matching records from the database.`;
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
                  <h2 className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-2">
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
