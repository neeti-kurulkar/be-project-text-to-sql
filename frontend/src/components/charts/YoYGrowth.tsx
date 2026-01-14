import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { ChartContainer } from './ChartContainer';
import type { YoYGrowthData } from '../../types/charts';

interface YoYGrowthProps {
  data: YoYGrowthData[];
}

export function YoYGrowth({ data }: YoYGrowthProps) {
  return (
    <ChartContainer
      title="Year-over-Year Growth"
      description="Annual revenue with growth rate"
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 40, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-ocean-700" />
          <XAxis
            dataKey="year"
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
          />
          <YAxis
            yAxisId="left"
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
            label={{ value: 'Revenue ($K)', angle: -90, position: 'insideLeft', fontSize: 12 }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
            label={{ value: 'Growth %', angle: 90, position: 'insideRight', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-ocean-900)',
              border: '1px solid var(--color-ocean-700)',
              borderRadius: '8px',
              color: 'white'
            }}
            formatter={(value, name) => {
              if (name === 'Growth Rate') return [`${Number(value).toFixed(1)}%`, name];
              return [`$${Number(value).toFixed(2)}K`, name];
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Bar
            yAxisId="left"
            dataKey="revenue"
            fill="#3B82F6"
            name="Revenue"
            radius={[8, 8, 0, 0]}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="growthRate"
            stroke="#10B981"
            strokeWidth={3}
            name="Growth Rate"
            dot={{ fill: '#10B981', r: 6 }}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
