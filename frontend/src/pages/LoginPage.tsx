import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Quote } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { LoginForm } from '../components/auth/LoginForm';

export function LoginPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding (Hidden on mobile) */}
      <div className="hidden lg:flex lg:w-2/5 bg-gradient-to-br from-electric-600 to-emerald-600 p-12 flex-col justify-between relative overflow-hidden">
        {/* Decorative background pattern */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, white 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }} />

        <div className="relative z-10">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-12">
            <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <span className="text-4xl font-bold font-mono text-white">
              FinQ
            </span>
          </div>

          {/* Quote/Testimonial */}
          <div className="mt-24">
            <Quote className="w-12 h-12 text-white/40 mb-6" />
            <blockquote className="text-2xl font-medium text-white mb-6 leading-relaxed">
              "FinQ transformed how we access financial insights. No more waiting for analysts."
            </blockquote>
            <cite className="text-white/80 not-italic">
              <p className="font-semibold">Sarah Chen</p>
              <p className="text-sm">CFO, Acme Corp</p>
            </cite>
          </div>
        </div>

        {/* Bottom tagline */}
        <p className="relative z-10 text-white/80 text-lg">
          Ask Questions. Get Insights. Skip the SQL.
        </p>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-white dark:bg-ocean-950 transition-colors duration-300">
        <LoginForm />
      </div>
    </div>
  );
}
