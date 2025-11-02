# PulseOps AI - AWS Deployment Guide

## Prerequisites

### Required Tools
1. **AWS CLI** - Version 2.x or higher
   ```bash
   aws --version
   ```
   Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

2. **AWS SAM CLI** - Version 1.x or higher
   ```bash
   sam --version
   ```
   Install: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

3. **Python** - Version 3.11 or higher
   ```bash
   python --version
   ```

4. **Node.js/NPM** - Version 18.x or higher
   ```bash
   node --version
   npm --version
   ```

### AWS Account Setup

1. **Configure AWS Credentials**
   ```bash
   aws configure
   ```
   Provide:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., us-east-1)
   - Output format (json)

2. **Verify Access**
   ```bash
   aws sts get-caller-identity
   ```

3. **Required IAM Permissions**
   Your AWS user/role needs permissions for:
   - CloudFormation (create/update/delete stacks)
   - Lambda (create/update functions)
   - API Gateway (create/manage APIs)
   - S3 (create/manage buckets)
   - RDS (create/manage databases)
   - DynamoDB (create/manage tables)
   - CloudFront (create distributions)
   - IAM (create/manage roles and policies)
   - VPC (create/manage network resources)
   - CloudWatch (create logs and alarms)

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

Use the automated deployment script:

```bash
# Deploy to development environment
cd infrastructure
python deploy.py --environment dev --region us-east-1

# Deploy to production environment
python deploy.py --environment prod --region us-east-1
```

The script will:
1. ✅ Check prerequisites
2. ✅ Validate AWS credentials
3. ✅ Build API service (Lambda package)
4. ✅ Build ML service (Lambda package)
5. ✅ Build React UI
6. ✅ Run SAM build
7. ✅ Deploy infrastructure via CloudFormation
8. ✅ Sync UI to S3
9. ✅ Display stack outputs

### Method 2: Manual Step-by-Step Deployment

#### Step 1: Build Services

```bash
# Build API Lambda
cd services/api
pip install -r requirements.txt -t package
cd ../..

# Build ML Lambda
cd services/ml
pip install -r requirements.txt -t package
cd ../..

# Build React UI
cd services/ui
npm install
npm run build
cd ../..
```

#### Step 2: SAM Build

```bash
cd infrastructure
sam build --template-file sam-template.yaml --use-container
```

#### Step 3: SAM Deploy

```bash
# Development
sam deploy \
  --template-file sam-template.yaml \
  --stack-name pulseops-dev \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Environment=dev \
    DBUsername=pulseops_admin \
    DBPassword=YourSecurePassword123! \
    JWTSecretKey=YourSecureJWTKey123!

# Production
sam deploy \
  --template-file sam-template.yaml \
  --stack-name pulseops-prod \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Environment=prod \
    DBUsername=pulseops_admin \
    DBPassword=YourSecurePassword123! \
    JWTSecretKey=YourSecureJWTKey123!
```

#### Step 4: Deploy UI to S3

```bash
# Get S3 bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name pulseops-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UIBucketName`].OutputValue' \
  --output text)

# Sync UI build
aws s3 sync services/ui/build s3://$BUCKET_NAME --delete
```

## Configuration

### Environment Variables

Update `.env` files after deployment:

**services/api/.env**
```env
DATABASE_URL=postgresql://username:password@<RDS_ENDPOINT>/pulseops
JWT_SECRET_KEY=<from-deployment>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**services/ui/.env.production**
```env
REACT_APP_API_URL=<API_GATEWAY_URL>
REACT_APP_ML_API_URL=<ML_API_URL>
```

### Secrets Management

**⚠️ IMPORTANT: Never commit secrets to Git!**

For production, use AWS Secrets Manager or Parameter Store:

```bash
# Store database password
aws secretsmanager create-secret \
  --name pulseops/prod/db-password \
  --secret-string "YourSecurePassword123!"

# Store JWT secret
aws secretsmanager create-secret \
  --name pulseops/prod/jwt-secret \
  --secret-string "YourSecureJWTKey123!"
```

Update `sam-template.yaml` to reference secrets:
```yaml
Environment:
  Variables:
    DB_PASSWORD: '{{resolve:secretsmanager:pulseops/prod/db-password}}'
    JWT_SECRET: '{{resolve:secretsmanager:pulseops/prod/jwt-secret}}'
```

## Post-Deployment Steps

### 1. Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name pulseops-dev \
  --query 'Stacks[0].Outputs'
