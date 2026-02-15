import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { Card } from '../components/common/Card';
import { NumberTicker } from '../components/common/NumberTicker';
import { QueryHistory } from '../components/data/QueryHistory';
import {
  TrendingUp,
  Globe,
  DollarSign,
  BarChart3,
  MessageSquare,
  Lightbulb,
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
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 font-sans">
        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 animate-fade-in-up">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-ocean-900 dark:text-slate-100 mb-1 font-sans">
              {getTimeGreeting()}, {user.name.split(' ')[0]}
            </h1>
            <p className="text-ocean-600 dark:text-slate-400 text-sm md:text-base font-sans">
              Here's what's happening with your financial data
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => navigate('/dashboard/query')}
              className="flex items-center gap-2 px-5 py-2.5 bg-electric-500 text-white rounded-xl hover:bg-electric-600 transition-smooth shadow-sm hover:shadow-md"
            >
              <MessageSquare className="w-4 h-4" />
              Ask FinQ
            </button>
            <button
              onClick={() => navigate('/dashboard/insights')}
              className="flex items-center gap-2 px-5 py-2.5 border border-slate-200 dark:border-ocean-600 rounded-xl text-ocean-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-ocean-800 transition-smooth"
            >
              <Lightbulb className="w-4 h-4" />
              View Insights
            </button>
          </div>
        </div>

        {/* Dashboard Overview - KPI Cards with number tickers */}
        <section>
          <h2 className="text-lg font-semibold text-ocean-900 dark:text-slate-100 mb-4 font-sans">
            Dashboard Overview
          </h2>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((_key) => (
              <Card key={_key} className="h-32 flex items-center justify-center rounded-2xl">
                <Loader2 className="w-6 h-6 animate-spin text-electric-500" />
              </Card>
            ))}
          </div>
        ) : stats ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              {
                label: 'Total Revenue',
                value: stats.total_revenue / 1000000,
                prefix: '$',
                suffix: 'M',
                decimals: 1,
                trend: 'positive',
                trendLabel: 'All time',
                icon: DollarSign,
                iconBg: 'bg-emerald-100 dark:bg-emerald-900/30',
                iconColor: 'text-emerald-600 dark:text-emerald-400',
                delay: 0
              },
              {
                label: 'Transactions',
                value: stats.total_transactions,
                trendLabel: 'Total records',
                icon: BarChart3,
                iconBg: 'bg-electric-100 dark:bg-electric-900/30',
                iconColor: 'text-electric-600 dark:text-electric-400',
                delay: 50
              },
              {
                label: 'Markets',
                value: stats.countries_count,
                trendLabel: 'Countries',
                icon: Globe,
                iconBg: 'bg-amber-100 dark:bg-amber-900/30',
                iconColor: 'text-amber-600 dark:text-amber-400',
                delay: 100
              },
              {
                label: 'Data Period',
                value: stats.date_range,
                trendLabel: 'Coverage',
                icon: TrendingUp,
                iconBg: 'bg-purple-100 dark:bg-purple-900/30',
                iconColor: 'text-purple-600 dark:text-purple-400',
                delay: 150
              }
            ].map((kpi) => (
              <div
                key={kpi.label}
                className="animate-fade-in-up card-3d bg-white dark:bg-ocean-900 rounded-2xl shadow-sm border border-slate-200 dark:border-ocean-700 p-5 opacity-0"
                style={{ animationDelay: `${kpi.delay}ms` }}
              >
                <div className="flex items-start justify-between">
                  <div className="min-w-0">
                    <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">{kpi.label}</p>
                    <p className="text-2xl font-bold text-ocean-900 dark:text-slate-100 tabular-nums">
                      {typeof kpi.value === 'number' && kpi.suffix === 'M' ? (
                        <NumberTicker value={kpi.value} prefix={kpi.prefix} suffix={kpi.suffix} decimals={1} duration={1000} />
                      ) : typeof kpi.value === 'number' ? (
                        <NumberTicker value={kpi.value} duration={1200} />
                      ) : (
                        <NumberTicker value={kpi.value} />
                      )}
                    </p>
                    <div className={`flex items-center gap-1 mt-1 text-sm ${kpi.trend === 'positive' ? 'text-emerald-600' : 'text-ocean-500 dark:text-slate-500'}`}>
                      {kpi.trend === 'positive' && <TrendingUp className="w-4 h-4" />}
                      <span>{kpi.trendLabel}</span>
                    </div>
                  </div>
                  <div className={`p-3 rounded-xl flex-shrink-0 ${kpi.iconBg}`}>
                    <kpi.icon className={`w-5 h-5 ${kpi.iconColor}`} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : null}
        </section>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <div className="lg:col-span-2 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <Card title="Quick Analysis" description="One-click access to common financial analyses" className="rounded-2xl transition-smooth">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                {quickActions.map((action) => (
                  <button
                    key={action.title}
                    onClick={() => handleQuickAction(action)}
                    className="flex items-center gap-4 p-4 rounded-xl border border-slate-200 dark:border-ocean-700 hover:border-electric-500 dark:hover:border-electric-500 hover:shadow-md transition-smooth text-left group"
                  >
                    <div className={`p-3 rounded-xl ${action.color} text-white flex-shrink-0 transition-smooth`}>
                      <action.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-ocean-900 dark:text-slate-100 group-hover:text-electric-600 dark:group-hover:text-electric-400 transition-smooth">
                        {action.title}
                      </h3>
                      <p className="text-sm text-ocean-600 dark:text-slate-400 truncate">
                        {action.description}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-ocean-400 dark:text-slate-600 group-hover:text-electric-500 transition-smooth flex-shrink-0" />
                  </button>
                ))}
              </div>
            </Card>
          </div>

          {/* Top Insights */}
          <div className="animate-fade-in-up" style={{ animationDelay: '150ms' }}>
            <Card
              title="Priority Insights"
              description="Issues requiring attention"
              className="rounded-2xl transition-smooth"
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
                      className={`p-3 rounded-xl border-l-4 transition-smooth ${
                        insight.type === 'risk'
                          ? 'border-red-500 bg-red-50 dark:bg-red-900/10'
                          : insight.type === 'opportunity'
                          ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-900/10'
                          : 'border-electric-500 bg-electric-50 dark:bg-electric-900/10'
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
                    className="w-full text-center text-sm text-electric-600 dark:text-electric-400 hover:underline py-2 transition-smooth"
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
        <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <QueryHistory />
        </div>
      </div>
    </DashboardLayout>
  );
}
