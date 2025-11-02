# Step-by-Step AWS Deployment Instructions

## Quick Start (Automated)

If you want to deploy quickly, run:

```powershell
cd d:\SuperOps-Hackathon\pulseops\deployment
.\quick-deploy.ps1 -Environment dev
```

This will automatically:
1. Package your backend API
2. Create Lambda function
3. Set up API Gateway
4. Build React frontend
5. Deploy to S3
6. Provide you with URLs

**Time: ~5-10 minutes**

---

## Step-by-Step Manual Deployment

Follow these steps if you want more control:

### ✅ **Step 1: Install AWS CLI & Configure Credentials**

1. **Install AWS CLI:**
   ```powershell
   winget install Amazon.AWSCLI
   ```

2. **Configure AWS credentials:**
   ```powershell
   aws configure
   ```
   
   Enter:
   - **AWS Access Key ID**: (get from AWS Console → IAM → Users → Security credentials)
   - **AWS Secret Access Key**: (from same location)
   - **Default region**: `us-east-1`
   - **Default output format**: `json`

3. **Verify it works:**
   ```powershell
   aws sts get-caller-identity
   ```
   You should see your account info.

---

### ✅ **Step 2: Package Backend API**

```powershell
cd d:\SuperOps-Hackathon\pulseops\services\api

# Create deployment folder
New-Item -ItemType Directory -Force -Path deploy

# Copy files
Copy-Item -Path *.py -Destination deploy\ -Exclude "test_*","seed_*"
Copy-Item -Path routers -Destination deploy\routers -Recurse
Copy-Item -Path models -Destination deploy\models -Recurse
Copy-Item -Path requirements.txt -Destination deploy\

# Install dependencies
cd deploy
pip install -r requirements.txt -t . --upgrade

# Create Lambda handler
@"
from mangum import Mangum
from main import app
handler = Mangum(app, lifespan='off')
"@ | Out-File -FilePath lambda_handler.py

# Create ZIP
cd ..
Compress-Archive -Path deploy\* -DestinationPath pulseops-api.zip -Force

Write-Host "✅ Package created: pulseops-api.zip"
```

---

### ✅ **Step 3: Create Lambda Function**

```powershell
# Get your AWS account ID
$accountId = aws sts get-caller-identity --query Account --output text

# Create IAM role for Lambda
aws iam create-role --role-name pulseops-lambda-role --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}'

# Attach execution policy
aws iam attach-role-policy --role-name pulseops-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Wait for IAM to propagate
Start-Sleep -Seconds 10

# Create Lambda function
aws lambda create-function --function-name pulseops-api `
  --runtime python3.11 `
  --role "arn:aws:iam::${accountId}:role/pulseops-lambda-role" `
  --handler lambda_handler.handler `
  --zip-file fileb://pulseops-api.zip `
  --timeout 30 `
  --memory-size 512 `
  --environment "Variables={SECRET_KEY=change-this-in-production}"

Write-Host "✅ Lambda function created"
```

---

### ✅ **Step 4: Create API Gateway**

```powershell
# Create REST API
$apiId = aws apigateway create-rest-api --name pulseops-api --query 'id' --output text

# Get root resource
$rootId = aws apigateway get-resources --rest-api-id $apiId --query 'items[0].id' --output text

# Create proxy resource {proxy+}
$proxyId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootId --path-part '{proxy+}' --query 'id' --output text

# Create ANY method on proxy
aws apigateway put-method --rest-api-id $apiId --resource-id $proxyId --http-method ANY --authorization-type NONE

# Integrate with Lambda
$lambdaArn = "arn:aws:lambda:us-east-1:${accountId}:function:pulseops-api"
aws apigateway put-integration --rest-api-id $apiId --resource-id $proxyId --http-method ANY --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$lambdaArn/invocations"

# Create ANY method on root
aws apigateway put-method --rest-api-id $apiId --resource-id $rootId --http-method ANY --authorization-type NONE

