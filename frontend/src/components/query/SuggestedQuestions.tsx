import { useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { SUGGESTED_QUESTIONS } from '../../utils/mockData';

interface SuggestedQuestionsProps {
  onQuestionClick?: (question: string) => void;
}

export function SuggestedQuestions({ onQuestionClick }: SuggestedQuestionsProps) {
  const navigate = useNavigate();

  const handleClick = (question: string) => {
    if (onQuestionClick) {
      onQuestionClick(question);
    } else {
      navigate('/dashboard/query', { state: { question } });
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-ocean-900 dark:text-slate-100 mb-4 flex items-center gap-2 font-sans">
        <Sparkles className="w-5 h-5 text-electric-500" />
        Suggested Questions
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {SUGGESTED_QUESTIONS.map((item) => (
          <button
            key={item.id}
            onClick={() => handleClick(item.question)}
            className="group text-left p-4 rounded-lg bg-white dark:bg-ocean-900 border border-slate-200 dark:border-ocean-700 hover:border-electric-500 dark:hover:border-electric-500 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-electric-100 dark:bg-electric-900/30 text-electric-600 dark:text-electric-400 group-hover:bg-electric-500 group-hover:text-white transition-colors duration-200">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-ocean-900 dark:text-slate-100 group-hover:text-electric-600 dark:group-hover:text-electric-400 transition-colors duration-200">
                  {item.question}
                </p>
                <p className="text-xs text-ocean-600 dark:text-slate-400 mt-1">
                  {item.category}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
