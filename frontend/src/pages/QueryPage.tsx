import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { QueryInterface } from '../components/query/QueryInterface';

export function QueryPage() {
  return (
    <DashboardLayout title="Ask Questions">
      <QueryInterface />
    </DashboardLayout>
  );
}
