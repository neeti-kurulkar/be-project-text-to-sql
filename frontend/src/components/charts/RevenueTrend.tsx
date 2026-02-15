import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { ChartContainer } from './ChartContainer';
import type { RevenueTrendData } from '../../types/charts';

interface RevenueTrendProps {
  data: RevenueTrendData[];
}

export function RevenueTrend({ data }: RevenueTrendProps) {
  return (
    <ChartContainer
      title="Revenue Trend"
      description="Monthly revenue over time"
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-ocean-700" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 10 }}
            className="fill-ocean-600 dark:fill-slate-400"
            interval="preserveStartEnd"
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
            formatter={(value) => [`$${Number(value || 0).toFixed(2)}K`, 'Revenue']}
          />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#10B981"
            strokeWidth={3}
            fill="url(#revenueGradient)"
            isAnimationActive
            animationBegin={0}
            animationDuration={700}
            animationEasing="ease-out"
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
