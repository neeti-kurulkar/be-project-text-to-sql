import { type QueryResult, type SuggestedQuestion } from '../types/query';
import { type TableInfo } from '../types/data';

// Quick Stats Data
export const QUICK_STATS = {
  totalRevenue: '12.4',
  totalTransactions: '27,909',
  countries: '7',
  dateRange: '2018-2020'
};

// Suggested Questions
export const SUGGESTED_QUESTIONS: SuggestedQuestion[] = [
  { id: '1', question: 'What was our total revenue in 2020?', category: 'Revenue' },
  { id: '2', question: 'Show me revenue by country', category: 'Revenue' },
  { id: '3', question: 'Which quarter had the highest sales?', category: 'Sales' },
  { id: '4', question: 'What are the top 5 expense accounts?', category: 'Expenses' },
  { id: '5', question: 'Compare 2019 vs 2020 revenue', category: 'Revenue' },
  { id: '6', question: 'Show me quarterly revenue trends', category: 'Trends' },
  { id: '7', question: "What's our revenue in USA?", category: 'Revenue' },
  { id: '8', question: 'List all countries we operate in', category: 'General' }
];

// Mock Query Responses (map question keywords to responses)
export const MOCK_QUERY_RESPONSES: Record<string, QueryResult> = {
  'total revenue in 2020': {
    columns: ['total_revenue'],
    rows: [{ total_revenue: '$4,856,234.67' }],
    rowCount: 1,
    explanation: 'The total revenue for 2020 was $4,856,234.67. This represents the sum of all revenue transactions across all territories during the fiscal year 2020.'
  },
  'revenue by country': {
    columns: ['country', 'revenue'],
    rows: [
      { country: 'USA', revenue: '$5,234,567.89' },
      { country: 'Canada', revenue: '$2,456,789.12' },
      { country: 'UK', revenue: '$1,987,654.32' },
      { country: 'Germany', revenue: '$1,234,567.89' },
      { country: 'France', revenue: '$987,654.32' },
      { country: 'Australia', revenue: '$765,432.10' },
      { country: 'New Zealand', revenue: '$456,789.01' }
    ],
    rowCount: 7,
    explanation: 'This shows the total revenue broken down by country. The USA is our largest market with $5.2M in revenue, followed by Canada with $2.5M.'
  },
  'highest sales': {
    columns: ['quarter', 'year', 'sales'],
    rows: [
      { quarter: 'Q4', year: 2020, sales: '$1,456,234.67' }
    ],
    rowCount: 1,
    explanation: 'Q4 2020 had the highest sales with $1,456,234.67. This represents strong performance during the holiday season.'
  },
  'top 5 expense': {
    columns: ['account_name', 'total_expenses'],
    rows: [
      { account_name: 'Cost of Sales', total_expenses: '$3,456,789.12' },
      { account_name: 'Salaries & Wages', total_expenses: '$2,345,678.90' },
      { account_name: 'Marketing', total_expenses: '$1,234,567.89' },
      { account_name: 'Rent & Utilities', total_expenses: '$987,654.32' },
      { account_name: 'Software & IT', total_expenses: '$765,432.10' }
    ],
    rowCount: 5,
    explanation: 'The top 5 expense accounts show that Cost of Sales ($3.5M) and Salaries & Wages ($2.3M) are our largest expense categories.'
  },
  'compare 2019 vs 2020': {
    columns: ['year', 'revenue', 'growth_rate'],
    rows: [
      { year: 2019, revenue: '$4,234,567.89', growth_rate: '12.5%' },
      { year: 2020, revenue: '$4,856,234.67', growth_rate: '14.7%' }
    ],
    rowCount: 2,
    explanation: 'Revenue grew from $4.2M in 2019 to $4.9M in 2020, representing a 14.7% year-over-year growth rate.'
  },
  'quarterly revenue trends': {
    columns: ['year', 'quarter', 'revenue'],
    rows: [
      { year: 2018, quarter: 'Q1', revenue: '$876,543.21' },
      { year: 2018, quarter: 'Q2', revenue: '$923,456.78' },
      { year: 2018, quarter: 'Q3', revenue: '$967,890.12' },
      { year: 2018, quarter: 'Q4', revenue: '$1,098,765.43' },
      { year: 2019, quarter: 'Q1', revenue: '$987,654.32' },
      { year: 2019, quarter: 'Q2', revenue: '$1,034,567.89' },
      { year: 2019, quarter: 'Q3', revenue: '$1,076,543.21' },
      { year: 2019, quarter: 'Q4', revenue: '$1,135,802.47' },
      { year: 2020, quarter: 'Q1', revenue: '$1,123,456.78' },
      { year: 2020, quarter: 'Q2', revenue: '$1,189,012.34' },
      { year: 2020, quarter: 'Q3', revenue: '$1,234,567.89' },
      { year: 2020, quarter: 'Q4', revenue: '$1,309,197.66' }
    ],
    rowCount: 12,
    explanation: 'Quarterly revenue shows consistent growth from 2018 to 2020, with Q4 typically being the strongest quarter each year.'
  },
  'revenue in usa': {
    columns: ['country', 'revenue'],
    rows: [
      { country: 'USA', revenue: '$5,234,567.89' }
    ],
    rowCount: 1,
    explanation: 'The total revenue from USA operations is $5,234,567.89, representing approximately 42% of our total global revenue.'
  },
  'all countries': {
    columns: ['country', 'territory_code'],
    rows: [
      { country: 'USA', territory_code: 'US' },
      { country: 'Canada', territory_code: 'CA' },
      { country: 'UK', territory_code: 'GB' },
      { country: 'Germany', territory_code: 'DE' },
      { country: 'France', territory_code: 'FR' },
      { country: 'Australia', territory_code: 'AU' },
      { country: 'New Zealand', territory_code: 'NZ' }
    ],
    rowCount: 7,
    explanation: 'We currently operate in 7 countries across North America, Europe, and Oceania.'
  }
};

