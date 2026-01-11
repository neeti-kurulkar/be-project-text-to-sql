import { Zap } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ThemeToggle } from '../common/ThemeToggle';
import { Button } from '../common/Button';

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-ocean-900/80 backdrop-blur-lg border-b border-slate-200 dark:border-ocean-700 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="p-2 bg-electric-500 rounded-lg group-hover:scale-110 transition-transform duration-200">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold font-mono text-electric-600 dark:text-electric-400">
              FinQ
            </span>
          </Link>

          {/* Right Side: Theme Toggle + Login Button */}
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Link to="/login">
              <Button variant="ghost">
                Log In
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
