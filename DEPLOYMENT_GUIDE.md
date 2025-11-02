# PulseOps AWS Deployment Guide

## Overview
This guide walks you through deploying PulseOps to AWS using a serverless architecture.

**Architecture:**
- Frontend: React → S3 + CloudFront
- Backend: FastAPI → Lambda + API Gateway
- Database: SQLite → RDS PostgreSQL

**Estimated Time:** 45-60 minutes
**Estimated Cost:** ~$30-50/month (with Free Tier benefits)

---

## Prerequisites

### 1. AWS Account
- Create an AWS account at https://aws.amazon.com
- Have admin access or sufficient IAM permissions

### 2. Install Required Tools
```powershell
# AWS CLI
winget install Amazon.AWSCLI

# AWS SAM CLI (for serverless deployments)
winget install Amazon.SAM-CLI

# Node.js (for React build)
# Already installed - verify: node --version

# Python (for API)
# Already installed - verify: python --version
```

### 3. Configure AWS Credentials
```powershell
# Configure AWS CLI with your credentials
aws configure

# Enter when prompted:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region name: us-east-1  # or your preferred region
# Default output format: json
```

**To get AWS credentials:**
1. Go to AWS Console → IAM → Users
2. Create a new user with programmatic access
3. Attach policy: `AdministratorAccess` (for deployment)
4. Save the Access Key ID and Secret Access Key

### 4. Verify Setup
```powershell
# Test AWS connection
aws sts get-caller-identity

# Test SAM CLI
sam --version
```

---

## Step 1: Prepare Database Migration (SQLite → PostgreSQL)

### 1.1 Export Current Data
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\api
python -c "
import sqlite3
import json

conn = sqlite3.connect('pulseops.db')
cursor = conn.cursor()

# Export users
cursor.execute('SELECT * FROM users')
users = [{'id': r[0], 'email': r[1], 'role': r[2], 'hashed_password': r[3]} for r in cursor.fetchall()]

# Export licenses
cursor.execute('SELECT * FROM software_licenses')
licenses = [{'id': r[0], 'software_name': r[1], 'vendor': r[2], 'category': r[3], 
             'monthly_cost': r[4], 'annual_cost': r[5], 'total_licenses': r[6], 
             'active_users': r[7], 'utilization_percent': r[8]} for r in cursor.fetchall()]

with open('data_export.json', 'w') as f:
    json.dump({'users': users, 'licenses': licenses}, f, indent=2)

print('✅ Data exported to data_export.json')
conn.close()
"
```

### 1.2 Create RDS PostgreSQL Instance
We'll do this through AWS Console (easier) or CLI:

**Option A: AWS Console (Recommended)**
1. Go to AWS RDS Console
2. Click "Create database"
3. Choose "PostgreSQL"
4. Template: "Free tier" or "Dev/Test"
5. Settings:
   - DB instance identifier: `pulseops-db`
   - Master username: `pulseops_admin`
   - Master password: [Create strong password - SAVE IT!]
6. Instance configuration:
   - DB instance class: `db.t3.micro` (Free tier eligible)
7. Storage:
   - Allocated storage: 20 GB
   - Storage autoscaling: Enable
8. Connectivity:
   - Public access: Yes (for now, will secure later)
   - VPC security group: Create new
   - Security group name: `pulseops-db-sg`
9. Additional configuration:
   - Initial database name: `pulseops`
10. Click "Create database"
11. Wait 5-10 minutes for creation
12. **SAVE THE ENDPOINT URL** (e.g., `pulseops-db.xxxxx.us-east-1.rds.amazonaws.com`)

**Option B: AWS CLI**
```powershell
# Create RDS PostgreSQL (this will take 5-10 minutes)
aws rds create-db-instance `
  --db-instance-identifier pulseops-db `
  --db-instance-class db.t3.micro `
  --engine postgres `
  --engine-version 15.4 `
  --master-username pulseops_admin `
  --master-user-password "YourStrongPassword123!" `
  --allocated-storage 20 `
  --publicly-accessible `
  --db-name pulseops `
  --backup-retention-period 7

