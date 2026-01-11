import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-ocean-800 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-electric-500/30"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'dark' ? (
        <Moon className="w-5 h-5 text-slate-300 transition-transform duration-200" />
      ) : (
        <Sun className="w-5 h-5 text-ocean-700 transition-transform duration-200" />
      )}
    </button>
  );
}
