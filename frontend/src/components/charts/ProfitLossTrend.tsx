import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { ChartContainer } from './ChartContainer';
import type { ProfitLossData } from '../../types/charts';

interface ProfitLossTrendProps {
  data: ProfitLossData[];
}

export function ProfitLossTrend({ data }: ProfitLossTrendProps) {
  return (
    <ChartContainer
      title="Profit & Loss Trend"
      description="Monthly revenue vs expenses with net income"
    >
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="plRevenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="plExpenseGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
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
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-ocean-900)',
              border: '1px solid var(--color-ocean-700)',
              borderRadius: '8px',
              color: 'white'
            }}
            formatter={(value) => `$${Number(value).toFixed(2)}K`}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#10B981"
            fill="url(#plRevenueGradient)"
            name="Revenue"
            isAnimationActive
            animationBegin={0}
            animationDuration={700}
            animationEasing="ease-out"
          />
          <Area
            type="monotone"
            dataKey="expenses"
            stroke="#EF4444"
            fill="url(#plExpenseGradient)"
            name="Expenses"
            isAnimationActive
            animationBegin={0}
            animationDuration={700}
            animationEasing="ease-out"
          />
          <Line
            type="monotone"
            dataKey="net"
            stroke="#3B82F6"
            strokeWidth={2}
            name="Net Income"
            dot={false}
            isAnimationActive
            animationBegin={0}
            animationDuration={700}
            animationEasing="ease-out"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