# Wait for instance to be available
aws rds wait db-instance-available --db-instance-identifier pulseops-db

# Get the endpoint
aws rds describe-db-instances --db-instance-identifier pulseops-db --query "DBInstances[0].Endpoint.Address"
```

---

## Step 2: Deploy Backend API to AWS Lambda

### 2.1 Create Lambda Deployment Package
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\api

# Create deployment directory
New-Item -ItemType Directory -Force -Path deploy

# Copy application files
Copy-Item -Path *.py -Destination deploy\
Copy-Item -Path routers -Destination deploy\routers -Recurse
Copy-Item -Path models -Destination deploy\models -Recurse
Copy-Item -Path requirements.txt -Destination deploy\

# Install dependencies
cd deploy
pip install -r requirements.txt -t . --upgrade

# Create ZIP file for Lambda
Compress-Archive -Path * -DestinationPath ..\pulseops-api.zip -Force

cd ..
Write-Host "✅ Lambda package created: pulseops-api.zip"
```

### 2.2 Create Lambda Function
```powershell
# Create IAM role for Lambda
aws iam create-role --role-name pulseops-lambda-role `
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach basic Lambda execution policy
aws iam attach-role-policy --role-name pulseops-lambda-role `
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Wait a few seconds for IAM propagation
Start-Sleep -Seconds 10

# Create Lambda function
aws lambda create-function --function-name pulseops-api `
  --runtime python3.11 `
  --role arn:aws:iam::{YOUR_ACCOUNT_ID}:role/pulseops-lambda-role `
  --handler main.handler `
  --zip-file fileb://pulseops-api.zip `
  --timeout 30 `
  --memory-size 512 `
  --environment Variables="{
    DATABASE_URL=postgresql://pulseops_admin:YourPassword@your-rds-endpoint:5432/pulseops,
    SECRET_KEY=your-secret-key-here-change-this
  }"

# Get your account ID
aws sts get-caller-identity --query Account --output text
```

### 2.3 Create API Gateway
```powershell
# Create REST API
$apiId = aws apigateway create-rest-api --name pulseops-api --query 'id' --output text

# Get root resource ID
$rootId = aws apigateway get-resources --rest-api-id $apiId --query 'items[0].id' --output text

# Create proxy resource
$proxyId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootId --path-part '{proxy+}' --query 'id' --output text

# Create ANY method
aws apigateway put-method --rest-api-id $apiId --resource-id $proxyId --http-method ANY --authorization-type NONE

# Integrate with Lambda
$accountId = aws sts get-caller-identity --query Account --output text
$lambdaArn = "arn:aws:lambda:us-east-1:$accountId:function:pulseops-api"

aws apigateway put-integration --rest-api-id $apiId --resource-id $proxyId --http-method ANY `
  --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$lambdaArn/invocations"

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission --function-name pulseops-api `
  --statement-id apigateway-invoke `
  --action lambda:InvokeFunction `
  --principal apigateway.amazonaws.com

# Deploy API
aws apigateway create-deployment --rest-api-id $apiId --stage-name prod

# Get API URL
Write-Host "✅ API deployed at: https://$apiId.execute-api.us-east-1.amazonaws.com/prod"
```

---

## Step 3: Deploy Frontend to S3 + CloudFront

### 3.1 Build React App
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\ui

# Update API endpoint in environment
$apiUrl = "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
Write-Output "REACT_APP_API_URL=$apiUrl" | Out-File -FilePath .env.production -Encoding utf8

# Build for production
npm run build

Write-Host "✅ React app built successfully"
```

### 3.2 Create S3 Bucket for Hosting
```powershell
# Create unique bucket name
$bucketName = "pulseops-ui-$(Get-Date -Format 'yyyyMMdd')"

# Create S3 bucket
aws s3 mb s3://$bucketName --region us-east-1

# Enable static website hosting
aws s3 website s3://$bucketName --index-document index.html --error-document index.html

# Upload build files
aws s3 sync build/ s3://$bucketName --delete

# Make bucket public (for website hosting)
aws s3api put-bucket-policy --bucket $bucketName --policy @"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$bucketName/*"
  }]
}
"@

Write-Host "✅ S3 bucket created: $bucketName"
Write-Host "Website URL: http://$bucketName.s3-website-us-east-1.amazonaws.com"
```

