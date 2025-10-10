import { useEffect, useState } from 'react';
import { Lightbulb, TrendingUp, DollarSign, BarChart3, Activity } from 'lucide-react';
import type { SampleQuestion } from '../types';

interface SampleQuestionsProps {
  onSelectQuestion: (question: string) => void;
}

const categoryIcons: Record<string, any> = {
  'Revenue Analysis': DollarSign,
  'Profitability': TrendingUp,
  'Asset Management': BarChart3,
  'Liquidity': Activity,
  'Efficiency': Activity,
  'Cash Flow': Activity,
  'Leverage': Activity,
};

const SampleQuestions = ({ onSelectQuestion }: SampleQuestionsProps) => {
  const [questions, setQuestions] = useState<SampleQuestion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/sample-questions')
      .then(res => res.json())
      .then(data => {
        setQuestions(data.questions);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching sample questions:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Lightbulb className="h-5 w-5 text-yellow-500" />
        <h2 className="text-lg font-semibold text-gray-900">
          Sample Questions
        </h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {questions.map((q) => {
          const Icon = categoryIcons[q.category] || BarChart3;
          return (
            <button
              key={q.id}
              onClick={() => onSelectQuestion(q.question)}
              className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all group"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <Icon className="h-5 w-5 text-gray-400 group-hover:text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                    {q.question}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {q.category}
                  </p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default SampleQuestions;