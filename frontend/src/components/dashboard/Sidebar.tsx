import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Database, BarChart3, ChevronLeft, ChevronRight, Zap, Lightbulb } from 'lucide-react';
import { useSidebar } from '../../hooks/useSidebar';

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Overview', end: true },
  { to: '/dashboard/query', icon: MessageSquare, label: 'Ask FinQ' },
  { to: '/dashboard/insights', icon: Lightbulb, label: 'Insights' },
  { to: '/dashboard/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/dashboard/explorer', icon: Database, label: 'Data Explorer' }
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

      {/* Sidebar - clean white, active: light purple + blue left border */}
      <aside
        className={`
          sidebar-3d fixed md:sticky top-0 left-0 h-screen
          bg-white dark:bg-ocean-900 border-r border-slate-200 dark:border-ocean-700
          transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] z-50
          flex flex-col
          ${isOpen ? 'w-64' : 'w-0 md:w-16'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-center border-b border-slate-200 dark:border-ocean-700 px-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-electric-500 rounded-xl transition-smooth">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {isOpen && (
              <span className="text-xl font-bold text-ocean-900 dark:text-slate-100 whitespace-nowrap transition-opacity duration-200 font-sans">
                FinQ
              </span>
            )}
          </div>
        </div>

        {/* Navigation - Menu style with active left border */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          <p className="px-3 py-2 text-xs font-semibold text-ocean-500 dark:text-slate-500 uppercase tracking-wider">
            {isOpen ? 'Menu' : ''}
          </p>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-smooth border-l-[3px] ${
                  isActive
                    ? 'bg-electric-50 dark:bg-electric-900/20 text-electric-600 dark:text-electric-400 border-electric-500'
                    : 'border-transparent text-ocean-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-ocean-800'
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