### 3.3 Create CloudFront Distribution (Optional but Recommended)
```powershell
# Create CloudFront distribution for HTTPS and CDN
$originDomain = "$bucketName.s3-website-us-east-1.amazonaws.com"

aws cloudfront create-distribution --distribution-config @"
{
  "CallerReference": "$(Get-Date -Format 'yyyyMMddHHmmss')",
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "S3-$bucketName",
      "DomainName": "$originDomain",
      "CustomOriginConfig": {
        "HTTPPort": 80,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "http-only"
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-$bucketName",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {"Forward": "none"}
    },
    "TrustedSigners": {"Enabled": false, "Quantity": 0},
    "MinTTL": 0
  },
  "Comment": "PulseOps UI Distribution",
  "Enabled": true
}
"@ --query 'Distribution.DomainName'

Write-Host "✅ CloudFront distribution created (takes 15-20 mins to deploy)"
Write-Host "Access your app at: https://[distribution-id].cloudfront.net"
```

---

## Step 4: Configure Environment Variables & Secrets

### 4.1 Store Secrets in AWS Secrets Manager
```powershell
# Store database credentials
aws secretsmanager create-secret --name pulseops/db-credentials `
  --secret-string '{
    "username": "pulseops_admin",
    "password": "YourStrongPassword123!",
    "host": "pulseops-db.xxxxx.us-east-1.rds.amazonaws.com",
    "port": "5432",
    "database": "pulseops"
  }'

# Store JWT secret
aws secretsmanager create-secret --name pulseops/jwt-secret `
  --secret-string "your-super-secret-jwt-key-change-this-in-production"
```

### 4.2 Update Lambda Environment Variables
```powershell
# Get RDS endpoint
$rdsEndpoint = aws rds describe-db-instances --db-instance-identifier pulseops-db --query "DBInstances[0].Endpoint.Address" --output text

# Update Lambda with correct database URL
aws lambda update-function-configuration --function-name pulseops-api `
  --environment Variables="{
    DATABASE_URL=postgresql://pulseops_admin:YourPassword@$rdsEndpoint:5432/pulseops,
    SECRET_KEY=your-super-secret-jwt-key-change-this-in-production,
    ENVIRONMENT=production
  }"
```

---

## Step 5: Migrate Data to RDS

### 5.1 Install PostgreSQL Client
```powershell
# Install psycopg2 for PostgreSQL connections
pip install psycopg2-binary
```

### 5.2 Run Migration Script
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\api

# Run database setup (creates tables)
python -c "
import psycopg2
from models.base import Base
from sqlalchemy import create_engine

# Update with your RDS endpoint
DATABASE_URL = 'postgresql://pulseops_admin:YourPassword@your-rds-endpoint:5432/pulseops'

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Import data
python -c "
import json
import psycopg2

# Load exported data
with open('data_export.json') as f:
    data = json.load(f)

# Connect to RDS
conn = psycopg2.connect(
    host='your-rds-endpoint',
    port=5432,
    database='pulseops',
    user='pulseops_admin',
    password='YourPassword'
)
cursor = conn.cursor()

# Insert users
for user in data['users']:
    cursor.execute(
        'INSERT INTO users (email, role, hashed_password) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
        (user['email'], user['role'], user['hashed_password'])
    )

# Insert licenses
for lic in data['licenses']:
    cursor.execute('''
        INSERT INTO software_licenses 
        (software_name, vendor, category, monthly_cost, annual_cost, total_licenses, active_users, utilization_percent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    ''', (lic['software_name'], lic['vendor'], lic['category'], lic['monthly_cost'], 
          lic['annual_cost'], lic['total_licenses'], lic['active_users'], lic['utilization_percent']))

conn.commit()
cursor.close()
conn.close()
print('✅ Data migrated successfully')
"
```

---

## Step 6: Update Frontend API Configuration

### 6.1 Update API Base URL
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\ui\src

# Update config.js or api.js with your API Gateway URL
# Example: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

