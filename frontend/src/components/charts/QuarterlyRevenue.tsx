import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { QUARTERLY_REVENUE_DATA } from '../../utils/mockData';
import { ChartContainer } from './ChartContainer';

export function QuarterlyRevenue() {
  return (
    <ChartContainer
      title="Quarterly Revenue"
      description="Revenue comparison by quarter across years"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={QUARTERLY_REVENUE_DATA} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
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
          <Bar dataKey="y2018" fill="#94A3B8" name="2018" radius={[8, 8, 0, 0]} />
          <Bar dataKey="y2019" fill="#3B82F6" name="2019" radius={[8, 8, 0, 0]} />
          <Bar dataKey="y2020" fill="#10B981" name="2020" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
