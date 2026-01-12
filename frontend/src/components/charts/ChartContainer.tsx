import { type ReactNode } from 'react';
import { Card } from '../common/Card';

interface ChartContainerProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function ChartContainer({ title, description, children }: ChartContainerProps) {
  return (
    <Card title={title} description={description}>
      <div className="h-80">
        {children}
      </div>
    </Card>
  );
}
