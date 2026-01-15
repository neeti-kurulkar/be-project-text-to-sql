import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { Card } from '../components/common/Card';
import { QueryHistory } from '../components/data/QueryHistory';
import {
  TrendingUp,
  TrendingDown,
  Globe,
  DollarSign,
  BarChart3,
  MessageSquare,
  Lightbulb,
  Database,
  ArrowRight,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { getQuickStats, getAutomatedInsights } from '../services/api';

interface QuickAction {
  title: string;
  description: string;
  icon: typeof TrendingUp;
  color: string;
  route: string;
  query?: string;
}

const quickActions: QuickAction[] = [
  {
    title: 'Revenue Analysis',
    description: 'Analyze revenue trends and distribution',
    icon: DollarSign,
    color: 'bg-emerald-500',
    route: '/dashboard/query',
    query: 'What percentage of our revenue comes from each territory?'
  },
  {
    title: 'Growth Insights',
    description: 'Compare year-over-year performance',
    icon: TrendingUp,
    color: 'bg-blue-500',
    route: '/dashboard/query',
    query: 'Compare year-over-year revenue growth by region'
  },
  {
    title: 'Cost Analysis',
    description: 'Review expense categories',
    icon: BarChart3,
    color: 'bg-amber-500',
    route: '/dashboard/query',
    query: 'Which expense categories are growing faster than revenue?'
  },
  {
    title: 'Market Risk',
    description: 'Check revenue concentration',
    icon: AlertCircle,
    color: 'bg-red-500',
    route: '/dashboard/query',
    query: 'How concentrated is our revenue? Are we too dependent on a few countries?'
  }
];

export function DashboardHome() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [topInsights, setTopInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, insightsData] = await Promise.all([
          getQuickStats(),
          getAutomatedInsights()
        ]);
        setStats(statsData);
        // Get top 3 high priority insights
        const highPriority = insightsData.insights
          .filter((i: any) => i.priority === 'high' || i.priority === 'medium')
          .slice(0, 3);
        setTopInsights(highPriority);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (!user) return null;

  const handleQuickAction = (action: QuickAction) => {
    if (action.query) {
      navigate(action.route, { state: { question: action.query } });
    } else {
      navigate(action.route);
    }
  };

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <DashboardLayout title="Overview">
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-1">
              {getTimeGreeting()}, {user.name.split(' ')[0]}
            </h1>
            <p className="text-ocean-600 dark:text-slate-400">
              Here's what's happening with your financial data
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/dashboard/query')}
              className="flex items-center gap-2 px-4 py-2 bg-electric-500 text-white rounded-lg hover:bg-electric-600 transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
              Ask FinQ
            </button>
            <button
              onClick={() => navigate('/dashboard/insights')}
              className="flex items-center gap-2 px-4 py-2 border border-slate-300 dark:border-ocean-600 rounded-lg text-ocean-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-ocean-800 transition-colors"
            >
              <Lightbulb className="w-4 h-4" />
              View Insights
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="h-28 flex items-center justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-electric-500" />
              </Card>
            ))}
          </div>
        ) : stats ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">Total Revenue</p>
                  <p className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100">
                    ${(stats.total_revenue / 1000000).toFixed(1)}M
                  </p>
                  <div className="flex items-center gap-1 mt-1 text-sm text-emerald-600">
                    <TrendingUp className="w-4 h-4" />
                    <span>All time</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
                  <DollarSign className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                </div>
              </div>
            </Card>

            <Card className="p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">Transactions</p>
                  <p className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100">
                    {stats.total_transactions.toLocaleString()}
                  </p>
                  <div className="flex items-center gap-1 mt-1 text-sm text-ocean-500 dark:text-slate-500">
                    <Database className="w-4 h-4" />
                    <span>Total records</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                  <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            </Card>

            <Card className="p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">Markets</p>
                  <p className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100">
                    {stats.countries_count}
                  </p>
                  <div className="flex items-center gap-1 mt-1 text-sm text-ocean-500 dark:text-slate-500">
                    <Globe className="w-4 h-4" />
                    <span>Countries</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                  <Globe className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                </div>
              </div>
            </Card>

            <Card className="p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">Data Period</p>
                  <p className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100">
                    {stats.date_range}
                  </p>
                  <div className="flex items-center gap-1 mt-1 text-sm text-ocean-500 dark:text-slate-500">
                    <span>Coverage</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                  <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
            </Card>
          </div>
        ) : null}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2">
            <Card title="Quick Analysis" description="One-click access to common financial analyses">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                {quickActions.map((action) => (
                  <button
                    key={action.title}
                    onClick={() => handleQuickAction(action)}
                    className="flex items-center gap-4 p-4 rounded-lg border border-slate-200 dark:border-ocean-700 hover:border-electric-500 dark:hover:border-electric-500 hover:shadow-md transition-all text-left group"
                  >
                    <div className={`p-3 rounded-lg ${action.color} text-white flex-shrink-0`}>
                      <action.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-ocean-900 dark:text-slate-100 group-hover:text-electric-600 dark:group-hover:text-electric-400 transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-ocean-600 dark:text-slate-400 truncate">
                        {action.description}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-ocean-400 dark:text-slate-600 group-hover:text-electric-500 transition-colors flex-shrink-0" />
                  </button>
                ))}
              </div>
            </Card>
          </div>

          {/* Top Insights */}
          <div>
            <Card
              title="Priority Insights"
              description="Issues requiring attention"
            >
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-electric-500" />
                </div>
              ) : topInsights.length > 0 ? (
                <div className="space-y-3 mt-4">
                  {topInsights.map((insight, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border-l-4 ${
                        insight.type === 'risk'
                          ? 'border-red-500 bg-red-50 dark:bg-red-900/10'
                          : insight.type === 'opportunity'
                          ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/10'
                          : 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
                      }`}
                    >
                      <h4 className="font-medium text-sm text-ocean-900 dark:text-slate-100 mb-1">
                        {insight.title}
                      </h4>
                      <p className="text-xs text-ocean-600 dark:text-slate-400 line-clamp-2">
                        {insight.description}
                      </p>
                    </div>
                  ))}
                  <button
                    onClick={() => navigate('/dashboard/insights')}
                    className="w-full text-center text-sm text-electric-600 dark:text-electric-400 hover:underline py-2"
                  >
                    View all insights →
                  </button>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Lightbulb className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-sm text-ocean-600 dark:text-slate-400">
                    No priority insights at this time
                  </p>
                </div>
              )}
            </Card>
          </div>
        </div>

        {/* Query History */}
        <QueryHistory />
      </div>
    </DashboardLayout>
  );
}
