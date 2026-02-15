import { useState, useEffect } from 'react';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { Card } from '../components/common/Card';
import { NumberTicker } from '../components/common/NumberTicker';
import {
  Lightbulb,
  TrendingUp,
  AlertTriangle,
  Target,
  RefreshCw,
  Loader2,
  ArrowUpRight,
  ArrowDownRight,
  Globe,
  DollarSign
} from 'lucide-react';
import { getAutomatedInsights } from '../services/api';

interface Insight {
  id: string;
  type: 'opportunity' | 'risk' | 'trend' | 'anomaly';
  title: string;
  description: string;
  metric?: string;
  change?: number;
  action?: string;
  priority: 'high' | 'medium' | 'low';
}

interface InsightsData {
  summary: {
    total_revenue: number;
    revenue_change: number;
    top_market: string;
    top_market_share: number;
    fastest_growing: string;
    growth_rate: number;
  };
  insights: Insight[];
  generated_at: string;
}

const typeConfig = {
  opportunity: {
    icon: Target,
    color: 'text-emerald-600 dark:text-emerald-400',
    bg: 'bg-emerald-100 dark:bg-emerald-900/30',
    border: 'border-emerald-200 dark:border-emerald-800'
  },
  risk: {
    icon: AlertTriangle,
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-100 dark:bg-red-900/30',
    border: 'border-red-200 dark:border-red-800'
  },
  trend: {
    icon: TrendingUp,
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-100 dark:bg-blue-900/30',
    border: 'border-blue-200 dark:border-blue-800'
  },
  anomaly: {
    icon: Lightbulb,
    color: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-100 dark:bg-amber-900/30',
    border: 'border-amber-200 dark:border-amber-800'
  }
};

const priorityBadge = {
  high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  low: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
};

