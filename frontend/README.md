# Frontend Documentation

React TypeScript frontend for the Text-to-SQL Financial Analytics Platform. Built with React 19, Tailwind CSS 4, Vite, and Recharts.

## Directory Structure

```
frontend/
├── src/
│   ├── App.tsx                 # Main app with routing
│   ├── main.tsx                # Entry point
│   ├── index.css               # Global styles + Tailwind
│   │
│   ├── pages/                  # Page components
│   │   ├── LandingPage.tsx     # Public landing page
│   │   ├── LoginPage.tsx       # Authentication
│   │   ├── Dashboard.tsx       # Dashboard layout wrapper
│   │   ├── DashboardHome.tsx   # Main dashboard with KPIs
│   │   ├── QueryPage.tsx       # NL2SQL query interface
│   │   ├── ChartsPage.tsx      # Pre-built visualizations
│   │   ├── InsightsPage.tsx    # AI-generated insights
│   │   ├── DataPage.tsx        # Raw data explorer
│   │   ├── ProfilePage.tsx     # User profile
│   │   └── SettingsPage.tsx    # User settings
│   │
│   ├── components/
│   │   ├── auth/               # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   │
│   │   ├── charts/             # Chart components (Recharts)
│   │   │   ├── ChartContainer.tsx
│   │   │   ├── ChartLoading.tsx
│   │   │   ├── ChartError.tsx
│   │   │   ├── RevenueByCountry.tsx
│   │   │   ├── RevenueTrend.tsx
│   │   │   ├── QuarterlyRevenue.tsx
│   │   │   ├── ExpenseBreakdown.tsx
│   │   │   ├── YoYGrowth.tsx
│   │   │   ├── ProfitLossTrend.tsx
│   │   │   ├── RegionalDistribution.tsx
│   │   │   └── TopExpenses.tsx
│   │   │
│   │   ├── dashboard/          # Dashboard widgets
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── QuickStats.tsx
│   │   │   └── RecentQueries.tsx
│   │   │
│   │   ├── query/              # NL2SQL query components
│   │   │   ├── QueryInterface.tsx
│   │   │   ├── QueryInput.tsx
│   │   │   ├── QueryMessage.tsx
│   │   │   ├── QueryResults.tsx
│   │   │   └── SampleQuestions.tsx
│   │   │
│   │   ├── common/             # Shared UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Loading.tsx
│   │   │
│   │   ├── landing/            # Landing page sections
│   │   │   └── Hero.tsx
│   │   │
│   │   └── data/               # Data display components
│   │       └── DataTable.tsx
│   │
│   ├── services/
│   │   └── api.ts              # API client (axios)
│   │
│   ├── context/
│   │   └── AuthContext.tsx     # Authentication state
│   │
│   ├── hooks/
│   │   ├── useAuth.ts          # Auth hook
│   │   └── useApi.ts           # API hooks
│   │
│   ├── types/
│   │   ├── api.ts              # API response types
│   │   ├── charts.ts           # Chart data types
│   │   └── query.ts            # Query types
│   │
│   └── utils/
│       ├── exportCSV.ts        # CSV export utility
│       └── formatters.ts       # Number/date formatters
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## Pages

### Landing Page (`LandingPage.tsx`)

Public page for unauthenticated users. Redirects to dashboard if logged in.

### Login Page (`LoginPage.tsx`)

- Email/password form
- JWT token storage in localStorage
- Redirect to dashboard on success
- Error handling for invalid credentials

### Dashboard (`Dashboard.tsx`)

Layout wrapper with:
- Sidebar navigation
- Header with user info
- Content area (Outlet)

### Dashboard Home (`DashboardHome.tsx`)

Main dashboard showing:
- **KPI Cards**: Total revenue, transactions, countries, date range
- **Quick Stats**: Organization metrics
- **Charts Grid**: Revenue trend, expense breakdown, regional distribution
- **Recent Activity**: Recent queries (if any)

### Query Page (`QueryPage.tsx`)

NL2SQL interface:
- Chat-like message interface
- Sample questions for quick start
- Real-time query processing
- Results with SQL, table, insights, visualization

### Charts Page (`ChartsPage.tsx`)

Pre-built analytics:
- Revenue by country (bar chart)
- Revenue trend (line chart)
- Quarterly revenue (grouped bar)
- Regional distribution (pie chart)

### Insights Page (`InsightsPage.tsx`)

AI-generated insights:
- Revenue summary with YoY change
- Top markets analysis
- Growth trends
- Strategic recommendations
- Insight cards with expandable details

---

## Components

### Chart Components (`components/charts/`)

All chart components use Recharts and follow a consistent pattern:

```tsx
interface ChartProps {
  data: ChartDataType[];
  loading?: boolean;
  error?: string;
}

