import { ReactNode, ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  className?: string;
}

export function Button({
  children,
  variant = 'primary',
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const baseClasses = 'px-6 py-3 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-4 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-electric-500 hover:bg-electric-600 text-white shadow-lg hover:shadow-xl hover:scale-105 focus:ring-electric-500/30',
    secondary: 'border-2 border-electric-500 text-electric-600 dark:text-electric-400 hover:bg-electric-50 dark:hover:bg-ocean-800 focus:ring-electric-500/30',
    ghost: 'text-ocean-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-ocean-800 focus:ring-ocean-500/20'
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
