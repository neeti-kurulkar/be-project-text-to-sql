import { type ReactNode } from 'react';

type BadgeVariant = 'blue' | 'green' | 'gray' | 'red' | 'amber';

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  blue: 'bg-electric-100 dark:bg-electric-900/30 text-electric-700 dark:text-electric-400',
  green: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400',
  gray: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
  red: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  amber: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
};

export function Badge({ children, variant = 'gray', className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
}
