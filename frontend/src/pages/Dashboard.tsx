import { useNavigate } from 'react-router-dom';
import { LogOut, User, Briefcase } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';
import { ThemeToggle } from '../components/common/ThemeToggle';

export function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-ocean-950 transition-colors duration-300">
      {/* Header */}
      <header className="bg-white dark:bg-ocean-900 border-b border-slate-200 dark:border-ocean-700 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100">
            Dashboard
          </h1>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Button variant="ghost" onClick={handleLogout} className="flex items-center gap-2">
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* Welcome Card */}
        <div className="bg-white dark:bg-ocean-900 rounded-2xl shadow-lg p-8 mb-8 border border-slate-200 dark:border-ocean-700 transition-colors duration-300">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-2">
                Welcome, {user.name}!
              </h2>
              <p className="text-ocean-600 dark:text-slate-400">
                You're logged into FinQ
              </p>
            </div>

            {/* Role Badge */}
            <div className={`
              px-4 py-2 rounded-full font-medium text-sm
              ${user.role === 'Admin'
                ? 'bg-electric-100 dark:bg-electric-900/30 text-electric-700 dark:text-electric-400'
                : 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
              }
            `}>
              {user.role}
            </div>
          </div>

          {/* User Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-ocean-800/50 rounded-lg">
              <div className="p-2 bg-electric-100 dark:bg-electric-900/30 rounded-lg">
                <User className="w-5 h-5 text-electric-600 dark:text-electric-400" />
              </div>
              <div>
                <p className="text-sm text-ocean-600 dark:text-slate-400">Email</p>
                <p className="font-medium text-ocean-900 dark:text-slate-100">{user.email}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-ocean-800/50 rounded-lg">
              <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
                <Briefcase className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <p className="text-sm text-ocean-600 dark:text-slate-400">Company</p>
                <p className="font-medium text-ocean-900 dark:text-slate-100">{user.company}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Placeholder Card */}
        <div className="bg-gradient-to-br from-electric-500 to-emerald-500 rounded-2xl shadow-lg p-12 text-center text-white">
          <h3 className="text-4xl font-bold font-mono mb-4">
            Query Interface Coming Soon
          </h3>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
            Phase 2 will include the natural language query interface, SQL visualization,
            and real-time insights dashboard.
          </p>
          <div className="inline-flex items-center gap-2 px-6 py-3 bg-white/20 backdrop-blur-sm rounded-lg">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span className="font-medium">In Development</span>
          </div>
        </div>
      </main>
    </div>
  );
}