export function RevenueByCountry({ data, loading, error }: ChartProps) {
  if (loading) return <ChartLoading />;
  if (error) return <ChartError message={error} />;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="country" />
        <YAxis domain={[0, 'auto']} />
        <Tooltip />
        <Bar dataKey="revenue" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

**Available Charts**:

| Component | Chart Type | Use Case |
|-----------|------------|----------|
| `RevenueByCountry` | Bar | Revenue comparison by country |
| `RevenueTrend` | Line | Monthly revenue over time |
| `QuarterlyRevenue` | Grouped Bar | Quarter comparison across years |
| `ExpenseBreakdown` | Pie | Expense category distribution |
| `YoYGrowth` | Bar | Year-over-year growth rates |
| `ProfitLossTrend` | Area | Revenue vs expenses over time |
| `RegionalDistribution` | Pie | Revenue by region |
| `TopExpenses` | Horizontal Bar | Top expense categories |

### Query Components (`components/query/`)

**QueryInterface** (`QueryInterface.tsx`):
- Main container for NL2SQL feature
- Manages message history
- Handles API calls to backend
- Displays loading states

**QueryMessage** (`QueryMessage.tsx`):
- Renders individual messages (user/assistant)
- For assistant messages, includes:
  - Summary text
  - Key insights (collapsible)
  - Visualization (auto-generated chart)
  - SQL code block (toggle)
  - Data table (toggle)
  - Export CSV button

**QueryResults** (`QueryResults.tsx`):
- Renders tabular data
- Sortable columns
- Pagination for large results

**Dynamic Chart Rendering**:

```tsx
const renderChart = () => {
  const { chart_type, chart_config } = message.visualization;
  const data = chart_config.data;

  if (chart_type === 'bar') {
    return (
      <BarChart data={data}>
        <XAxis dataKey={chart_config.x_axis?.dataKey} />
        <YAxis domain={[0, 'auto']} />
        {chart_config.bars?.map((bar) => (
          <Bar key={bar.dataKey} dataKey={bar.dataKey} fill={bar.fill} />
        ))}
      </BarChart>
    );
  }
  // Similar for line, pie
};
```

### Dashboard Components (`components/dashboard/`)

**Sidebar** (`Sidebar.tsx`):
- Navigation links
- Active state highlighting
- Collapsible on mobile

**Header** (`Header.tsx`):
- Organization name
- User menu
- Logout button

**QuickStats** (`QuickStats.tsx`):
- KPI cards with icons
- Real-time data from API
- Loading skeleton states

### Auth Components (`components/auth/`)

**ProtectedRoute** (`ProtectedRoute.tsx`):
```tsx
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" />;

  return children;
}
```

---

## Services

### API Client (`services/api.ts`)

Axios-based API client with:
- Base URL configuration
- JWT token injection
- Response interceptors
- Error handling

```typescript
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions
export const login = (email: string, password: string) =>
  api.post('/api/auth/login', { email, password });

export const getQuickStats = () =>
  api.get('/api/stats');

export const getChartData = (chartType: string) =>
  api.get(`/api/charts/${chartType}`);

export const queryNL2SQL = (question: string) =>
  api.post('/api/nl2sql/query', { question });

export const getAutomatedInsights = () =>
  api.get('/api/insights/automated');
```

---

## Context

### Auth Context (`context/AuthContext.tsx`)

Provides authentication state across the app:

```typescript
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password);
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

## Types

### Query Types (`types/query.ts`)

```typescript
interface QueryMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql?: string;
  results?: QueryResults;
  insights?: Insights;
  visualization?: Visualization;
  executionTime?: number;
}

