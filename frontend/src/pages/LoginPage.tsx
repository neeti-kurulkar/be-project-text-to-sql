import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Zap, Quote, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { LoginForm } from '../components/auth/LoginForm';
import { Fintech3D } from '../components/common/Fintech3D';

export function LoginPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex login-fintech-bg">
      {/* Left Side - Fintech 3D + branding (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-2/5 login-fintech-panel p-12 flex-col justify-between relative overflow-hidden">
        {/* Ambient glow behind 3D */}
        <div className="absolute inset-0 login-fintech-glow" aria-hidden />

        <div className="relative z-10">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors mb-8 group"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            <span>Back to Home</span>
          </Link>

          <div className="flex items-center gap-3 mb-12">
            <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/10">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <span className="text-4xl font-bold font-sans text-white">
              FinQ
            </span>
          </div>

          {/* Central 3D component */}
          <div className="flex justify-center my-12">
            <div className="scale-150 origin-center">
              <Fintech3D />
            </div>
          </div>

          <div className="mt-8">
            <Quote className="w-12 h-12 text-electric-400/50 mb-6" />
            <blockquote className="text-xl font-medium text-white/95 mb-6 leading-relaxed font-sans">
              "FinQ transformed how we access financial insights. No more waiting for analysts."
            </blockquote>
            <cite className="text-white/70 not-italic font-sans">
              <p className="font-semibold">Sarah Chen</p>
              <p className="text-sm">CFO, Kuvalis Inc.</p>
            </cite>
          </div>
        </div>

        <p className="relative z-10 text-white/70 text-lg font-sans">
          Ask Questions. Get Insights. Skip the SQL.
        </p>
      </div>

      {/* Right Side - Login form on same fintech background */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 login-fintech-form relative">
        <div className="absolute inset-0 login-fintech-glow-subtle" aria-hidden />
        <Link
          to="/"
          className="lg:hidden absolute top-6 left-6 z-10 inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span>Back to Home</span>
        </Link>

        <div className="relative z-10 w-full max-w-md">
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