export function InsightsPage() {
  const [data, setData] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const fetchInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAutomatedInsights();
      setData(response);
    } catch (err: any) {
      setError(err.message || 'Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const filteredInsights = data?.insights.filter(
    insight => filter === 'all' || insight.type === filter
  ) || [];

  const insightCounts = {
    all: data?.insights.length || 0,
    opportunity: data?.insights.filter(i => i.type === 'opportunity').length || 0,
    risk: data?.insights.filter(i => i.type === 'risk').length || 0,
    trend: data?.insights.filter(i => i.type === 'trend').length || 0,
    anomaly: data?.insights.filter(i => i.type === 'anomaly').length || 0
  };

  return (
    <DashboardLayout title="AI Insights">
      <div className="max-w-7xl mx-auto px-6 py-8 font-sans">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h2 className="text-2xl font-bold text-ocean-900 dark:text-slate-100 mb-2 font-sans">
              AI-Powered Insights
            </h2>
            <p className="text-ocean-600 dark:text-slate-400 font-sans">
              Automated analysis of your financial data to surface opportunities, risks, and trends
            </p>
          </div>
          <button
            onClick={fetchInsights}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 dark:border-ocean-600 bg-white dark:bg-ocean-800 text-ocean-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-ocean-700 disabled:opacity-50 transition-smooth"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {loading && !data ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="w-10 h-10 animate-spin text-electric-500 mx-auto mb-4" />
              <p className="text-ocean-600 dark:text-slate-400">Analyzing your data...</p>
            </div>
          </div>
        ) : error ? (
          <Card className="p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
            <button
              onClick={fetchInsights}
              className="px-4 py-2 bg-electric-500 text-white rounded-xl hover:bg-electric-600 transition-smooth"
            >
              Try Again
            </button>
          </Card>
        ) : data ? (
          <>
            {/* Summary Cards - NumberTicker + same font style */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <Card className="p-4 hover-lift transition-smooth">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-electric-100 dark:bg-electric-900/30">
                    <DollarSign className="w-5 h-5 text-electric-600 dark:text-electric-400" />
                  </div>
                  <div>
                    <p className="text-sm text-ocean-600 dark:text-slate-400 font-sans">Total Revenue</p>
                    <p className="text-xl font-bold text-ocean-900 dark:text-slate-100 font-sans tabular-nums">
                      <NumberTicker value={data.summary.total_revenue / 1000000} prefix="$" suffix="M" decimals={1} duration={1000} />
                    </p>
                    <div className={`flex items-center gap-1 text-sm font-sans ${data.summary.revenue_change >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {data.summary.revenue_change >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                      <NumberTicker value={Math.abs(data.summary.revenue_change)} suffix="% YoY" decimals={1} duration={800} />
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-4 hover-lift transition-smooth">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-emerald-100 dark:bg-emerald-900/30">
                    <Globe className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm text-ocean-600 dark:text-slate-400 font-sans">Top Market</p>
                    <p className="text-xl font-bold text-ocean-900 dark:text-slate-100 font-sans">
                      {data.summary.top_market}
                    </p>
                    <p className="text-sm text-emerald-600 font-sans">
                      <NumberTicker value={data.summary.top_market_share} suffix="% of revenue" decimals={0} duration={800} />
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-4 hover-lift transition-smooth">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-blue-100 dark:bg-blue-900/30">
                    <TrendingUp className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm text-ocean-600 dark:text-slate-400 font-sans">Fastest Growing</p>
                    <p className="text-xl font-bold text-ocean-900 dark:text-slate-100 font-sans">
                      {data.summary.fastest_growing}
                    </p>
                    <p className="text-sm text-emerald-600 font-sans">
                      +<NumberTicker value={data.summary.growth_rate} suffix="% growth" decimals={0} duration={800} />
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-4 hover-lift transition-smooth">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-amber-100 dark:bg-amber-900/30">
                    <Lightbulb className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <div>
                    <p className="text-sm text-ocean-600 dark:text-slate-400 font-sans">Active Insights</p>
                    <p className="text-xl font-bold text-ocean-900 dark:text-slate-100 font-sans tabular-nums">
                      <NumberTicker value={data.insights.length} duration={800} />
                    </p>
                    <p className="text-sm text-emerald-600 font-sans">
                      <NumberTicker value={data.insights.filter(i => i.priority === 'high').length} duration={600} /> high priority
                    </p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
              {(['all', 'opportunity', 'risk', 'trend', 'anomaly'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setFilter(type)}
                  className={`px-4 py-2 rounded-xl font-medium text-sm whitespace-nowrap transition-smooth font-sans ${
                    filter === type
                      ? 'bg-electric-500 text-white'
                      : 'bg-white dark:bg-ocean-800 text-ocean-600 dark:text-slate-400 border border-slate-200 dark:border-ocean-700 hover:bg-slate-50 dark:hover:bg-ocean-700'
                  }`}
                >
                  {type === 'all' ? 'All Insights' : type.charAt(0).toUpperCase() + type.slice(1) + 's'}
                  <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-black/10 dark:bg-white/10 tabular-nums">
                    <NumberTicker value={insightCounts[type]} duration={400} />
                  </span>
                </button>
              ))}
            </div>

            {/* Insights List */}
            <div className="space-y-4">
              {filteredInsights.length === 0 ? (
                <Card className="p-8 text-center">
                  <Lightbulb className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                  <p className="text-ocean-600 dark:text-slate-400">No insights found for this filter</p>
                </Card>
              ) : (
                filteredInsights.map((insight) => {
                  const config = typeConfig[insight.type];
                  const Icon = config.icon;

                  return (
                    <Card
                      key={insight.id}
                      className={`p-5 border-l-4 ${config.border} hover-lift transition-smooth`}
                    >
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg ${config.bg} flex-shrink-0`}>
                          <Icon className={`w-5 h-5 ${config.color}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-semibold text-ocean-900 dark:text-slate-100 font-sans">
                              {insight.title}
                            </h3>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priorityBadge[insight.priority]}`}>
                              {insight.priority}
                            </span>
                          </div>
                          <p className="text-ocean-600 dark:text-slate-400 mb-3">
                            {insight.description}
                          </p>
                          {insight.metric && (
                            <div className="flex items-center gap-4 text-sm">
                              <span className="text-ocean-500 dark:text-slate-500">
                                Metric: <span className="font-medium text-ocean-700 dark:text-slate-300 font-sans">{insight.metric}</span>
                              </span>
                              {insight.change !== undefined && (
                                <span className={`flex items-center gap-1 font-sans ${insight.change >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                                  {insight.change >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                  <NumberTicker value={Math.abs(insight.change)} suffix="%" decimals={1} duration={600} />
                                </span>
                              )}
                            </div>
                          )}
                          {insight.action && (
                            <div className="mt-3 p-3 bg-slate-50 dark:bg-ocean-800 rounded-lg">
                              <p className="text-sm">
                                <span className="font-medium text-ocean-700 dark:text-slate-300">Recommended Action: </span>
                                <span className="text-ocean-600 dark:text-slate-400">{insight.action}</span>
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </Card>
                  );
                })
              )}
            </div>

            {/* Generated timestamp */}
            <p className="text-center text-sm text-ocean-500 dark:text-slate-500 mt-8">
              Insights generated at {new Date(data.generated_at).toLocaleString()}
            </p>
          </>
        ) : null}
      </div>
    </DashboardLayout>
  );
}
