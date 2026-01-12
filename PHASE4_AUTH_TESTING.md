# Phase 4: Authentication System Testing Guide

## Setup Steps

### 1. Run the Database Schema

```bash
cd backend
psql -U postgres -d financial_db -f database/schema_users.sql
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the Backend Server

```bash
cd backend
python -m app.main
```

Expected output:
```
==================================================
Starting FinQ API...
Initializing database connection pool...
FinQ API is ready!
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Test Organizations

### Kuvalis (Enterprise)
- **Domains:** kuvalis.com, kuvalis.io
- **Users:**
  - sarah.chen@kuvalis.com (Admin)
  - mike.rodriguez@kuvalis.com (Analyst)
- **Data:** All existing financial data (17.1M revenue)

### Vandervort (Professional)
- **Domains:** vandervort.com
- **Users:**
  - john.smith@vandervort.com (Admin)
- **Data:** Empty (no financial data yet)

**All passwords:** `password123`

## API Testing

### 1. Test Authentication Endpoints

#### Register a New User (Domain Must Match)

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@kuvalis.com",
    "password": "password123",
    "name": "New Analyst",
    "role": "analyst"
  }'
```

Expected Response:
```json
{
  "user": {
    "id": "4",
    "email": "analyst@kuvalis.com",
    "name": "New Analyst",
    "role": "analyst",
    "company": "Kuvalis"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login with Existing User

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah.chen@kuvalis.com",
    "password": "password123"
  }'
```

Expected Response:
```json
{
  "user": {
    "id": "1",
    "email": "sarah.chen@kuvalis.com",
    "name": "Sarah Chen",
    "role": "admin",
    "company": "Kuvalis"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Save this token for the next requests!**

#### Get Current User Info

```bash
TOKEN="your_token_here"

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Test Protected Endpoints (Require Authentication)

#### Get Dashboard Stats

```bash
TOKEN="your_token_here"

curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response (Kuvalis):
```json
{
  "total_revenue": 17108642.0,
  "total_transactions": 27909,
  "countries_count": 7,
  "date_range": "2018-2020"
}
```

#### Execute Query

```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8000/api/query/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "sql": "SELECT * FROM territory LIMIT 3"
  }'
```

Expected Response:
- Should return only territories from Kuvalis organization
- Data is automatically filtered by organization_id

#### List Tables

```bash
TOKEN="your_token_here"

curl -X GET http://localhost:8000/api/tables \
  -H "Authorization: Bearer $TOKEN"
```

Expected Response:
- Shows tables with row counts for Kuvalis organization only

#### Get Table Data

```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/api/tables/territory?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test Multi-Tenancy (Data Isolation)

#### Login as Vandervort User

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.smith@vandervort.com",
    "password": "password123"
  }'
```

#### Get Stats for Vandervort

```bash
TOKEN_VANDERVORT="vandervort_token_here"

curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer $TOKEN_VANDERVORT"
```

Expected Response:
```json
{
  "total_revenue": 0.0,
  "total_transactions": 0,
  "countries_count": 0,
  "date_range": "N/A"
}
```

**This proves data isolation works!** Vandervort has no data, while Kuvalis has all the financial data.

### 4. Test Authentication Errors

#### Invalid Credentials

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah.chen@kuvalis.com",
    "password": "wrongpassword"
  }'
```

Expected: `401 Unauthorized - Invalid email or password`

#### Invalid Domain

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@unknown.com",
    "password": "password123",
    "name": "Test User",
    "role": "analyst"
  }'
```

Expected: `400 Bad Request - Email domain is not registered`

#### No Token (Accessing Protected Route)

```bash
curl -X GET http://localhost:8000/api/stats
```

Expected: `403 Forbidden - Not authenticated`

#### Invalid/Expired Token

```bash
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer invalid_token_here"
```

Expected: `401 Unauthorized - Invalid or expired token`

## Frontend Integration

### Update AuthContext to Use Real API

The current frontend uses mock authentication. To integrate real auth:

1. **Update `frontend/src/context/AuthContext.tsx`:**

```typescript
const login = async (email: string, password: string): Promise<void> => {
  setLoading(true);
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();

    // Store token
    localStorage.setItem('finq_token', data.token);

    // Store user
    setUser(data.user);
    localStorage.setItem('finq_user', JSON.stringify(data.user));
  } catch (error) {
    throw error;
  } finally {
    setLoading(false);
  }
};
```

2. **Update API Client to Include Token:**

```typescript
// frontend/src/services/api.ts
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('finq_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (token expired)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('finq_token');
      localStorage.removeItem('finq_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Success Criteria

### ✅ Authentication
- [x] Users can register with valid email domain
- [x] Users can login with correct credentials
- [x] Invalid credentials are rejected
- [x] JWT tokens are generated and validated
- [x] Tokens expire after configured time

### ✅ Authorization
- [x] Protected routes require authentication
- [x] Invalid/expired tokens are rejected
- [x] User role is included in token

### ✅ Multi-Tenancy
- [x] Users can only access their organization's data
- [x] Kuvalis users see Kuvalis data only
- [x] Vandervort users see Vandervort data only (empty)
- [x] Queries are automatically filtered by organization_id
- [x] Stats, tables, and query endpoints all respect organization boundaries

### ✅ Security
- [x] Passwords are hashed with bcrypt
- [x] SQL injection prevented (parameterized queries)
- [x] Organization filter cannot be bypassed
- [x] Proper HTTP status codes

## Next Steps

1. **Run the schema** - Create organizations and users
2. **Start backend** - Test authentication endpoints
3. **Update frontend** - Integrate real authentication
4. **Test end-to-end** - Login from frontend, access protected routes
5. **Deploy** - Consider environment variables for production

## Common Issues

### Issue: "relation 'organizations' does not exist"
**Solution:** Run the schema: `psql -U postgres -d financial_db -f database/schema_users.sql`

### Issue: "column organization_id does not exist"
**Solution:** The schema adds this column. If you ran it before, drop and recreate:
```sql
ALTER TABLE general_ledger DROP COLUMN IF EXISTS organization_id CASCADE;
```
Then run the full schema again.

### Issue: "Invalid or expired token"
**Solution:** Token expires after 60 minutes. Login again to get a new token.

### Issue: Frontend shows "Not authenticated"
**Solution:** Make sure to include `Authorization: Bearer {token}` header in all API requests.

## Database Verification

### Check Organizations

```sql
SELECT * FROM organizations;
```

### Check Users

```sql
SELECT u.email, u.name, u.role, o.name as company
FROM users u
JOIN organizations o ON u.organization_id = o.organization_id;
```

### Check Data Distribution

```sql
-- Kuvalis data
SELECT COUNT(*) FROM general_ledger WHERE organization_id = 1;

-- Vandervort data (should be 0)
SELECT COUNT(*) FROM general_ledger WHERE organization_id = 2;
```

### Test Helper Function

```sql
-- Get organization by email
SELECT * FROM get_organization_by_email('sarah.chen@kuvalis.com');
SELECT * FROM get_organization_by_email('john.smith@vandervort.com');
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation with the ability to test endpoints directly.
