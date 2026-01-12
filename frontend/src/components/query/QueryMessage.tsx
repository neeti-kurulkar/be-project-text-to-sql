import { useState } from 'react';
import { User, Bot, Code, Table, Copy, Check } from 'lucide-react';
import { type QueryMessage as QueryMessageType } from '../../types/query';
import { QueryResults } from './QueryResults';
import { Button } from '../common/Button';

interface QueryMessageProps {
  message: QueryMessageType;
}

export function QueryMessage({ message }: QueryMessageProps) {
  const [showSQL, setShowSQL] = useState(false);
  const [showTable, setShowTable] = useState(false);
  const [copied, setCopied] = useState(false);

  const isUser = message.type === 'user';

  const handleCopySQL = () => {
    if (message.sql) {
      navigator.clipboard.writeText(message.sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="flex items-start gap-3 max-w-3xl">
          <div className="flex-1 bg-electric-500 text-white rounded-2xl rounded-tr-sm px-4 py-3">
            <p className="text-sm">{message.content}</p>
          </div>
          <div className="w-8 h-8 rounded-full bg-electric-500 text-white flex items-center justify-center flex-shrink-0">
            <User className="w-5 h-5" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="flex items-start gap-3 max-w-4xl">
        <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5" />
        </div>
        <div className="flex-1 space-y-3">
          {/* Explanation */}
          <div className="bg-slate-100 dark:bg-ocean-800 rounded-2xl rounded-tl-sm px-4 py-3">
            <p className="text-sm text-ocean-900 dark:text-slate-100">
              {message.results?.explanation || message.content}
            </p>
          </div>

          {/* Toggle Buttons */}
          {(message.sql || message.results) && (
            <div className="flex gap-2">
              {message.sql && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSQL(!showSQL)}
                  className="flex items-center gap-2"
                >
                  <Code className="w-4 h-4" />
                  {showSQL ? 'Hide' : 'Show'} SQL
                </Button>
              )}
              {message.results && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowTable(!showTable)}
                  className="flex items-center gap-2"
                >
                  <Table className="w-4 h-4" />
                  {showTable ? 'Hide' : 'Show'} Table
                </Button>
              )}
            </div>
          )}

          {/* SQL Code Block */}
          {message.sql && showSQL && (
            <div className="bg-ocean-900 rounded-lg overflow-hidden border border-ocean-700">
              <div className="flex items-center justify-between px-4 py-2 border-b border-ocean-700">
                <span className="text-xs font-mono text-slate-400">SQL Query</span>
                <button
                  onClick={handleCopySQL}
                  className="flex items-center gap-1.5 px-2 py-1 text-xs text-slate-400 hover:text-slate-100 transition-colors duration-200"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      Copy
                    </>
                  )}
                </button>
              </div>
              <pre className="p-4 overflow-x-auto">
                <code className="text-sm text-slate-100 font-mono">
                  {message.sql}
                </code>
              </pre>
            </div>
          )}

          {/* Results Table */}
          {message.results && showTable && (
            <QueryResults results={message.results} />
          )}

          {/* Timestamp */}
          <p className="text-xs text-ocean-600 dark:text-slate-400">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
}
