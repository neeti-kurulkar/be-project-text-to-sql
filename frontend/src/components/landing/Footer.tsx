import { Zap } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-ocean-900 text-slate-300 py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Column 1: Logo & Tagline */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-electric-500 rounded-lg">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-2xl font-bold font-mono text-white">
                FinQ
              </span>
            </div>
            <p className="text-slate-400 leading-relaxed">
              Ask Questions. Get Insights. Skip the SQL.
            </p>
          </div>

          {/* Column 2: Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="hover:text-electric-400 transition-colors">
                  About
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-electric-400 transition-colors">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-electric-400 transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-electric-400 transition-colors">
                  Terms of Service
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Copyright */}
          <div className="md:text-right">
            <p className="text-slate-400">
              © 2026 FinQ. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
