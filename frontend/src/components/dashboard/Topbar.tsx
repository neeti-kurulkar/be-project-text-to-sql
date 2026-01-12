import { Menu } from 'lucide-react';
import { ThemeToggle } from '../common/ThemeToggle';
import { UserMenu } from './UserMenu';
import { useSidebar } from '../../hooks/useSidebar';

interface TopbarProps {
  title: string;
}

export function Topbar({ title }: TopbarProps) {
  const { toggle } = useSidebar();

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-ocean-900 border-b border-slate-200 dark:border-ocean-700 transition-colors duration-300">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-4">
          <button
            onClick={toggle}
            className="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-ocean-800 transition-colors duration-200"
          >
            <Menu className="w-5 h-5 text-ocean-600 dark:text-slate-400" />
          </button>
          <h1 className="text-2xl font-bold font-mono text-ocean-900 dark:text-slate-100">
            {title}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