Update `src/services/api.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-gateway-url/prod';
```

### 6.2 Rebuild and Redeploy
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\ui

# Rebuild with new API URL
npm run build

# Upload to S3
aws s3 sync build/ s3://$bucketName --delete

# Invalidate CloudFront cache
$distributionId = aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='PulseOps UI Distribution'].Id" --output text
aws cloudfront create-invalidation --distribution-id $distributionId --paths "/*"
```

---

## Step 7: Test Deployment

### 7.1 Test API
```powershell
# Test API health
$apiUrl = "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
Invoke-RestMethod -Uri "$apiUrl/api/health" -Method GET

# Test login
Invoke-RestMethod -Uri "$apiUrl/api/auth/login?email=it@pulseops.com&password=itadmin123" -Method POST
```

### 7.2 Test Frontend
1. Open your CloudFront URL: `https://[distribution-id].cloudfront.net`
2. Login with: `it@pulseops.com` / `itadmin123`
3. Verify dashboard loads with data
4. Check all KPIs and charts display correctly

---

## Step 8: Security Hardening (Important!)

### 8.1 Configure CORS
Update Lambda to allow only your CloudFront domain:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-cloudfront-domain.cloudfront.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.2 Restrict Database Access
```powershell
# Update RDS security group to allow only Lambda access
$sgId = aws rds describe-db-instances --db-instance-identifier pulseops-db --query "DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId" --output text

# Remove public access (after testing)
aws rds modify-db-instance --db-instance-identifier pulseops-db --no-publicly-accessible
```

### 8.3 Enable SSL/HTTPS
- CloudFront already provides HTTPS
- For custom domain, request ACM certificate

---

## Cost Estimates

**Monthly costs (approximate):**
- RDS PostgreSQL (db.t3.micro): $15-20
- Lambda (1M requests): $0.20
- API Gateway: $3.50
- S3 Storage (1GB): $0.02
- CloudFront (10GB transfer): $1.00
- **Total: ~$20-25/month**

**Free Tier Benefits (first year):**
- RDS: 750 hours/month free
- Lambda: 1M requests free
- S3: 5GB storage free
- CloudFront: 1TB transfer free

---

## Monitoring & Maintenance

### View Logs
```powershell
# Lambda logs
aws logs tail /aws/lambda/pulseops-api --follow

# Check errors
aws logs filter-log-events --log-group-name /aws/lambda/pulseops-api --filter-pattern "ERROR"
```

### Update Code
```powershell
# Update Lambda function
cd d:\SuperOps-Hackathon\pulseops\services\api\deploy
Compress-Archive -Path * -DestinationPath ..\pulseops-api-new.zip -Force
aws lambda update-function-code --function-name pulseops-api --zip-file fileb://pulseops-api-new.zip

# Update frontend
cd d:\SuperOps-Hackathon\pulseops\services\ui
npm run build
aws s3 sync build/ s3://$bucketName --delete
```

---

## Troubleshooting

### Issue: "Lambda timeout"
- Increase timeout: `aws lambda update-function-configuration --function-name pulseops-api --timeout 60`

### Issue: "Database connection failed"
- Check security group allows Lambda IP range
- Verify DATABASE_URL environment variable
- Check RDS status in console

### Issue: "CORS errors in browser"
- Update CORS configuration in main.py
- Redeploy Lambda function

### Issue: "404 on React routes"
- Ensure S3 error document is set to `index.html`
- CloudFront should have custom error response for 404 → index.html

---

## Quick Deploy Script

Save time with this all-in-one script:
```powershell
# See: deployment/quick-deploy.ps1
cd d:\SuperOps-Hackathon\pulseops\deployment
.\quick-deploy.ps1
```

---

## Support

For issues:
1. Check AWS CloudWatch logs
2. Review Lambda execution logs
3. Test API endpoints with Postman
4. Check browser console for frontend errors

**Next Steps:**
- Set up custom domain (Route 53 + ACM)
- Configure CI/CD pipeline (GitHub Actions)
- Add monitoring (CloudWatch Alarms)
- Set up backups (RDS automated backups)
