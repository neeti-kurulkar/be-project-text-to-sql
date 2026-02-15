import { Link } from 'react-router-dom';
import { Button } from '../common/Button';

export function Hero() {
  return (
    <section className="min-h-[90vh] bg-gradient-to-br from-ocean-900 via-ocean-800 to-ocean-700 relative overflow-hidden">
      {/* Subtle grid pattern overlay */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: `linear-gradient(to right, #3B82F6 1px, transparent 1px),
                          linear-gradient(to bottom, #3B82F6 1px, transparent 1px)`,
        backgroundSize: '80px 80px'
      }} />

      <div className="relative max-w-4xl mx-auto px-6 py-24 flex flex-col items-center justify-center min-h-[90vh] text-center">
        {/* Headline – three clear lines, balanced */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-8 leading-tight tracking-tight font-sans animate-fadeIn">
          <span className="block">Ask Questions.</span>
          <span className="block">Get Insights.</span>
          <span className="block text-electric-400">Skip the SQL.</span>
        </h1>

        {/* Subheadline – two lines, readable width */}
        <p className="text-lg md:text-xl text-slate-300 mb-12 max-w-xl mx-auto leading-relaxed animate-fadeIn" style={{ animationDelay: '0.2s' }}>
          FinQ transforms your natural language questions into powerful SQL queries and beautiful visualizations.
          <span className="block mt-2 text-slate-400">No database expertise required.</span>
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fadeIn" style={{ animationDelay: '0.4s' }}>
          <Link to="/login">
            <Button variant="primary" className="text-lg px-8 py-4">
              Get Started
            </Button>
          </Link>
          <a href="#features">
            <Button variant="secondary" className="text-lg px-8 py-4 border-white text-white hover:bg-white/10">
              Learn More
            </Button>
          </a>
        </div>
      </div>

      {/* Add fadeIn animation */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.8s ease-out forwards;
          opacity: 0;
        }
      `}</style>
    </section>
  );
}
