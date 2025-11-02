# CI/CD Pipeline Documentation

## Overview
PulseOps AI uses GitHub Actions for continuous integration and deployment. The pipeline includes automated testing, security scanning, and deployment to AWS environments.

## Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**

#### Test Jobs
- **test-api**: Tests API service with pytest
- **test-ml**: Tests ML service with pytest
- **test-ui**: Tests React UI with Jest

#### Security Scanning
- **security-scan**: Runs Trivy vulnerability scanner

#### Deployment Jobs
- **deploy-dev**: Deploys to development on push to `develop`
- **deploy-prod**: Deploys to production on push to `main` (requires approval)
- **deploy-manual**: Manual deployment to any environment

**Deployment Flow:**
```
develop branch → test-api, test-ml, test-ui → deploy-dev → AWS Dev
main branch    → tests + security-scan → deploy-prod → AWS Prod (with approval)
```

### 2. Pull Request Checks (`pr-checks.yml`)

**Triggers:**
- Pull requests to `main` or `develop`

**Jobs:**
- **code-quality**: Runs linters (flake8, black, isort, ESLint)
- **dependency-scan**: Scans dependencies with Snyk
- **secrets-scan**: Scans for leaked secrets with TruffleHog
- **validate-infrastructure**: Validates CloudFormation templates
- **pr-size-check**: Analyzes PR size and provides feedback
- **pr-labeler**: Auto-labels PRs based on changed files

### 3. Scheduled Tasks (`scheduled-tasks.yml`)

**Triggers:**
- Weekly (Monday 9 AM UTC): Dependency updates
- Daily (2 AM UTC): Security audits and cleanup
- Manual workflow dispatch

**Jobs:**
- **dependency-updates**: Checks for outdated dependencies
- **security-audit**: Runs daily security audits
- **cleanup-old-deployments**: Cleans up old Lambda versions and logs

## GitHub Secrets Required

Add these secrets to your GitHub repository settings:

### AWS Credentials
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

### Environment-Specific Secrets

**Development:**
- `DEV_DB_USERNAME`: RDS username for dev
- `DEV_DB_PASSWORD`: RDS password for dev
- `DEV_JWT_SECRET`: JWT secret key for dev

**Production:**
- `PROD_DB_USERNAME`: RDS username for prod
- `PROD_DB_PASSWORD`: RDS password for prod
- `PROD_JWT_SECRET`: JWT secret key for prod

### Optional (for enhanced security scanning)
- `SNYK_TOKEN`: Snyk API token for dependency scanning
- `CODECOV_TOKEN`: Codecov token for coverage reports

## GitHub Environments

Configure these environments in GitHub repository settings:

### Development Environment
- **Protection rules**: None (auto-deploy)
- **Secrets**: DEV_* secrets
- **Reviewers**: Optional

### Production Environment
- **Protection rules**: Required reviewers
- **Secrets**: PROD_* secrets
- **Reviewers**: Team leads/DevOps
- **Branch protection**: Deploy from `main` only

## Setting Up CI/CD

### 1. Configure AWS Credentials

```bash
# Create an IAM user for GitHub Actions
aws iam create-user --user-name github-actions-pulseops

# Attach necessary policies
aws iam attach-user-policy \
  --user-name github-actions-pulseops \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create access keys
aws iam create-access-key --user-name github-actions-pulseops
```

**Best Practice:** Use OIDC instead of access keys for GitHub Actions:
```yaml
permissions:
  id-token: write
  contents: read

- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole
    aws-region: us-east-1
```

### 2. Add Secrets to GitHub

1. Go to repository **Settings → Secrets and variables → Actions**
2. Add **New repository secret** for each required secret
3. Ensure secrets are available to workflows

### 3. Set Up Environments

1. Go to **Settings → Environments**
2. Create `development` environment
3. Create `production` environment
4. Add protection rules for production:
   - Required reviewers: 1-2 people
   - Wait timer: 5 minutes (optional)
   - Deployment branches: `main` only

### 4. Enable Workflows

1. Go to **Actions** tab
2. Enable workflows if disabled
3. Review workflow permissions

