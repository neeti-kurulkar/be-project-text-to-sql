import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { REGIONAL_DISTRIBUTION_DATA } from '../../utils/mockData';
import { ChartContainer } from './ChartContainer';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B'];

export function RegionalDistribution() {
  return (
    <ChartContainer
      title="Regional Distribution"
      description="Revenue distribution by region"
    >
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={REGIONAL_DISTRIBUTION_DATA}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(props) => {
              const entry = REGIONAL_DISTRIBUTION_DATA[props.index];
              return `${entry.region} ${entry.percentage}%`;
            }}
            outerRadius={100}
            innerRadius={60}
            fill="#8884d8"
            dataKey="value"
          >
            {REGIONAL_DISTRIBUTION_DATA.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
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
        </PieChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
