import { useAuth } from '../context/AuthContext';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { QuickStats } from '../components/dashboard/QuickStats';
import { SuggestedQuestions } from '../components/query/SuggestedQuestions';
import { QueryHistory } from '../components/data/QueryHistory';

export function DashboardHome() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <DashboardLayout title="Dashboard">
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-2">
            Welcome back, {user.name.split(' ')[0]}!
          </h1>
          <p className="text-ocean-600 dark:text-slate-400">
            What would you like to explore today?
          </p>
        </div>

        {/* Quick Stats */}
        <QuickStats />

        {/* Query History */}
        <QueryHistory />

        {/* Suggested Questions */}
        <SuggestedQuestions />
      </div>
    </DashboardLayout>
  );
}
