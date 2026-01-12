import { Menu } from '@headlessui/react';
import { User, Settings, LogOut, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../common/Badge';

export function UserMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  const initials = user.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase();

  return (
    <Menu as="div" className="relative">
      <Menu.Button className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-ocean-800 transition-colors duration-200">
        <div className="w-8 h-8 rounded-full bg-electric-500 text-white flex items-center justify-center font-semibold text-sm">
          {initials}
        </div>
        <div className="hidden sm:block text-left">
          <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
            {user.name}
          </div>
          <div className="text-xs text-ocean-600 dark:text-slate-400">
            {user.role}
          </div>
        </div>
        <ChevronDown className="w-4 h-4 text-ocean-600 dark:text-slate-400" />
      </Menu.Button>

      <Menu.Items className="absolute right-0 mt-2 w-56 origin-top-right rounded-lg bg-white dark:bg-ocean-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none border border-slate-200 dark:border-ocean-700 overflow-hidden">
        {/* User Info */}
        <div className="px-4 py-3 border-b border-slate-200 dark:border-ocean-700">
          <div className="text-sm font-medium text-ocean-900 dark:text-slate-100">
            {user.name}
          </div>
          <div className="text-xs text-ocean-600 dark:text-slate-400 mt-0.5">
            {user.email}
          </div>
          <div className="mt-2">
            <Badge variant={user.role === 'Admin' ? 'blue' : 'green'}>
              {user.role}
            </Badge>
          </div>
        </div>

        {/* Menu Items */}
        <div className="py-1">
          <Menu.Item>
            {({ active }) => (
              <button
                onClick={() => navigate('/dashboard/profile')}
                className={`${
                  active ? 'bg-slate-100 dark:bg-ocean-700' : ''
                } group flex w-full items-center gap-2 px-4 py-2 text-sm text-ocean-900 dark:text-slate-100`}
              >
                <User className="w-4 h-4 text-ocean-600 dark:text-slate-400" />
                Profile
              </button>
            )}
          </Menu.Item>
          <Menu.Item>
            {({ active }) => (
              <button
                onClick={() => navigate('/dashboard/settings')}
                className={`${
                  active ? 'bg-slate-100 dark:bg-ocean-700' : ''
                } group flex w-full items-center gap-2 px-4 py-2 text-sm text-ocean-900 dark:text-slate-100`}
              >
                <Settings className="w-4 h-4 text-ocean-600 dark:text-slate-400" />
                Settings
              </button>
            )}
          </Menu.Item>
        </div>

        {/* Logout */}
        <div className="py-1 border-t border-slate-200 dark:border-ocean-700">
          <Menu.Item>
            {({ active }) => (
              <button
                onClick={handleLogout}
                className={`${
                  active ? 'bg-slate-100 dark:bg-ocean-700' : ''
                } group flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400`}
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            )}
          </Menu.Item>
        </div>
      </Menu.Items>
    </Menu>
  );
}