## Workflow Triggers

### Automatic Triggers

**On Push:**
- Push to `develop` → Run tests → Deploy to dev
- Push to `main` → Run tests + security → Deploy to prod (with approval)

**On Pull Request:**
- Run all tests
- Code quality checks
- Security scans
- No deployment

**Scheduled:**
- Monday 9 AM UTC: Check dependency updates
- Daily 2 AM UTC: Security audits and cleanup

### Manual Triggers

**Deploy to Specific Environment:**
1. Go to **Actions** tab
2. Select **CI/CD Pipeline** workflow
3. Click **Run workflow**
4. Choose environment (dev/staging/prod)
5. Click **Run workflow**

## Monitoring Deployments

### View Workflow Status

1. Go to **Actions** tab
2. Select workflow run
3. View job logs and outputs

### Deployment URLs

After successful deployment, URLs are available in:
- Workflow outputs
- PR comments (for PR deployments)
- GitHub releases (for prod)

### CloudWatch Logs

```bash
# View API Lambda logs
aws logs tail /aws/lambda/pulseops-dev-ApiFunction --follow

# View ML Lambda logs
aws logs tail /aws/lambda/pulseops-dev-MLFunction --follow
```

## Rollback Procedures

### Automatic Rollback

The pipeline doesn't currently have automatic rollback. If tests fail, deployment stops.

### Manual Rollback

**Option 1: Revert Git Commit**
```bash
git revert HEAD
git push origin main
# Triggers new deployment with reverted code
```

**Option 2: Redeploy Previous Version**
```bash
# Checkout previous commit
git checkout <previous-commit-hash>

# Deploy manually
cd infrastructure
python deploy.py --environment prod
```

**Option 3: CloudFormation Stack Update**
```bash
# Cancel current update
aws cloudformation cancel-update-stack --stack-name pulseops-prod

# Or update to previous template
aws cloudformation update-stack \
  --stack-name pulseops-prod \
  --template-body file://previous-template.yaml
```

## Troubleshooting

### Build Failures

**Python Tests Fail:**
```bash
# Run locally to debug
cd services/api
pytest -v
```

**UI Tests Fail:**
```bash
# Run locally
cd services/ui
npm test
```

### Deployment Failures

**SAM Deploy Fails:**
- Check CloudFormation events in AWS Console
- Verify IAM permissions
- Check CloudWatch logs

**Lambda Function Errors:**
- View Lambda logs in CloudWatch
- Check environment variables
- Verify VPC/security group configuration

### Secret Issues

**Missing Secrets:**
- Verify secrets are added in GitHub
- Check secret names match workflow file
- Ensure environment has access to secrets

## Best Practices

### 1. Branch Strategy

- `main`: Production-ready code
- `develop`: Development integration
- `feature/*`: Feature branches
- `hotfix/*`: Emergency fixes

### 2. Commit Messages

Follow conventional commits:
```
feat(api): add new endpoint for analytics
fix(ui): resolve dashboard rendering issue
docs: update deployment documentation
chore(deps): update dependencies
```

### 3. Testing Before Push

```bash
# Run tests locally
cd services/api && pytest
cd services/ml && pytest
cd services/ui && npm test

# Run linters
flake8 services/api services/ml
cd services/ui && npm run lint
```

### 4. Security

- Never commit secrets
- Rotate AWS credentials regularly
- Review dependency updates
- Monitor security scan results

## Continuous Improvement

### Metrics to Monitor

- Build success rate
- Test coverage
- Deployment frequency
- Mean time to recovery (MTTR)
- Failed deployment rate

### Optimizations

1. **Cache Dependencies:**
   - Python packages cached
   - npm packages cached
   - Docker layers cached

2. **Parallel Jobs:**
   - Tests run in parallel
   - Independent builds run concurrently

3. **Incremental Deployments:**
   - Only changed services deployed
   - CloudFormation change sets

## Support

For CI/CD issues:
1. Check workflow logs
2. Review this documentation
3. Check GitHub Actions status page
4. Contact DevOps team