aws apigateway put-integration --rest-api-id $apiId --resource-id $rootId --http-method ANY --type AWS_PROXY --integration-http-method POST --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$lambdaArn/invocations"

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission --function-name pulseops-api --statement-id apigateway-invoke --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:${accountId}:${apiId}/*/*"

# Deploy API to 'prod' stage
aws apigateway create-deployment --rest-api-id $apiId --stage-name prod

# Get API URL
$apiUrl = "https://${apiId}.execute-api.us-east-1.amazonaws.com/prod"
Write-Host "✅ API deployed at: $apiUrl"
```

**SAVE THIS URL!** You'll need it for the frontend.

---

### ✅ **Step 5: Build React Frontend**

```powershell
cd d:\SuperOps-Hackathon\pulseops\services\ui

# Create production environment file
"REACT_APP_API_URL=$apiUrl" | Out-File -FilePath .env.production

# Install dependencies (if not already)
npm install

# Build for production
npm run build

Write-Host "✅ React app built"
```

---

### ✅ **Step 6: Deploy Frontend to S3**

```powershell
# Create unique bucket name
$bucketName = "pulseops-ui-$(Get-Date -Format 'yyyyMMdd')"

# Create S3 bucket
aws s3 mb "s3://$bucketName" --region us-east-1

# Enable static website hosting
aws s3 website "s3://$bucketName" --index-document index.html --error-document index.html

# Upload build files
aws s3 sync build/ "s3://$bucketName" --delete

# Make bucket public
$policy = @"
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
Set-Content -Path bucket-policy.json -Value $policy
aws s3api put-bucket-policy --bucket $bucketName --policy file://bucket-policy.json
Remove-Item bucket-policy.json

# Get website URL
$websiteUrl = "http://$bucketName.s3-website-us-east-1.amazonaws.com"
Write-Host "✅ Frontend deployed at: $websiteUrl"
```

---

### ✅ **Step 7: Test Your Application**

1. **Open the website URL in your browser:**
   ```
   http://pulseops-ui-YYYYMMDD.s3-website-us-east-1.amazonaws.com
   ```

2. **Login with:**
   - Email: `it@pulseops.com`
   - Password: `itadmin123`

3. **Verify:**
   - ✅ Login works
   - ✅ Dashboard loads
   - ✅ Charts display data
   - ✅ Filters work

---

## Important Notes

### 🔒 **Security (Critical!)**

Your app is now public but using SQLite in Lambda (not ideal for production). For production:

1. **Migrate to RDS PostgreSQL** (see DEPLOYMENT_GUIDE.md)
2. **Add CloudFront** for HTTPS
3. **Use AWS Secrets Manager** for credentials
4. **Restrict CORS** to your domain only

### 💰 **Cost Estimate**

With just Lambda + S3:
- **Lambda**: ~$0-5/month (1M requests free)
- **API Gateway**: ~$3/month
- **S3**: ~$0.50/month
- **Total: ~$3-8/month**

### 🔄 **Update Application**

**Update Backend:**
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\api\deploy
Compress-Archive -Path * -DestinationPath ..\pulseops-api-updated.zip -Force
aws lambda update-function-code --function-name pulseops-api --zip-file fileb://pulseops-api-updated.zip
```

**Update Frontend:**
```powershell
cd d:\SuperOps-Hackathon\pulseops\services\ui
npm run build
aws s3 sync build/ "s3://$bucketName" --delete
```

### 📊 **Monitor Logs**

```powershell
# View Lambda logs
aws logs tail /aws/lambda/pulseops-api --follow

# Check for errors
aws logs filter-log-events --log-group-name /aws/lambda/pulseops-api --filter-pattern "ERROR"
```

---

## Troubleshooting

### "Lambda timeout error"
```powershell
aws lambda update-function-configuration --function-name pulseops-api --timeout 60
```

### "CORS error in browser"
The API needs CORS headers. Update `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Then redeploy Lambda.

### "404 on React routes"
S3 needs to serve index.html for all routes. Already configured with `--error-document index.html`.

### "Can't see data in dashboard"
Check:
1. Browser console for errors
2. Lambda logs: `aws logs tail /aws/lambda/pulseops-api --follow`
3. API endpoint directly: `curl https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/health`

---

## Next Steps

✅ **Done with basic deployment!**

**Optional Enhancements:**
1. **Add HTTPS with CloudFront** (see DEPLOYMENT_GUIDE.md)
2. **Custom domain** with Route 53
3. **CI/CD pipeline** with GitHub Actions
4. **Monitoring** with CloudWatch Alarms
5. **Database** migration to RDS PostgreSQL

---

## Quick Reference Commands

```powershell
# Redeploy everything
cd d:\SuperOps-Hackathon\pulseops\deployment
.\quick-deploy.ps1

# Update just backend
cd d:\SuperOps-Hackathon\pulseops\services\api
# (make changes)
cd deploy; Compress-Archive -Path * -DestinationPath ..\pulseops-api.zip -Force; cd ..
aws lambda update-function-code --function-name pulseops-api --zip-file fileb://pulseops-api.zip

# Update just frontend
cd d:\SuperOps-Hackathon\pulseops\services\ui
# (make changes)
npm run build
aws s3 sync build/ "s3://YOUR-BUCKET-NAME" --delete

# View logs
aws logs tail /aws/lambda/pulseops-api --follow

# Check Lambda status
aws lambda get-function --function-name pulseops-api

# List S3 buckets
aws s3 ls

# Check API Gateway
aws apigateway get-rest-apis
```

---

**Need help?** Check the full guide: `DEPLOYMENT_GUIDE.md`
