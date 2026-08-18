# CI/CD Setup Guide for Databricks Asset Bundles

## 🎯 Overview

This guide walks you through setting up automated deployments for your DAB project using GitHub Actions.

## 📋 Prerequisites

- GitHub repository for this project
- Databricks workspace access
- Admin permissions to create service principals (recommended) or ability to generate personal access tokens

---

## 🔐 Step 1: Create Databricks Access Token

### Option A: Service Principal (Recommended for Production)

1. **Create a Service Principal:**
   ```bash
   # In Databricks workspace, go to:
   # Settings > Identity and Access > Service Principals > Add Service Principal
   ```
   - Name it: `github-actions-cicd`
   - Note the Application ID

2. **Generate Token for Service Principal:**
   - Select the service principal
   - Go to "Tokens" tab
   - Click "Generate token"
   - Set lifetime (e.g., 90 days - set calendar reminder to rotate)
   - Copy and save the token securely

3. **Grant Permissions:**
   - Workspace access: "User" role minimum
   - Permissions on target folders/resources as needed

### Option B: Personal Access Token (Quick Start / Dev)

1. In Databricks workspace:
   - Click your profile icon → Settings
   - Developer → Access tokens
   - Generate new token
   - Set lifetime and description: "GitHub Actions"
   - Copy and save the token

⚠️ **Security Note:** Service principals are preferred for production as they:
- Don't expire when you leave the organization
- Can have restricted, audit-friendly permissions
- Aren't tied to a personal account

---

## 🔑 Step 2: Configure GitHub Secrets

1. **Navigate to your GitHub repository**

2. **Go to Settings > Secrets and variables > Actions**

3. **Add the following Repository Secrets:**

   | Secret Name | Value | Example |
   |------------|--------|--------|
   | `DATABRICKS_HOST` | Your workspace URL | `https://dbc-df56fd26-1a11.cloud.databricks.com` |
   | `DATABRICKS_TOKEN` | Token from Step 1 | `dapi...` |

4. **Click "New repository secret"** for each and paste the values

### 🛡️ Using Environment Secrets (Advanced)

For better security, use GitHub Environments:

1. **Settings > Environments > New environment**
   - Create `production` environment
   - Add protection rules:
     - ✅ Required reviewers (select team members)
     - ✅ Wait timer (e.g., 5 minutes)
   - Add environment-specific secrets here

2. The `deploy-prod.yml` workflow already uses `environment: production`

---

## 📁 Step 3: Commit and Push Workflow Files

The workflows are already created in `.github/workflows/`:

```bash
# From your local terminal in the project directory
git add .github/
git commit -m "Add GitHub Actions workflows for CI/CD"
git push origin feature/<your-branch>
```

---

## 🚀 Step 4: Test the Workflows

### Test PR Validation

1. **Create a test PR:**
   ```bash
   git checkout -b test-cicd
   # Make a small change (e.g., edit README)
   git add .
   git commit -m "Test: Trigger CI/CD validation"
   git push origin test-cicd
   ```

2. **Create PR to main** in GitHub

3. **Verify** the "Validate Pull Request" workflow runs:
   - Go to Actions tab
   - Should see ✅ green check if validation passes
   - PR will show the check status

### Test Production Deployment

1. **Merge the PR to main**

2. **Watch the deployment:**
   - Actions tab → "Deploy to Production" workflow
   - If using environment protection, approve the deployment
   - Verify successful deployment

3. **Verify in Databricks:**
   - Check your workspace for deployed resources
   - Look for resources with `prod` prefix

---

## 📊 Step 5: Recommended Deployment Improvements

### A. Add Deployment Status Notifications

Add Slack/Teams notifications to workflows:

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Deployment ${{ job.status }}: ${{ github.repository }}"
      }
```

### B. Add Deployment Tags

```yaml
- name: Tag Release
  if: success()
  run: |
    git tag -a "prod-$(date +%Y%m%d-%H%M%S)" -m "Production deployment"
    git push origin --tags
```

### C. Add Pre-deployment Tests

Expand the validation workflow:

```yaml
- name: Run Integration Tests
  run: |
    databricks bundle run --target dev test_job
```

### D. Implement GitFlow

```
main (production)
  ↑
develop (pre-prod)
  ↑
feature/* (dev)
```

Update workflow triggers:
- `main` → Deploy to production
- `develop` → Deploy to staging/pre-prod
- `feature/*` → Manual dev deployment only

---

## 🔍 Monitoring and Troubleshooting

### Common Issues

**1. "Authentication failed"**
- Verify `DATABRICKS_HOST` format (include `https://`, no trailing `/`)
- Check token hasn't expired
- Verify service principal has workspace access

**2. "Bundle validation failed"**
- Run locally: `databricks bundle validate --target prod`
- Check `databricks.yml` syntax
- Verify resource definitions in `resources/`

**3. "Permission denied"**
- Service principal needs permissions on:
  - Deployment folder (`/Workspace/PROD/.bundle/...`)
  - Target resources (clusters, jobs, etc.)

### Workflow Monitoring

- **GitHub Actions tab**: View all workflow runs
- **Databricks workspace**: Check deployed resources
- **Set up alerts**: GitHub can email on workflow failures

---

## ✅ Best Practices Checklist

- [ ] Use service principal for production deployments
- [ ] Rotate tokens every 90 days (set calendar reminder)
- [ ] Enable branch protection on `main`
- [ ] Require PR reviews before merge
- [ ] Use GitHub Environments for production with approvals
- [ ] Keep manual dev deployments for fast iteration
- [ ] Monitor workflow runs and deployment health
- [ ] Document your deployment process in README
- [ ] Test workflows in non-production first
- [ ] Add deployment notifications to team channels

---

## 🎓 Your Current Setup Summary

**Development:**
- ✅ Manual: `databricks bundle deploy --target dev`
- ⚠️ Optional: Auto-deploy on feature branch push (disabled by default)

**Production:**
- ✅ Automated: Triggers on merge to `main`
- ✅ Validation: Runs on every PR to `main`
- ✅ Manual trigger: Available via GitHub Actions UI

**Next Steps:**
1. Set up GitHub secrets (Step 2)
2. Push workflow files to your repo (Step 3)
3. Test with a PR (Step 4)
4. Celebrate! 🎉

---

## 📚 Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Databricks CLI Reference](https://docs.databricks.com/dev-tools/cli/)
- [Service Principal Best Practices](https://docs.databricks.com/administration-guide/users-groups/service-principals.html)

---

**Questions?** Check the [troubleshooting section](#monitoring-and-troubleshooting) or reach out to your team's Databricks admin.