// Default response for unknown questions
export const DEFAULT_QUERY_RESPONSE: QueryResult = {
  columns: ['message'],
  rows: [{ message: 'Mock data not available for this query' }],
  rowCount: 1,
  explanation: 'This is a mock response. In production, this query would be processed by the multi-agent system and executed against the actual database. The natural language would be converted to SQL, executed, and results would be returned with an explanation.'
};

// Function to get mock response for a question
export function getMockQueryResponse(question: string): QueryResult {
  const lowerQuestion = question.toLowerCase();

  // Find matching response based on keywords
  for (const [key, response] of Object.entries(MOCK_QUERY_RESPONSES)) {
    if (lowerQuestion.includes(key)) {
      return response;
    }
  }

  return DEFAULT_QUERY_RESPONSE;
}

// Function to generate mock SQL for a question
export function getMockSQL(question: string): string {
  const lowerQuestion = question.toLowerCase();

  if (lowerQuestion.includes('total revenue') && lowerQuestion.includes('2020')) {
    return `SELECT SUM(gl.amount) AS total_revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
WHERE EXTRACT(YEAR FROM gl.date) = 2020
  AND coa.class = 'Trading account' AND coa.subclass = 'Sales'`;
  }

  if (lowerQuestion.includes('revenue by country')) {
    return `SELECT t.country, SUM(gl.amount) AS revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
WHERE coa.class = 'Trading account' AND coa.subclass = 'Sales'
GROUP BY t.country
ORDER BY revenue DESC`;
  }

  if (lowerQuestion.includes('highest sales') || lowerQuestion.includes('quarter')) {
    return `SELECT c.quarter, c.year, SUM(gl.amount) AS sales
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Trading account' AND coa.subclass = 'Sales'
GROUP BY c.quarter, c.year
ORDER BY sales DESC
LIMIT 1`;
  }

  if (lowerQuestion.includes('top') && lowerQuestion.includes('expense')) {
    return `SELECT coa.account, SUM(ABS(gl.amount)) AS total_expenses
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
WHERE coa.class IN ('Operating account', 'Trading account')
  AND gl.amount < 0
GROUP BY coa.account
ORDER BY total_expenses DESC
LIMIT 5`;
  }

  if (lowerQuestion.includes('compare') && lowerQuestion.includes('2019') && lowerQuestion.includes('2020')) {
    return `SELECT EXTRACT(YEAR FROM gl.date) AS year, SUM(gl.amount) AS revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
WHERE EXTRACT(YEAR FROM gl.date) IN (2019, 2020)
  AND coa.class = 'Trading account' AND coa.subclass = 'Sales'
GROUP BY EXTRACT(YEAR FROM gl.date)
ORDER BY year`;
  }

  if (lowerQuestion.includes('quarterly') && lowerQuestion.includes('trend')) {
    return `SELECT c.year, c.quarter, SUM(gl.amount) AS revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN calendar c ON gl.date = c.date
WHERE coa.class = 'Trading account' AND coa.subclass = 'Sales'
GROUP BY c.year, c.quarter
ORDER BY c.year, c.quarter`;
  }

  if (lowerQuestion.includes('usa') || lowerQuestion.includes('united states')) {
    return `SELECT t.country, SUM(gl.amount) AS revenue
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
WHERE t.country = 'USA'
  AND coa.class = 'Trading account' AND coa.subclass = 'Sales'
GROUP BY t.country`;
  }

  if (lowerQuestion.includes('all countries') || (lowerQuestion.includes('list') && lowerQuestion.includes('countries'))) {
    return `SELECT country, region
FROM territory
ORDER BY country`;
  }

  // Default SQL for unknown queries - show sample data from general ledger
  return `SELECT gl.entry_no, gl.date, t.country, coa.class, coa.account, gl.amount
FROM general_ledger gl
JOIN chart_of_accounts coa ON gl.account_key = coa.account_key
JOIN territory t ON gl.territory_key = t.territory_key
LIMIT 10`;
}

