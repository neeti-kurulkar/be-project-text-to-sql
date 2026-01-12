import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { type QueryMessage as QueryMessageType } from '../../types/query';
import { getMockQueryResponse, getMockSQL } from '../../utils/mockData';
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

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 800));

    // Get mock response
    const mockResponse = getMockQueryResponse(question);
    const mockSQL = getMockSQL(question);

    // Add assistant message
    const assistantMessage: QueryMessageType = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: mockResponse.explanation,
      timestamp: new Date(),
      sql: mockSQL,
      results: mockResponse
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);

    // Add to query history
    const executionTime = Date.now() - startTime;
    addQuery(question, executionTime);
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
