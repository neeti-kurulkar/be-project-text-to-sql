import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { TableBrowser } from '../components/data/TableBrowser';

export function DataPage() {
  return (
    <DashboardLayout title="View Data">
      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        <TableBrowser />
      </div>
    </DashboardLayout>
  );
}