```

Important outputs:
- `ApiUrl` - API Gateway endpoint
- `MLApiUrl` - ML service endpoint
- `UIUrl` - CloudFront URL for UI
- `DatabaseEndpoint` - RDS endpoint
- `UIBucketName` - S3 bucket for UI

### 2. Initialize Database

```bash
# Connect to RDS via bastion or VPN
psql -h <RDS_ENDPOINT> -U pulseops_admin -d pulseops

# Run migrations (using Alembic)
cd services/api
alembic upgrade head

# Or use seed script
python seed_data.py
```

### 3. Update UI Configuration

Edit `services/ui/.env.production`:
```env
REACT_APP_API_URL=https://xyz123.execute-api.us-east-1.amazonaws.com/Prod
```

Rebuild and redeploy UI:
```bash
cd services/ui
npm run build
aws s3 sync build s3://<UI_BUCKET_NAME> --delete
```

### 4. Invalidate CloudFront Cache

```bash
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name pulseops-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text)

aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"
```

### 5. Test Deployment

```bash
# Test API health
curl https://<API_URL>/health

# Test ML API
curl https://<ML_API_URL>/health

# Access UI
open https://<CLOUDFRONT_URL>
```

## Monitoring & Troubleshooting

### View Logs

```bash
# API Lambda logs
sam logs --stack-name pulseops-dev --name ApiFunction --tail

# ML Lambda logs
sam logs --stack-name pulseops-dev --name MLFunction --tail

# CloudWatch Logs
aws logs tail /aws/lambda/pulseops-dev-ApiFunction --follow
```

### CloudWatch Metrics

Navigate to CloudWatch console:
- Lambda invocations and errors
- API Gateway requests and latency
- RDS connections and CPU
- DynamoDB read/write capacity

### Common Issues

#### 1. Lambda Cold Start Timeout
- **Symptom**: First API request takes >30 seconds
- **Solution**: Increase Lambda timeout or use provisioned concurrency

#### 2. Database Connection Errors
- **Symptom**: "Connection refused" from Lambda
- **Solution**: Verify security groups allow Lambda access to RDS

#### 3. CORS Errors in UI
- **Symptom**: API calls blocked by browser
- **Solution**: Update API Gateway CORS configuration

#### 4. CloudFront Cache Issues
- **Symptom**: Old UI version still showing
- **Solution**: Create CloudFront invalidation (see above)

## Updating Deployment

### Update Infrastructure

```bash
# Make changes to sam-template.yaml
# Then redeploy
sam build --template-file sam-template.yaml
sam deploy --stack-name pulseops-dev
```

### Update Lambda Functions

```bash
# Rebuild and deploy
cd infrastructure
sam build
sam deploy --stack-name pulseops-dev
```

### Update UI Only

```bash
cd services/ui
npm run build
aws s3 sync build s3://<UI_BUCKET_NAME> --delete
aws cloudfront create-invalidation --distribution-id <DIST_ID> --paths "/*"
```

## Cleanup / Teardown

To delete all AWS resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name pulseops-dev

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name pulseops-dev

# Manually delete S3 buckets (they may be retained)
aws s3 rb s3://<UI_BUCKET_NAME> --force
aws s3 rb s3://<DATA_BUCKET_NAME> --force
```

## Cost Estimation

### Development Environment (~$50-100/month)
- RDS db.t3.micro: ~$15/month
- Lambda: ~$5/month (minimal usage)
- S3: ~$1/month
- CloudFront: ~$1/month
- DynamoDB: ~$1/month (on-demand)
- API Gateway: ~$3.50/month
- Data Transfer: ~$5-10/month

### Production Environment (~$200-500/month)
- RDS db.t3.small Multi-AZ: ~$70/month
- Lambda: ~$20-50/month
- S3: ~$5/month
- CloudFront: ~$10-20/month
- DynamoDB: ~$10-50/month
- API Gateway: ~$10-20/month
- Data Transfer: ~$20-50/month

**💡 Tip**: Use AWS Cost Explorer and set up billing alarms!

## Security Best Practices

1. ✅ **Use Secrets Manager** for sensitive data
2. ✅ **Enable CloudTrail** for audit logging
3. ✅ **Implement WAF** on CloudFront/API Gateway
4. ✅ **Use VPC** for database isolation
5. ✅ **Enable encryption** at rest and in transit
6. ✅ **Implement least privilege** IAM policies
7. ✅ **Regular security patches** for dependencies
8. ✅ **Enable MFA** on AWS accounts
9. ✅ **Use custom domain** with SSL/TLS
10. ✅ **Implement rate limiting** on API Gateway

## Support

For issues or questions:
- Check CloudWatch Logs for errors
- Review CloudFormation events for deployment issues
- Consult AWS documentation for service-specific help
