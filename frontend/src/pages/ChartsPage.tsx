import { useState } from 'react';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { RevenueByCountry } from '../components/charts/RevenueByCountry';
import { RevenueTrend } from '../components/charts/RevenueTrend';
import { QuarterlyRevenue } from '../components/charts/QuarterlyRevenue';
import { TopExpenses } from '../components/charts/TopExpenses';
import { RegionalDistribution } from '../components/charts/RegionalDistribution';
import { ProfitLossTrend } from '../components/charts/ProfitLossTrend';
import { YoYGrowth } from '../components/charts/YoYGrowth';
import { ExpenseBreakdown } from '../components/charts/ExpenseBreakdown';
import { ChartLoading } from '../components/charts/ChartLoading';
import { ChartError } from '../components/charts/ChartError';
import { useAllCharts } from '../hooks/useChartData';
import { RefreshCw } from 'lucide-react';

export function ChartsPage() {
  const [selectedYear, setSelectedYear] = useState<number | undefined>(undefined);
  const { data, loading, error, refetch } = useAllCharts(selectedYear);

  const yearOptions = [
    { value: '', label: 'All Years' },
    { value: '2020', label: '2020' },
    { value: '2019', label: '2019' },
    { value: '2018', label: '2018' },
  ];

  return (
    <DashboardLayout title="Financial Dashboard">
      <div className="max-w-7xl mx-auto px-6 py-8 font-sans">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-xl font-semibold text-ocean-900 dark:text-slate-100 mb-2 font-sans">
              Visual Analytics
            </h2>
            <p className="text-ocean-600 dark:text-slate-400 font-sans">
              Interactive charts and visualizations of your financial data
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={selectedYear || ''}
              onChange={(e) => setSelectedYear(e.target.value ? parseInt(e.target.value) : undefined)}
              className="px-3 py-2 rounded-lg border border-slate-300 dark:border-ocean-600 bg-white dark:bg-ocean-800 text-ocean-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {yearOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <button
              onClick={refetch}
              disabled={loading}
              className="p-2 rounded-lg border border-slate-300 dark:border-ocean-600 bg-white dark:bg-ocean-800 text-ocean-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-ocean-700 disabled:opacity-50"
              title="Refresh data"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {loading && !data && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartLoading />
            <ChartLoading />
            <ChartLoading />
            <ChartLoading />
          </div>
        )}

        {error && !data && (
          <ChartError message={error} onRetry={refetch} />
        )}

        {data && (
          <>
            {/* Revenue Analysis Section */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-ocean-900 dark:text-slate-100 mb-4 font-sans">
                Revenue Analysis
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <RevenueByCountry data={data.revenueByCountry} />
                <RevenueTrend data={data.revenueTrend} />
                <QuarterlyRevenue data={data.quarterlyRevenue} />
                <RegionalDistribution data={data.regionalDistribution} />
              </div>
            </div>

            {/* Expense Analysis Section */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-ocean-900 dark:text-slate-100 mb-4 font-sans">
                Expense Analysis
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TopExpenses data={data.topExpenses} />
                <ExpenseBreakdown data={data.expenseBreakdown} />
              </div>
            </div>

            {/* Performance Analysis Section */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-ocean-900 dark:text-slate-100 mb-4 font-sans">
                Performance Analysis
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ProfitLossTrend data={data.profitLoss} />
                <YoYGrowth data={data.yoyGrowth} />
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
