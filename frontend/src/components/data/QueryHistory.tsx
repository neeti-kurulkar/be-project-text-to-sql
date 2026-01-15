import { useNavigate } from 'react-router-dom';
import { Clock, Eye, RotateCw, Trash2 } from 'lucide-react';
import { useQueryHistory } from '../../hooks/useQueryHistory';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

export function QueryHistory() {
  const { history, clearHistory, removeQuery } = useQueryHistory();
  const navigate = useNavigate();

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const handleView = (item: typeof history[0]) => {
    // Navigate with cached response if available
    navigate('/dashboard/query', {
      state: {
        question: item.question,
        cachedResponse: item.cachedResponse,
        fromCache: true
      }
    });
  };

  const handleRerun = (question: string) => {
    // Re-run without cache - will make fresh LLM call
    navigate('/dashboard/query', { state: { question, fromCache: false } });
  };

  if (history.length === 0) {
    return (
      <Card title="Query History" description="Your recent questions">
        <div className="text-center py-12">
          <Clock className="w-12 h-12 mx-auto text-ocean-400 dark:text-slate-600 mb-3" />
          <p className="text-ocean-600 dark:text-slate-400">
            No queries yet. Start by asking a question!
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title="Query History"
      description={`${history.length} recent ${history.length === 1 ? 'query' : 'queries'}`}
    >
      <div className="space-y-3">
        {/* Clear button */}
        <div className="flex justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={clearHistory}
            className="flex items-center gap-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            <Trash2 className="w-4 h-4" />
            Clear History
          </Button>
        </div>

        {/* History List */}
        <div className="space-y-2">
          {history.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg hover:bg-slate-100 dark:hover:bg-ocean-700 transition-colors duration-200"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ocean-900 dark:text-slate-100 truncate">
                  {item.question}
                </p>
                <div className="flex items-center gap-3 mt-1 text-xs text-ocean-600 dark:text-slate-400">
                  <span>{formatTime(item.timestamp)}</span>
                  <span>•</span>
                  <span>{item.executionTime}ms</span>
                </div>
              </div>
              <div className="flex items-center gap-1 ml-4">
                <button
                  onClick={() => handleView(item)}
                  className="p-2 rounded-lg text-ocean-600 dark:text-slate-400 hover:bg-white dark:hover:bg-ocean-800 hover:text-electric-600 dark:hover:text-electric-400 transition-colors duration-200"
                  title="View cached result"
                >
                  <Eye className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleRerun(item.question)}
                  className="p-2 rounded-lg text-ocean-600 dark:text-slate-400 hover:bg-white dark:hover:bg-ocean-800 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors duration-200"
                  title="Re-run query"
                >
                  <RotateCw className="w-4 h-4" />
                </button>
                <button
                  onClick={() => removeQuery(item.id)}
                  className="p-2 rounded-lg text-ocean-600 dark:text-slate-400 hover:bg-white dark:hover:bg-ocean-800 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200"
                  title="Delete query"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
