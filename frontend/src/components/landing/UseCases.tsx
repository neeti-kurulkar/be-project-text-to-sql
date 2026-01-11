import { TrendingUp, Database, Users } from 'lucide-react';

const useCases = [
  {
    icon: TrendingUp,
    title: 'Finance Teams',
    description: 'Analyze revenue trends, track KPIs, and generate reports without waiting for data analysts.'
  },
  {
    icon: Database,
    title: 'Data Analysts',
    description: 'Query databases faster than writing SQL manually. Focus on insights, not syntax.'
  },
  {
    icon: Users,
    title: 'Business Leaders',
    description: 'Get instant answers to critical business questions. Make data-driven decisions in real-time.'
  }
];

export function UseCases() {
  return (
    <section className="py-24 bg-slate-50 dark:bg-ocean-800/50 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Title */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-4">
            Built for Modern Teams
          </h2>
          <p className="text-lg text-ocean-600 dark:text-slate-400 max-w-2xl mx-auto">
            Empowering professionals across your organization
          </p>
        </div>

        {/* Use Cases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {useCases.map((useCase, index) => {
            const Icon = useCase.icon;
            return (
              <div
                key={index}
                className="p-8 rounded-2xl border-2 border-slate-200 dark:border-ocean-700
                          hover:border-emerald-500 dark:hover:border-emerald-500
                          hover:shadow-xl transition-all duration-300
                          bg-white dark:bg-ocean-900 group"
              >
                {/* Icon */}
                <div className="w-14 h-14 rounded-lg bg-emerald-100 dark:bg-emerald-900/30
                               flex items-center justify-center mb-4
                               group-hover:scale-110 transition-transform duration-300">
                  <Icon className="w-7 h-7 text-emerald-600 dark:text-emerald-400" />
                </div>

                {/* Title */}
                <h3 className="text-xl font-semibold font-mono text-ocean-900 dark:text-slate-100 mb-3">
                  {useCase.title}
                </h3>

                {/* Description */}
                <p className="text-ocean-600 dark:text-slate-400 leading-relaxed">
                  {useCase.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
