import { MessageSquare, BarChart3, Code2 } from 'lucide-react';

const features = [
  {
    icon: MessageSquare,
    title: 'Natural Language Queries',
    description: 'Ask questions in plain English, just like you\'re talking to a colleague. No SQL knowledge required.'
  },
  {
    icon: BarChart3,
    title: 'Instant Visualizations',
    description: 'Automatically generate beautiful charts and graphs from your data. Understand trends at a glance.'
  },
  {
    icon: Code2,
    title: 'SQL Transparency',
    description: 'See the generated SQL queries and learn as you go. Full transparency into every database operation.'
  }
];

export function Features() {
  return (
    <section id="features" className="py-24 bg-white dark:bg-ocean-950 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Title */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold font-mono text-ocean-900 dark:text-slate-100 mb-4">
            Powerful Features
          </h2>
          <p className="text-lg text-ocean-600 dark:text-slate-400 max-w-2xl mx-auto">
            Everything you need to turn financial data into actionable insights
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="p-8 rounded-2xl border-2 border-slate-200 dark:border-ocean-700
                          hover:border-electric-500 dark:hover:border-electric-500
                          hover:shadow-xl transition-all duration-300
                          bg-white dark:bg-ocean-900 group"
              >
                {/* Icon */}
                <div className="w-14 h-14 rounded-lg bg-electric-100 dark:bg-electric-900/30
                               flex items-center justify-center mb-4
                               group-hover:scale-110 transition-transform duration-300">
                  <Icon className="w-7 h-7 text-electric-600 dark:text-electric-400" />
                </div>

                {/* Title */}
                <h3 className="text-xl font-semibold font-mono text-ocean-900 dark:text-slate-100 mb-3">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-ocean-600 dark:text-slate-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
