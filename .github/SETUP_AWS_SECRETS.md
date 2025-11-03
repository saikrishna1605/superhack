# AWS Credentials Setup for GitHub Actions

## Quick Setup

To resolve the "Credentials could not be loaded" error, you need to add AWS credentials to GitHub Secrets.

### Step 1: Create AWS IAM User (if you don't have one)

```bash
# Create IAM user for GitHub Actions
aws iam create-user --user-name github-actions-pulseops

# Create access policy (minimum required permissions)
# Attach policies for:
# - CloudFormation (read/write)
# - Lambda (read/write)
# - S3 (read/write)
# - IAM (for creating roles)
# - API Gateway (read/write)
# - CloudFront (read/write)

# Create access keys
aws iam create-access-key --user-name github-actions-pulseops
```

**Output will contain:**
- `AccessKeyId` - This is your `AWS_ACCESS_KEY_ID`
- `SecretAccessKey` - This is your `AWS_SECRET_ACCESS_KEY`

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

#### Required Secrets:
- **Name:** `AWS_ACCESS_KEY_ID`
  - **Value:** Your AWS Access Key ID from Step 1
  
- **Name:** `AWS_SECRET_ACCESS_KEY`
  - **Value:** Your AWS Secret Access Key from Step 1

#### Environment-Specific Secrets (for deployment):

**Development Environment:**
- `DEV_DB_USERNAME` - Database username for dev environment
- `DEV_DB_PASSWORD` - Database password for dev environment  
- `DEV_JWT_SECRET` - JWT secret key for dev environment

**Production Environment:**
- `PROD_DB_USERNAME` - Database username for prod environment
- `PROD_DB_PASSWORD` - Database password for prod environment
- `PROD_JWT_SECRET` - JWT secret key for prod environment

### Step 3: Verify Secrets Are Set

After adding secrets, they will appear in the secrets list (values are hidden for security).

### Step 4: Test Deployment

Once secrets are configured:
1. Push to the `develop` branch to trigger dev deployment
2. Push to the `main` branch to trigger prod deployment (requires approval)

## Troubleshooting

### "Credentials could not be loaded"
- Verify secret names match exactly: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Check that secrets are added under **Repository secrets** (not Environment secrets)
- Ensure secrets are not empty

### "Access Denied" Errors
- Verify IAM user has required permissions
- Check IAM user policies include:
  - CloudFormation permissions
  - Lambda permissions
  - S3 permissions
  - IAM permissions (for role creation)

### Secrets Not Found in Environment
- Verify secrets are in **Repository secrets**, not **Environment secrets**
- For environment-specific secrets, add them under the respective environment in **Environments** section

## Security Best Practices

1. **Use IAM Roles Instead of Keys (Recommended)**
   - Set up OIDC provider for GitHub Actions
   - Use IAM roles instead of access keys
   - More secure and doesn't require storing credentials

2. **Rotate Credentials Regularly**
   - Rotate access keys every 90 days
   - Update GitHub secrets when rotating

3. **Limit Permissions**
   - Grant minimum required permissions to IAM user
   - Use separate IAM users for dev/prod if needed

## Need Help?

See `.github/CI_CD_GUIDE.md` for detailed CI/CD setup instructions.

