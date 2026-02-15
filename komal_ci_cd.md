# MEMBER 4: CI/CD Pipeline, Cost Estimation, and Project Setup

================================================================================

## WHAT THIS IS ABOUT

CI/CD stands for **Continuous Integration / Continuous Deployment**. It means: every time we push code to GitHub, it automatically builds and deploys to Azure — no manual steps needed. You'll also be responsible for figuring out the overall Azure account setup and total cost.

================================================================================

---

## 1. Azure for Students

### Overview
- We're students, so we get **free Azure credits**.
- Sign-up URL: **https://azure.microsoft.com/en-us/free/students/**
- Use your **college email** (e.g. @university.edu) for verification.

### Signup process (document with screenshots)

1. **Go to** https://azure.microsoft.com/en-us/free/students/
2. **Click** "Start free" or "Sign up".
3. **Sign in** with your Microsoft account (or create one using your college email).
4. **Verify student status** — you may need to:
   - Enter your school name and select it from the list, OR
   - Upload student ID / use a verified college email domain.
5. **Accept** the Azure for Students terms.
6. **Complete identity verification** (phone or card for $0 verification — no charge).
7. **Credits are applied** to your account; you can use them within the validity period.

### What you get (typical)

| Item | Details |
|------|--------|
| **Free credit** | **$100** (USD) for 12 months (no credit card required for signup in many regions; some regions may require card for verification only). |
| **Duration** | 12 months from activation. |
| **Services** | Access to a large set of Azure services (excluding some enterprise-only ones). Includes App Service, Static Web Apps, PostgreSQL (Flexible Server or managed DB), Key Vault, etc. |
| **After expiry** | Account becomes pay-as-you-go; you can choose to add a card or stop using paid resources. |

### Can multiple team members sign up separately?
- **Yes.** Each student can sign up with their own college email and get their own $100 credit.
- **Recommendation:** Use one shared Azure account (one team member’s student account) for the project so all resources and CI/CD live in one place. Other members can be added as **Guest users** in Azure AD if needed.
- If you use one account, document who owns it and ensure credentials (e.g. for GitHub Actions) are stored only in GitHub Secrets, not shared in chat or email.

### What to deliver
- **Azure for Students signup guide** with step-by-step instructions and **screenshots** (add screenshots in the same folder or in a `screenshots/` subfolder and reference them here).

---

## 2. Azure Resource Organization

### Resource Group
- In Azure, **everything lives inside a Resource Group** (think of it as a folder for a project).
- One Resource Group per project/environment (e.g. one for FinQ).

### How to create a Resource Group