interface QueryResults {
  columns: string[];
  rows: Record<string, any>[];
  rowCount: number;
  explanation?: string;
}

interface Insights {
  summary: string;
  key_insights: string[];
  trends?: string[];
  anomalies?: string[];
}

interface Visualization {
  should_visualize: boolean;
  chart_type: 'bar' | 'line' | 'pie';
  chart_config: ChartConfig;
}
```

### Chart Types (`types/charts.ts`)

```typescript
interface ChartConfig {
  data: any[];
  title?: string;
  x_axis?: { dataKey: string; label?: string };
  y_axis?: { dataKey: string; label?: string };
  bars?: { dataKey: string; fill: string; name?: string }[];
  lines?: { dataKey: string; stroke: string; name?: string }[];
}

interface RevenueByCountryData {
  country: string;
  revenue: number;
}

interface RevenueTrendData {
  month: string;
  revenue: number;
}
```

---

## Routing

```tsx
// App.tsx
<Routes>
  {/* Public routes */}
  <Route path="/" element={<LandingPage />} />
  <Route path="/login" element={<LoginPage />} />

  {/* Protected routes */}
  <Route element={<ProtectedRoute><Dashboard /></ProtectedRoute>}>
    <Route path="/dashboard" element={<DashboardHome />} />
    <Route path="/dashboard/query" element={<QueryPage />} />
    <Route path="/dashboard/charts" element={<ChartsPage />} />
    <Route path="/dashboard/insights" element={<InsightsPage />} />
    <Route path="/dashboard/data" element={<DataPage />} />
    <Route path="/dashboard/profile" element={<ProfilePage />} />
    <Route path="/dashboard/settings" element={<SettingsPage />} />
  </Route>
</Routes>
```

---

## Styling

### Tailwind CSS 4

The project uses Tailwind CSS 4 with custom theme colors:

```css
/* index.css */
@import "tailwindcss";

@theme {
  --color-ocean-50: #f0f7ff;
  --color-ocean-100: #e0efff;
  --color-ocean-500: #3b82f6;
  --color-ocean-900: #1e3a5f;

  --color-electric-400: #60a5fa;
  --color-electric-500: #3b82f6;
  --color-electric-600: #2563eb;
}
```

### Design System

- **Colors**: Ocean blue palette for professional look
- **Typography**: System fonts with Inter fallback
- **Spacing**: Consistent 4px grid system
- **Components**: Rounded corners, subtle shadows
- **Dark mode**: Supported via Tailwind classes

---

## Development

### Running Locally

```bash
npm install
npm run dev
```

### Building for Production

```bash
npm run build
npm run preview
```

### Type Checking

```bash
npm run build  # Includes TypeScript compilation
```

### Linting

```bash
npm run lint
```

---

## Environment Variables

Create `.env` in the frontend directory (optional):

```env
VITE_API_URL=http://localhost:8000
```

Access in code:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | 19.x | UI library |
| react-router-dom | 7.x | Routing |
| tailwindcss | 4.x | Styling |
| recharts | 3.x | Charts |
| axios | 1.x | HTTP client |
| lucide-react | 0.4x | Icons |
| @headlessui/react | 2.x | Accessible UI components |
| clsx | 2.x | Conditional classnames |
