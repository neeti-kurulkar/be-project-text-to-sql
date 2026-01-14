import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ChartContainer } from './ChartContainer';
import type { QuarterlyRevenueData } from '../../types/charts';

interface QuarterlyRevenueProps {
  data: QuarterlyRevenueData[];
}

const YEAR_COLORS: Record<string, string> = {
  y2018: '#94A3B8',
  y2019: '#3B82F6',
  y2020: '#10B981',
  y2021: '#F59E0B',
  y2022: '#8B5CF6',
  y2023: '#EC4899',
};

export function QuarterlyRevenue({ data }: QuarterlyRevenueProps) {
  // Dynamically extract year keys from data
  const yearKeys = data.length > 0
    ? Object.keys(data[0]).filter(key => key.startsWith('y') && key !== 'quarter')
    : [];

  return (
    <ChartContainer
      title="Quarterly Revenue"
      description="Revenue comparison by quarter across years"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-ocean-700" />
          <XAxis
            dataKey="quarter"
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
            label={{ value: 'Revenue ($K)', angle: -90, position: 'insideLeft', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-ocean-900)',
              border: '1px solid var(--color-ocean-700)',
              borderRadius: '8px',
              color: 'white'
            }}
            formatter={(value) => `$${Number(value || 0).toFixed(2)}K`}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="circle"
          />
          {yearKeys.map((yearKey) => (
            <Bar
              key={yearKey}
              dataKey={yearKey}
              fill={YEAR_COLORS[yearKey] || '#3B82F6'}
              name={yearKey.replace('y', '')}
              radius={[8, 8, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
