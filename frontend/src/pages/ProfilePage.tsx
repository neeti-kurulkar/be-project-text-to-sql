import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { User, Mail, Building2, Shield, Calendar } from 'lucide-react';

export function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  const joinDate = new Date('2024-01-15'); // Mock join date
  const formattedDate = joinDate.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <DashboardLayout title="Profile">
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Profile Header Card */}
        <Card>
          <div className="flex flex-col sm:flex-row items-center gap-6">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-electric-500 to-emerald-500 text-white flex items-center justify-center font-bold text-3xl shadow-lg">
              {user.name
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase()}
            </div>

            {/* User Info */}
            <div className="flex-1 text-center sm:text-left">
              <h2 className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-2">
                {user.name}
              </h2>
              <p className="text-ocean-600 dark:text-slate-400 mb-3">
                {user.email}
              </p>
              <Badge variant={user.role === 'Admin' ? 'blue' : 'green'}>
                {user.role}
              </Badge>
            </div>
          </div>
        </Card>

        {/* Account Details */}
        <Card title="Account Details" description="Your account information">
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <User className="w-5 h-5 text-ocean-600 dark:text-slate-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                  Full Name
                </div>
                <div className="text-sm text-ocean-600 dark:text-slate-400 mt-1">
                  {user.name}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <Mail className="w-5 h-5 text-ocean-600 dark:text-slate-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                  Email Address
                </div>
                <div className="text-sm text-ocean-600 dark:text-slate-400 mt-1">
                  {user.email}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <Building2 className="w-5 h-5 text-ocean-600 dark:text-slate-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                  Company
                </div>
                <div className="text-sm text-ocean-600 dark:text-slate-400 mt-1">
                  {user.company}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <Shield className="w-5 h-5 text-ocean-600 dark:text-slate-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                  Role & Permissions
                </div>
                <div className="text-sm text-ocean-600 dark:text-slate-400 mt-1">
                  {user.role} - {user.role === 'Admin' ? 'Full access to all features' : 'Read and query access'}
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <Calendar className="w-5 h-5 text-ocean-600 dark:text-slate-400 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                  Member Since
                </div>
                <div className="text-sm text-ocean-600 dark:text-slate-400 mt-1">
                  {formattedDate}
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Activity Stats */}
        <Card title="Activity Overview" description="Your usage statistics">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg text-center">
              <div className="text-2xl font-bold font-mono text-electric-600 dark:text-electric-400 mb-1">
                142
              </div>
              <div className="text-sm text-ocean-600 dark:text-slate-400">
                Queries Run
              </div>
            </div>

            <div className="p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg text-center">
              <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mb-1">
                28
              </div>
              <div className="text-sm text-ocean-600 dark:text-slate-400">
                Days Active
              </div>
            </div>

            <div className="p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg text-center">
              <div className="text-2xl font-bold font-mono text-blue-600 dark:text-blue-400 mb-1">
                5.1s
              </div>
              <div className="text-sm text-ocean-600 dark:text-slate-400">
                Avg Response Time
              </div>
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}