1. In **Azure Portal** (https://portal.azure.com): search for **Resource groups**.
2. Click **+ Create**.
3. **Subscription:** Select your subscription (e.g. Azure for Students).
4. **Resource group:** Enter name (see naming below).
5. **Region:** Choose one region and **use the same for all resources** (e.g. **Central India** or **South India**).
6. Click **Review + create** → **Create**.

### Naming conventions (recommended for FinQ)

| Resource type | Example name | Notes |
|---------------|--------------|--------|
| Resource Group | `finq-rg` or `finq-prod-rg` | Holds all FinQ resources. |
| App Service (backend) | `finq-backend` or `finq-api` | Must be globally unique (e.g. finq-backend-&lt;your-id&gt;). |
| Static Web App (frontend) | `finq-frontend` or `finq-web` | Auto-generated URL. |
| PostgreSQL / Database | `finq-db` or `finq-psql` | If using Azure Database for PostgreSQL. |
| Key Vault | `finq-kv` or `finq-secrets` | Key Vault names must be globally unique. |

**Rules:**
- Lowercase, numbers, hyphens only (no spaces).
- Keep names short and consistent (e.g. prefix `finq-`).

### Region selection
- **Central India** or **South India** — use the **same region** for Resource Group, App Service, Static Web Apps, and database to reduce latency and avoid cross-region data transfer costs.
- Document the chosen region in this file (e.g. "We use **Central India** for all resources.").

### What to deliver
- **Resource Group setup instructions** (step-by-step, with the chosen region and naming convention).

---

## 3. GitHub Actions for Automated Deployment

### Overview
- **GitHub Actions** is a free CI/CD service built into GitHub.
- We use it to:
  - **Backend:** On push to `main`, build and deploy the `backend/` folder to **Azure App Service**.
  - **Frontend:** On push to `main`, build and deploy the `frontend/` folder to **Azure Static Web Apps**.

### Frontend: Azure Static Web Apps
- Azure Static Web Apps **can create a GitHub Actions workflow automatically** when you create the resource in the Azure Portal and connect your GitHub repo.
- Steps:
  1. In Azure Portal: create a **Static Web App** (resource type: Static Web App).
  2. Connect **GitHub** → choose org/repo and branch (e.g. `main`).
  3. **Build details:** App location: `/frontend` or root if frontend is at repo root; output location: e.g. `build` (Vite) or `dist`.
  4. Azure generates a workflow file (e.g. `.github/workflows/azure-static-web-apps-xxx.yml`) and adds it to your repo. You can edit it later if needed.

### Backend: Azure App Service
- Use **App Service Deployment Center** to connect GitHub to the App Service:
  1. Create an **App Service** (e.g. Web App, Linux, Python or Node runtime as per your backend).
  2. In the App Service → **Deployment Center** → Source: **GitHub** → authorize and select repo + branch.
  3. Azure can generate a **GitHub Actions workflow** that builds and deploys on push to `main`.
- Alternatively, write the workflow manually (see template below).

### Manual workflow structure (backend)

Create (or adapt) a file: **`.github/workflows/deploy-backend.yml`**

```yaml
name: Deploy Backend to Azure App Service

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
  workflow_dispatch:

env:
  AZURE_WEBAPP_NAME: finq-backend    # or your App Service name

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python (or Node, as per your stack)
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: ./backend
```

- **Secrets:** Store `AZURE_WEBAPP_PUBLISH_PROFILE` in GitHub Secrets (see Section 4).

### Frontend workflow (if not auto-generated)

If you prefer a single workflow that deploys both:

- **Backend:** Trigger on `backend/**` changes; deploy to App Service.
- **Frontend:** Trigger on `frontend/**` changes; build (e.g. `npm run build`) and deploy to Static Web Apps (using `Azure/static-web-apps-deploy` action with `app_location: frontend`, `output_location: dist` or `build`).

### What to deliver
- **GitHub Actions workflow file(s)** — at least the **structure/template** (e.g. `.github/workflows/deploy-backend.yml` and, if not auto-created, a frontend deploy workflow).
- Short note on how **Azure Static Web Apps** auto-creates a workflow and how **Deployment Center** works for the backend.

---

## 4. Secrets Management in GitHub Actions

### Why secrets?
- The CI/CD pipeline needs **credentials** to deploy to Azure (e.g. publish profile or service principal). These must **not** be committed to the repo.

### GitHub Secrets
- **Repository** → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
- Secrets are available in workflows as `${{ secrets.SECRET_NAME }}`.

### Credentials needed

| Method | What you need | Use case |
|--------|----------------|----------|
| **Publish profile** | Download from App Service → **Get publish profile** | Simple deploy for App Service (backend). |
| **Service principal** | App registration + client secret; contributor role on Resource Group | More flexible; good for multiple resources or Static Web Apps (when not using auto-generated workflow). |

### Step-by-step: Publish profile (backend)

1. **Azure Portal** → your **App Service** (e.g. finq-backend).
2. Click **Get publish profile** (top bar) → download the `.PublishSettings` file.
3. Open the file in a text editor and **copy the entire contents**.
4. **GitHub** → repo → **Settings** → **Secrets and variables** → **Actions**.
5. **New repository secret** → Name: `AZURE_WEBAPP_PUBLISH_PROFILE` → Value: paste the contents → **Add secret**.

Your workflow then uses:
```yaml
publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

### Step-by-step: Static Web Apps (if using manual workflow)
- When you create the Static Web App in Azure and connect GitHub, Azure can add a secret like `AZURE_STATIC_WEB_APPS_API_TOKEN` automatically. If you create the workflow manually, you get this token from the Static Web App resource → **Manage deployment token** and add it as a repo secret.

### What to deliver
- **How to store and use deployment credentials**: short guide (with steps above) and a note on which secret names your workflows use.

---

## 5. Azure Key Vault (Bonus)

### What it is
- **Azure Key Vault** stores secrets (API keys, DB passwords, connection strings) securely. Applications (e.g. App Service) can **reference** Key Vault secrets instead of storing them in App Service configuration.

### Is it worth it for our project?
- **App Service application settings** are enough for a student project: you can store env vars (e.g. `DATABASE_URL`, `OPENAI_API_KEY`) in App Service → Configuration → Application settings. They are encrypted at rest.
- **Key Vault** is useful if:
  - You want a single place for secrets used by multiple apps.
  - You need audit logs for who accessed which secret.
  - You want rotation or stricter access policies.
- **Recommendation:** For FinQ, **App Service settings are sufficient**. Key Vault can be a "bonus" if you have time.

### If you set up Key Vault

1. Create a **Key Vault** (e.g. `finq-kv`) in the same Resource Group and region.
2. Add **secrets** (e.g. database connection string, API key).
3. In **App Service** → **Identity** → turn **On** System-assigned managed identity.
4. In **Key Vault** → **Access policies** → add access policy for the App Service’s managed identity (Secret Get).
5. In **App Service** → **Configuration** → add a setting with value like `@Microsoft.KeyVault(SecretUri=...)` to reference the secret.

### What to deliver
- One paragraph: **Is Key Vault worth it for us?** (Yes/No and why.)
- If yes: **How to create a Key Vault and connect it to App Service** (short steps as above).

---

## 6. Total Cost Estimation

### Goal
- **Combine** cost estimates from Members 1, 2, and 3.
- Show: each Azure service, pricing tier, monthly cost (INR and USD), what’s covered by free/student credits, when we’d start paying, and how long we can run on student credits.

### Template table (fill with actual numbers from your team)

| Azure service | Pricing tier | Monthly cost (USD) | Monthly cost (INR) | Covered by student credit? | When we pay |
|---------------|--------------|--------------------|--------------------|----------------------------|-------------|
| App Service (backend) | Free / B1 / etc. | $0 / $X | ₹0 / ₹X | Yes / No | After credit exhausted |
| Azure Static Web Apps | Free | $0 | ₹0 | Yes | N/A |
| PostgreSQL (if used) | Flexible / Burstable | $X | ₹X | Yes / No | … |
| Key Vault (if used) | Standard | $X | ₹X | Yes | … |
| **Total** | | **$X** | **₹X** | | |

(Add/remove rows to match your actual services.)

### Student credit duration
- **Total student credit:** $100 (one account) or $100 × number of accounts if you use multiple.
- **Estimated monthly burn:** Sum of monthly costs from the table (only services that consume the credit).
- **Months on free credit:** `$100 / estimated_monthly_burn` (e.g. if burn is $20/month → about 5 months).

### What to deliver
- **Complete cost breakdown table** (combining all members’ estimates).
- **Timeline:** How long can we run for free on student credits? (e.g. "We can run for approximately X months on $100 credit.")

---

## WHAT TO DELIVER (Checklist)

- [ ] **Azure for Students signup guide** (with screenshots).
- [ ] **Resource Group setup instructions** (region + naming).
- [ ] **GitHub Actions workflow file(s)** or structure/template for backend and frontend.
- [ ] **How to store and use deployment credentials** (GitHub Secrets + publish profile / token).
- [ ] **Complete cost breakdown table** (combining all members’ estimates).
- [ ] **Timeline:** How long can we run for free?

---

## References

- Azure for Students: https://azure.microsoft.com/en-us/free/students/
- Azure Resource Groups: https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal
- GitHub Actions for Azure: https://github.com/Azure/actions
- Azure Static Web Apps + GitHub: https://docs.microsoft.com/en-us/azure/static-web-apps/get-started-cli
- App Service Deployment Center: https://docs.microsoft.com/en-us/azure/app-service/deploy-github-actions

---

*Document for Member 4 — CI/CD, Cost Estimation, and Project Setup. Update with your actual screenshots, secret names, and cost figures from Members 1–3.*
