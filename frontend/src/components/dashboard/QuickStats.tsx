import { useState, useEffect } from 'react';
import { TrendingUp, Database, Globe, Calendar, Loader2 } from 'lucide-react';
import { getQuickStats } from '../../services/api';
import { Card } from '../common/Card';

const colorClasses = {
  electric: 'bg-electric-100 dark:bg-electric-900/30 text-electric-600 dark:text-electric-400',
  emerald: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400',
  amber: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
  blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
};

export function QuickStats() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getQuickStats();
        setStats(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load statistics');
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="h-28 flex items-center justify-center">
            <Loader2 className="w-6 h-6 animate-spin text-electric-500" />
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <p className="text-red-600 dark:text-red-400">Error: {error}</p>
      </Card>
    );
  }

  if (!stats) {
    return null;
  }

  const statsConfig = [
    {
      label: 'Total Revenue',
      value: `$${(stats.total_revenue / 1000000).toFixed(1)}M`,
      icon: TrendingUp,
      color: 'electric' as const
    },
    {
      label: 'Total Transactions',
      value: stats.total_transactions.toLocaleString(),
      icon: Database,
      color: 'emerald' as const
    },
    {
      label: 'Countries',
      value: stats.countries_count.toString(),
      icon: Globe,
      color: 'amber' as const
    },
    {
      label: 'Date Range',
      value: stats.date_range,
      icon: Calendar,
      color: 'blue' as const
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {statsConfig.map((stat) => (
        <Card key={stat.label} className="hover:shadow-md transition-shadow duration-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">
                {stat.label}
              </p>
              <p className="text-3xl font-bold text-ocean-900 dark:text-slate-100 font-sans">
                {stat.value}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${colorClasses[stat.color]}`}>
              <stat.icon className="w-6 h-6" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
