# B2B SaaS Authentication & Multi-Tenancy Design

## Overview

FinQ is designed as a B2B SaaS platform where multiple organizations (tenants) can use the platform with complete data isolation. Users are authenticated based on their email domain and can only access their organization's data.

## Architecture

### Multi-Tenancy Approach

We use a **shared database with organization-based isolation** model:
- Single PostgreSQL database
- All tables include `organization_id` column
- Row-level security enforced by application logic
- Each query automatically filters by organization_id

**Why this approach?**
- ✅ Easier to manage and scale
- ✅ Simpler migrations and backups
- ✅ Cost-effective (no separate DB per tenant)
- ✅ Allows cross-organization analytics if needed
- ✅ Better resource utilization

## Database Schema

### Core Tables

#### 1. **organizations**
The main tenant table - each row represents a company using FinQ.

```sql
- organization_id (PK)
- name                    -- "Acme Corp"
- slug                    -- "acme-corp" (URL-friendly)
- subscription_tier       -- free, starter, professional, enterprise
- is_active               -- Can disable entire org
- max_users               -- Subscription limit
- settings (JSONB)        -- Org-specific configuration
- created_at, updated_at
```

#### 2. **email_domains**
Maps email domains to organizations. Supports multiple domains per org.

```sql
- domain_id (PK)
- organization_id (FK)
- domain                  -- "acme.com"
- is_verified             -- Domain ownership verified
- is_primary              -- Primary domain for display
```

**Examples:**
- Acme Corp → ["acme.com", "acmecorp.com"]
- TechStart Inc → ["techstart.io"]

#### 3. **users**
Individual user accounts linked to organizations.

```sql
- user_id (PK)
- organization_id (FK)
- email (unique)
- password_hash           -- bcrypt hashed
- name
- role                    -- admin, analyst, viewer
- is_active
- email_verified
- last_login
- preferences (JSONB)     -- User settings
- created_at, updated_at
```

#### 4. **sessions**
Active authentication sessions (optional - can use JWT instead).

```sql
- session_id (PK)
- user_id (FK)
- organization_id (FK)
- token_hash
- expires_at
- ip_address, user_agent
```

#### 5. **audit_log**
Track all user actions for compliance and security.

```sql
- log_id (PK)
- organization_id (FK)
- user_id (FK)
- action                  -- 'login', 'query_executed', 'data_exported'
- resource_type, resource_id
- details (JSONB)
- ip_address
- created_at
```

### Financial Data Tables (Modified)

All existing financial tables now include `organization_id`:

```sql
- general_ledger + organization_id
- chart_of_accounts + organization_id
- territory + organization_id
```

## Authentication Flow

### 1. Sign Up / Invitation Flow

```
User enters email (e.g., sarah@acme.com)
    ↓
Extract domain → "acme.com"
    ↓
Check if domain exists in email_domains table
    ↓
  YES: Domain found                    NO: Domain not registered
    ↓                                      ↓
  Link user to that org             Reject or allow org creation
    ↓
  Create user account
    ↓
  Send verification email
```

### 2. Login Flow

```
User enters email + password
    ↓
Look up user by email
    ↓
Verify password hash (bcrypt)
    ↓
Load organization data
    ↓
Check if org is active
    ↓
Generate JWT token with:
  - user_id
  - organization_id
  - role
    ↓
Return token + user data
```

### 3. API Request Flow

```
Client sends request with JWT token
    ↓
Backend validates JWT
    ↓
Extract organization_id from token
    ↓
Inject organization_id into all queries
    ↓
Return data (only from user's org)
```

## Roles & Permissions

### Admin
- Full access to organization
- Can invite/remove users
- Can manage organization settings
- Can run any query
- Can export data
- Can view audit logs

### Analyst
- Can run queries
- Can view dashboards
- Can export reports
- Cannot manage users
- Cannot change settings

### Viewer
- Read-only access
- Can view dashboards
- Can view saved reports
- Cannot run custom queries
- Cannot export data

## Data Isolation

### Application-Level Enforcement

All queries must include organization_id filter:

```python
# ❌ BAD - No org filter
SELECT * FROM general_ledger WHERE account_key = 'A001'

# ✅ GOOD - Filtered by org
SELECT * FROM general_ledger
WHERE organization_id = :org_id AND account_key = 'A001'
```

### Middleware Implementation

```python
# FastAPI middleware example
@app.middleware("http")
async def inject_organization_context(request: Request, call_next):
    # Extract org_id from JWT token
    token = request.headers.get("Authorization")
    org_id = decode_token(token).get("organization_id")

    # Inject into request state
    request.state.organization_id = org_id

    response = await call_next(request)
    return response
```

