# Push your changes to the `komal` branch

Repo: **https://github.com/neeti-kurulkar/be-project-text-to-sql**

---

## Option A: Run these commands in order (recommended)

Open **PowerShell** or **Terminal**, then:

### 1. Go to the project folder
```powershell
cd "c:\Users\ASUS\Downloads\final_year_project\be-project-text-to-sql"
```

### 2. Create and switch to the new branch `komal`
```powershell
git checkout -b komal
```

### 3. Stage all changes (modified + new files)
```powershell
git add -A
```

### 4. Commit with a message
```powershell
git commit -m "Komal: dashboard UI, NumberTicker, insights, CI/CD doc, komal_db_egs"
```

### 5. Push the `komal` branch to GitHub
```powershell
git push -u origin komal
```

- **First time:** GitHub may ask you to sign in (browser or credential manager).
- If you use **2FA**, use a **Personal Access Token** as the password instead of your GitHub password.

---

## Option B: If you get "permission denied" or "403"

You need **write access** to `neeti-kurulkar/be-project-text-to-sql`.

- If it’s **your repo** or you’re a **collaborator**, sign in with the account that has access.
- If it’s **someone else’s repo**, they must add you as a collaborator, or you:
  1. **Fork** the repo to your GitHub account.
  2. Add your fork as a remote:  
     `git remote add myfork https://github.com/YOUR_USERNAME/be-project-text-to-sql.git`
  3. Push to your fork:  
     `git push -u myfork komal`
  4. Open a **Pull Request** from your fork’s `komal` branch to `neeti-kurulkar/be-project-text-to-sql` `main` (or `komal`).

---

## After a successful push

- Branch on GitHub: **https://github.com/neeti-kurulkar/be-project-text-to-sql/tree/komal**
- To open a Pull Request: GitHub repo → **Branches** → **komal** → **Compare & pull request**.

---

## Quick copy-paste (all steps)

```powershell
cd "c:\Users\ASUS\Downloads\final_year_project\be-project-text-to-sql"
git checkout -b komal
git add -A
git commit -m "Komal: dashboard UI, NumberTicker, insights, CI/CD doc, komal_db_egs"
git push -u origin komal
```
