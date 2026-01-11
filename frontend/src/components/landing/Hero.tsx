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

      <div className="relative max-w-4xl mx-auto px-6 py-24 text-center flex flex-col items-center justify-center min-h-[90vh]">
        {/* Headline */}
        <h1 className="text-5xl md:text-6xl font-bold font-mono text-white mb-6 animate-fadeIn">
          Ask Questions. Get Insights.
          <br />
          <span className="text-electric-400">Skip the SQL.</span>
        </h1>

        {/* Subheadline */}
        <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-2xl animate-fadeIn" style={{ animationDelay: '0.2s' }}>
          FinQ transforms your natural language questions into powerful SQL queries
          and beautiful visualizations. No database expertise required.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 animate-fadeIn" style={{ animationDelay: '0.4s' }}>
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
