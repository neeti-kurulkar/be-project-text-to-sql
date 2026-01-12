import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Database, BarChart3, ChevronLeft, ChevronRight, Zap } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Home', end: true },
  { to: '/dashboard/query', icon: MessageSquare, label: 'Ask Questions' },
  { to: '/dashboard/charts', icon: BarChart3, label: 'Charts' },
  { to: '/dashboard/data', icon: Database, label: 'View Data' }
];

export function Sidebar() {
  const { isOpen, toggle } = useSidebar();

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={toggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed md:sticky top-0 left-0 h-screen
          bg-white dark:bg-ocean-900 border-r border-slate-200 dark:border-ocean-700
          transition-all duration-300 ease-in-out z-50
          flex flex-col
          ${isOpen ? 'w-64' : 'w-0 md:w-16'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-center border-b border-slate-200 dark:border-ocean-700 px-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-electric-500 rounded-lg">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {isOpen && (
              <span className="text-xl font-bold font-mono text-ocean-900 dark:text-slate-100 whitespace-nowrap">
                FinQ
              </span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-electric-100 dark:bg-electric-900/30 text-electric-700 dark:text-electric-400'
                    : 'text-ocean-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-ocean-800'
                }`
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {isOpen && (
                <span className="font-medium whitespace-nowrap">{item.label}</span>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Toggle button */}
        <div className="p-3 border-t border-slate-200 dark:border-ocean-700">
          <button
            onClick={toggle}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg text-ocean-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-ocean-800 transition-colors duration-200"
          >
            {isOpen ? (
              <>
                <ChevronLeft className="w-5 h-5" />
                <span className="font-medium text-sm">Collapse</span>
              </>
            ) : (
              <ChevronRight className="w-5 h-5" />
            )}
          </button>
        </div>
      </aside>
    </>
  );
}
