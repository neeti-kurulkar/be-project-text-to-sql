import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { ChartContainer } from './ChartContainer';
import type { ExpenseBreakdownData } from '../../types/charts';

interface ExpenseBreakdownProps {
  data: ExpenseBreakdownData[];
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

export function ExpenseBreakdown({ data }: ExpenseBreakdownProps) {
  // Dynamically extract category keys from data
  const categories = data.length > 0
    ? Object.keys(data[0]).filter(key => key !== 'month')
    : [];

  return (
    <ChartContainer
      title="Expense Breakdown"
      description="Monthly expenses by category"
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-ocean-700" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 10 }}
            className="fill-ocean-600 dark:fill-slate-400"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
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
          <Legend wrapperStyle={{ fontSize: '11px' }} />
          {categories.map((category, index) => (
            <Area
              key={category}
              type="monotone"
              dataKey={category}
              stackId="1"
              stroke={COLORS[index % COLORS.length]}
              fill={COLORS[index % COLORS.length]}
              fillOpacity={0.6}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
