import { useState } from 'react';
import { DashboardLayout } from '../components/dashboard/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Moon, Sun, Bell, Database, Download, Trash2, Check } from 'lucide-react';

export function SettingsPage() {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [queryNotifications, setQueryNotifications] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!user) return null;

  const handleSavePreferences = () => {
    // Mock save action
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <DashboardLayout title="Settings">
      <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {/* Appearance Settings */}
        <Card title="Appearance" description="Customize how FinQ looks for you">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <div className="flex items-center gap-3">
                {theme === 'dark' ? (
                  <Moon className="w-5 h-5 text-ocean-600 dark:text-slate-400" />
                ) : (
                  <Sun className="w-5 h-5 text-ocean-600 dark:text-slate-400" />
                )}
                <div>
                  <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                    Theme
                  </div>
                  <div className="text-xs text-ocean-600 dark:text-slate-400 mt-0.5">
                    Currently using {theme === 'dark' ? 'Dark' : 'Light'} mode
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={toggleTheme}
                className="flex items-center gap-2"
              >
                {theme === 'dark' ? (
                  <>
                    <Sun className="w-4 h-4" />
                    Light
                  </>
                ) : (
                  <>
                    <Moon className="w-4 h-4" />
                    Dark
                  </>
                )}
              </Button>
            </div>
          </div>
        </Card>

        {/* Notification Settings */}
        <Card title="Notifications" description="Manage how you receive updates">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <div className="flex items-center gap-3">
                <Bell className="w-5 h-5 text-ocean-600 dark:text-slate-400" />
                <div>
                  <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                    Email Notifications
                  </div>
                  <div className="text-xs text-ocean-600 dark:text-slate-400 mt-0.5">
                    Receive email updates about your queries
                  </div>
                </div>
              </div>
              <button
                onClick={() => setEmailNotifications(!emailNotifications)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  emailNotifications
                    ? 'bg-electric-500'
                    : 'bg-slate-300 dark:bg-ocean-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    emailNotifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <div className="flex items-center gap-3">
                <Bell className="w-5 h-5 text-ocean-600 dark:text-slate-400" />
                <div>
                  <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                    Query Completion Alerts
                  </div>
                  <div className="text-xs text-ocean-600 dark:text-slate-400 mt-0.5">
                    Get notified when long-running queries finish
                  </div>
                </div>
              </div>
              <button
                onClick={() => setQueryNotifications(!queryNotifications)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  queryNotifications
                    ? 'bg-electric-500'
                    : 'bg-slate-300 dark:bg-ocean-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    queryNotifications ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <div className="flex justify-end pt-2">
              <Button
                variant={saved ? 'primary' : 'outline'}
                size="sm"
                onClick={handleSavePreferences}
                className="flex items-center gap-2"
              >
                {saved ? (
                  <>
                    <Check className="w-4 h-4" />
                    Saved!
                  </>
                ) : (
                  'Save Preferences'
                )}
              </Button>
            </div>
          </div>
        </Card>

        {/* Database Settings */}
        <Card title="Database" description="Connection and data management">
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <Database className="w-5 h-5 text-ocean-600 dark:text-slate-400 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-ocean-900 dark:text-slate-100 mb-1">
                  Connected Database
                </div>
                <div className="text-xs text-ocean-600 dark:text-slate-400 mb-2">
                  financial_db @ localhost:5432
                </div>
                <Badge variant="green">Connected</Badge>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-ocean-800 rounded-lg">
              <div className="flex items-center gap-3">
                <Download className="w-5 h-5 text-ocean-600 dark:text-slate-400" />
                <div>
                  <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
                    Export Query History
                  </div>
                  <div className="text-xs text-ocean-600 dark:text-slate-400 mt-0.5">
                    Download your query history as CSV
                  </div>
                </div>
              </div>
              <Button variant="outline" size="sm">
                Export
              </Button>
            </div>
          </div>
        </Card>

        {/* Data & Privacy */}
        <Card title="Data & Privacy" description="Manage your data and privacy settings">
          <div className="space-y-4">
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <div className="flex items-start gap-3">
                <Trash2 className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-1">
                    Clear Query History
                  </div>
                  <div className="text-xs text-amber-700 dark:text-amber-300 mb-3">
                    This will permanently delete all your saved queries and history. This action cannot be undone.
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700 hover:bg-amber-100 dark:hover:bg-amber-900/30"
                  >
                    Clear All History
                  </Button>
                </div>
              </div>
            </div>

            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-start gap-3">
                <Trash2 className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-red-900 dark:text-red-200 mb-1">
                    Delete Account
                  </div>
                  <div className="text-xs text-red-700 dark:text-red-300 mb-3">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-700 dark:text-red-300 border-red-300 dark:border-red-700 hover:bg-red-100 dark:hover:bg-red-900/30"
                  >
                    Delete Account
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Account Info */}
        <div className="text-center text-sm text-ocean-600 dark:text-slate-400 pt-4">
          Account ID: {user.id} • Member since January 2024
        </div>
      </div>
    </DashboardLayout>
  );
}