### Service Layer Pattern

```python
class QueryService:
    def execute_sql(self, sql: str, org_id: int):
        # Validate SQL
        self.validate_sql(sql)

        # Create a view or CTE that filters by org
        wrapped_sql = f"""
        WITH org_data AS (
            SELECT * FROM general_ledger WHERE organization_id = {org_id}
        )
        {sql}  -- User's SQL runs against org_data
        """

        return self.db.execute(wrapped_sql)
```

## Security Considerations

### 1. Password Security
- Use bcrypt with salt (minimum cost factor 12)
- Never store plain text passwords
- Implement password complexity requirements

### 2. Email Verification
- Require email verification before full access
- Send verification links that expire

### 3. Domain Verification
- Verify organization owns the domain (DNS TXT record)
- Prevent unauthorized domain registration

### 4. Rate Limiting
- Limit login attempts (5 attempts per 15 minutes)
- Implement API rate limiting per organization

### 5. Audit Logging
- Log all authentication events
- Log all data access (queries, exports)
- Track failed login attempts

### 6. Session Management
- Use secure JWT tokens
- Short expiration times (1 hour)
- Refresh token mechanism
- Ability to revoke sessions

## Implementation Checklist

### Phase 1: Database Setup
- [x] Create schema_users.sql
- [ ] Run SQL script on PostgreSQL
- [ ] Verify tables created
- [ ] Run seed data

### Phase 2: Backend Authentication
- [ ] Install bcrypt, PyJWT dependencies
- [ ] Create AuthService (register, login, verify)
- [ ] Create JWT token generation/validation
- [ ] Add authentication middleware
- [ ] Update all services to filter by org_id

### Phase 3: Frontend Updates
- [ ] Update login form to use real API
- [ ] Store JWT token in localStorage
- [ ] Add token to all API requests
- [ ] Handle token expiration/refresh
- [ ] Update AuthContext to use real auth

### Phase 4: User Management UI
- [ ] Invite users page (admin only)
- [ ] User list/management
- [ ] Role assignment
- [ ] Password reset flow

## Sample Data

The schema includes two sample organizations:

### Acme Corp (Enterprise)
- **Domains:** acme.com, acmecorp.com
- **Users:**
  - sarah.chen@acme.com (Admin)
  - mike.rodriguez@acme.com (Analyst)
- **Data:** All existing financial data

### TechStart Inc (Professional)
- **Domains:** techstart.io
- **Users:**
  - john.smith@techstart.io (Admin)
- **Data:** None yet (empty database)

**Test Credentials:**
- Email: sarah.chen@acme.com
- Password: password123

## API Endpoints

### Authentication

```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
POST /api/auth/verify-email
POST /api/auth/reset-password
GET  /api/auth/me
```

### User Management (Admin only)

```
GET    /api/users                    # List org users
POST   /api/users/invite             # Invite new user
DELETE /api/users/:id                # Remove user
PATCH  /api/users/:id/role           # Change role
```

### Organizations

```
GET   /api/organization              # Current org info
PATCH /api/organization              # Update settings
GET   /api/organization/audit-log    # View audit log
```

## Environment Variables

```env
# Authentication
JWT_SECRET=your-secret-key-here
JWT_EXPIRATION=3600  # 1 hour
BCRYPT_ROUNDS=12

# Email (for verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@finq.com
SMTP_PASSWORD=your-smtp-password
```

## Testing Strategy

### Unit Tests
- Password hashing/verification
- JWT token generation/validation
- Email domain extraction
- Role permission checks

### Integration Tests
- Full registration flow
- Login with valid/invalid credentials
- Data isolation (can't access other org's data)
- Role-based access control

### Security Tests
- SQL injection attempts
- XSS attacks
- CSRF protection
- Rate limiting

## Migration Path

### From Mock Auth to Real Auth

1. **Backend First:**
   - Implement AuthService
   - Add authentication endpoints
   - Keep mock auth working alongside

2. **Frontend Gradually:**
   - Update AuthContext to support both mock and real
   - Test with real backend
   - Remove mock auth once stable

3. **Data Migration:**
   - Existing data already linked to "Acme Corp"
   - Create new orgs as needed
   - Import their financial data separately

## Future Enhancements

- [ ] SSO integration (Google, Microsoft)
- [ ] Multi-factor authentication (MFA)
- [ ] API keys for programmatic access
- [ ] Granular permissions (beyond 3 roles)
- [ ] Team/department sub-organization
- [ ] White-label customization per org
- [ ] Usage analytics and billing integration
