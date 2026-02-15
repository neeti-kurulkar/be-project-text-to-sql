import { type ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

export function Card({ children, className = '', title, description }: CardProps) {
  return (
    <div className={`card-3d bg-white dark:bg-ocean-900 rounded-2xl border border-slate-200 dark:border-ocean-700 p-6 ${className}`}>
      {title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-ocean-900 dark:text-slate-100 font-sans">
            {title}
          </h3>
          {description && (
            <p className="text-sm text-ocean-600 dark:text-slate-400 mt-1 font-sans">
              {description}
            </p>
          )}
        </div>
      )}
      {children}
    </div>
  );
}
