import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { RevenueByCountry } from '../components/charts/RevenueByCountry';
import { RevenueTrend } from '../components/charts/RevenueTrend';
import { QuarterlyRevenue } from '../components/charts/QuarterlyRevenue';
import { TopExpenses } from '../components/charts/TopExpenses';
import { RegionalDistribution } from '../components/charts/RegionalDistribution';

export function ChartsPage() {
  return (
    <DashboardLayout title="Financial Dashboard">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold font-mono text-ocean-900 dark:text-slate-100 mb-2">
            Visual Analytics
          </h2>
          <p className="text-ocean-600 dark:text-slate-400">
            Interactive charts and visualizations of your financial data
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RevenueByCountry />
          <RevenueTrend />
          <QuarterlyRevenue />
          <TopExpenses />
          <RegionalDistribution />
        </div>
      </div>
    </DashboardLayout>
  );
}
