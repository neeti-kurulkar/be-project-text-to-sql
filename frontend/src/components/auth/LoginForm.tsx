import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../common/Input';
import { Button } from '../common/Button';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      // Add shake animation to form
      const form = e.currentTarget as HTMLFormElement;
      form.classList.add('animate-shake');
      setTimeout(() => form.classList.remove('animate-shake'), 500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      {/* Title */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-2">
          Welcome back
        </h2>
        <p className="text-ocean-600 dark:text-slate-400">
          Enter your credentials to access FinQ
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email Input */}
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your company email"
          required
        />

        {/* Password Input with Toggle */}
        <div className="relative">
          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-11 text-ocean-500 dark:text-slate-400 hover:text-ocean-700 dark:hover:text-slate-300 transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? (
              <EyeOff className="w-5 h-5" />
            ) : (
              <Eye className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Remember Me Checkbox */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="remember-me"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="w-4 h-4 text-electric-500 border-slate-300 dark:border-ocean-700 rounded focus:ring-electric-500/30"
          />
          <label
            htmlFor="remember-me"
            className="ml-2 text-sm text-ocean-700 dark:text-slate-300"
          >
            Remember me
          </label>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          </div>
        )}

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          className="w-full py-4 text-lg font-semibold"
          disabled={loading}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              Signing in...
            </span>
          ) : (
            'Sign In'
          )}
        </Button>
      </form>

      {/* Shake Animation */}
      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }
        .animate-shake {
          animation: shake 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
}
