export interface RevenueByCountryData {
  country: string;
  revenue: number;
}

export interface RevenueTrendData {
  month: string;
  revenue: number;
}

export interface QuarterlyRevenueData {
  quarter: string;
  [key: string]: string | number;
}

export interface TopExpenseData {
  account: string;
  amount: number;
}

export interface RegionalDistributionData {
  region: string;
  value: number;
  percentage: number;
}

export interface ProfitLossData {
  month: string;
  revenue: number;
  expenses: number;
  net: number;
}

export interface YoYGrowthData {
  year: number;
  revenue: number;
  prevRevenue: number | null;
  growthRate: number | null;
}

export interface ExpenseBreakdownData {
  month: string;
  [key: string]: string | number;
}

export interface AllChartsData {
  revenueByCountry: RevenueByCountryData[];
  revenueTrend: RevenueTrendData[];
  quarterlyRevenue: QuarterlyRevenueData[];
  topExpenses: TopExpenseData[];
  regionalDistribution: RegionalDistributionData[];
  profitLoss: ProfitLossData[];
  yoyGrowth: YoYGrowthData[];
  expenseBreakdown: ExpenseBreakdownData[];
}
