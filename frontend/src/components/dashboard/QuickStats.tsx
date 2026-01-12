import { TrendingUp, Database, Globe, Calendar } from 'lucide-react';
import { QUICK_STATS } from '../../utils/mockData';
import { Card } from '../common/Card';

const stats = [
  {
    label: 'Total Revenue',
    value: `$${QUICK_STATS.totalRevenue}M`,
    icon: TrendingUp,
    color: 'electric'
  },
  {
    label: 'Total Transactions',
    value: QUICK_STATS.totalTransactions,
    icon: Database,
    color: 'emerald'
  },
  {
    label: 'Countries',
    value: QUICK_STATS.countries,
    icon: Globe,
    color: 'amber'
  },
  {
    label: 'Date Range',
    value: QUICK_STATS.dateRange,
    icon: Calendar,
    color: 'blue'
  }
];

const colorClasses = {
  electric: 'bg-electric-100 dark:bg-electric-900/30 text-electric-600 dark:text-electric-400',
  emerald: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400',
  amber: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
  blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
};

export function QuickStats() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <Card key={stat.label} className="hover:shadow-md transition-shadow duration-200">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-ocean-600 dark:text-slate-400 mb-1">
                {stat.label}
              </p>
              <p className="text-3xl font-bold font-mono text-ocean-900 dark:text-slate-100">
                {stat.value}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${colorClasses[stat.color as keyof typeof colorClasses]}`}>
              <stat.icon className="w-6 h-6" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
