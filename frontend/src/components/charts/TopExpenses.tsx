import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ChartContainer } from './ChartContainer';
import type { TopExpenseData } from '../../types/charts';

interface TopExpensesProps {
  data: TopExpenseData[];
}

export function TopExpenses({ data }: TopExpensesProps) {
  return (
    <ChartContainer
      title="Top 5 Expense Accounts"
      description="Highest expense categories"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 10, left: 100, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-ocean-700" />
          <XAxis
            type="number"
            tick={{ fontSize: 12 }}
            className="fill-ocean-600 dark:fill-slate-400"
          />
          <YAxis
            type="category"
            dataKey="account"
            tick={{ fontSize: 11 }}
            className="fill-ocean-600 dark:fill-slate-400"
            width={90}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--color-ocean-900)',
              border: '1px solid var(--color-ocean-700)',
              borderRadius: '8px',
              color: 'white'
            }}
            formatter={(value) => [`$${Number(value || 0).toFixed(2)}K`, 'Amount']}
          />
          <Bar dataKey="amount" fill="#F59E0B" radius={[0, 8, 8, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