// Table Information
export const TABLES: TableInfo[] = [
  { name: 'general_ledger', displayName: 'General Ledger', rowCount: 27909 },
  { name: 'chart_of_accounts', displayName: 'Chart of Accounts', rowCount: 54 },
  { name: 'territory', displayName: 'Territory', rowCount: 7 },
  { name: 'calendar', displayName: 'Calendar', rowCount: 1096 }
];

// Mock table data
export const MOCK_TABLE_DATA: Record<string, any[]> = {
  general_ledger: [
    { id: 1, date: '2020-01-15', account_id: 101, territory_id: 1, amount: 15234.56, description: 'Product Sales - Q1' },
    { id: 2, date: '2020-01-16', account_id: 201, territory_id: 2, amount: 8456.78, description: 'Service Revenue' },
    { id: 3, date: '2020-01-17', account_id: 102, territory_id: 1, amount: 12345.67, description: 'Consulting Fees' },
    { id: 4, date: '2020-01-18', account_id: 301, territory_id: 3, amount: 5678.90, description: 'License Revenue' },
    { id: 5, date: '2020-01-19', account_id: 401, territory_id: 1, amount: 23456.78, description: 'Product Sales - Premium' },
    { id: 6, date: '2020-01-20', account_id: 102, territory_id: 4, amount: 9876.54, description: 'Professional Services' },
    { id: 7, date: '2020-01-21', account_id: 201, territory_id: 2, amount: 14567.89, description: 'Subscription Revenue' },
    { id: 8, date: '2020-01-22', account_id: 101, territory_id: 5, amount: 11234.56, description: 'Product Sales - Standard' }
  ],
  chart_of_accounts: [
    { account_id: 101, account_name: 'Product Sales', account_type: 'Revenue', category: 'Operating Revenue' },
    { account_id: 102, account_name: 'Service Revenue', account_type: 'Revenue', category: 'Operating Revenue' },
    { account_id: 103, account_name: 'Consulting Revenue', account_type: 'Revenue', category: 'Operating Revenue' },
    { account_id: 201, account_name: 'Cost of Sales', account_type: 'Expense', category: 'Cost of Goods Sold' },
    { account_id: 202, account_name: 'Salaries & Wages', account_type: 'Expense', category: 'Operating Expenses' },
    { account_id: 203, account_name: 'Marketing', account_type: 'Expense', category: 'Operating Expenses' },
    { account_id: 204, account_name: 'Rent & Utilities', account_type: 'Expense', category: 'Operating Expenses' },
    { account_id: 205, account_name: 'Software & IT', account_type: 'Expense', category: 'Operating Expenses' }
  ],
  territory: [
    { territory_id: 1, country: 'USA', territory_code: 'US', region: 'North America' },
    { territory_id: 2, country: 'Canada', territory_code: 'CA', region: 'North America' },
    { territory_id: 3, country: 'UK', territory_code: 'GB', region: 'Europe' },
    { territory_id: 4, country: 'Germany', territory_code: 'DE', region: 'Europe' },
    { territory_id: 5, country: 'France', territory_code: 'FR', region: 'Europe' },
    { territory_id: 6, country: 'Australia', territory_code: 'AU', region: 'Oceania' },
    { territory_id: 7, country: 'New Zealand', territory_code: 'NZ', region: 'Oceania' }
  ],
  calendar: [
    { date: '2018-01-01', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Monday', fiscal_year: 2018 },
    { date: '2018-01-02', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Tuesday', fiscal_year: 2018 },
    { date: '2018-01-03', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Wednesday', fiscal_year: 2018 },
    { date: '2018-01-04', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Thursday', fiscal_year: 2018 },
    { date: '2018-01-05', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Friday', fiscal_year: 2018 },
    { date: '2018-01-06', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Saturday', fiscal_year: 2018 },
    { date: '2018-01-07', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Sunday', fiscal_year: 2018 },
    { date: '2018-01-08', year: 2018, quarter: 'Q1', month: 1, day_of_week: 'Monday', fiscal_year: 2018 }
  ]
};

// Chart Data
export const REVENUE_BY_COUNTRY_DATA = [
  { country: 'USA', revenue: 5234.57 },
  { country: 'Canada', revenue: 2456.79 },
  { country: 'UK', revenue: 1987.65 },
  { country: 'Germany', revenue: 1234.57 },
  { country: 'France', revenue: 987.65 },
  { country: 'Australia', revenue: 765.43 },
  { country: 'NZ', revenue: 456.79 }
];

export const REVENUE_TREND_DATA = [
  { month: 'Jan 2018', revenue: 876.54 },
  { month: 'Apr 2018', revenue: 923.46 },
  { month: 'Jul 2018', revenue: 967.89 },
  { month: 'Oct 2018', revenue: 1098.76 },
  { month: 'Jan 2019', revenue: 987.65 },
  { month: 'Apr 2019', revenue: 1034.57 },
  { month: 'Jul 2019', revenue: 1076.54 },
  { month: 'Oct 2019', revenue: 1135.80 },
  { month: 'Jan 2020', revenue: 1123.46 },
  { month: 'Apr 2020', revenue: 1189.01 },
  { month: 'Jul 2020', revenue: 1234.57 },
  { month: 'Oct 2020', revenue: 1309.20 }
];

export const QUARTERLY_REVENUE_DATA = [
  { quarter: 'Q1', y2018: 876.54, y2019: 987.65, y2020: 1123.46 },
  { quarter: 'Q2', y2018: 923.46, y2019: 1034.57, y2020: 1189.01 },
  { quarter: 'Q3', y2018: 967.89, y2019: 1076.54, y2020: 1234.57 },
  { quarter: 'Q4', y2018: 1098.76, y2019: 1135.80, y2020: 1309.20 }
];

export const TOP_EXPENSES_DATA = [
  { account: 'Cost of Sales', amount: 3456.79 },
  { account: 'Salaries & Wages', amount: 2345.68 },
  { account: 'Marketing', amount: 1234.57 },
  { account: 'Rent & Utilities', amount: 987.65 },
  { account: 'Software & IT', amount: 765.43 }
];

export const REGIONAL_DISTRIBUTION_DATA = [
  { region: 'North America', value: 7691.36, percentage: 62 },
  { region: 'Europe', value: 4209.87, percentage: 34 },
  { region: 'Oceania', value: 1222.22, percentage: 4 }
];
