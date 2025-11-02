#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick deployment script for PulseOps to AWS
.DESCRIPTION
    This script automates the deployment of PulseOps application to AWS
.PARAMETER Environment
    Deployment environment (dev, staging, prod)
.PARAMETER SkipBuild
    Skip building frontend
.EXAMPLE
    .\quick-deploy.ps1 -Environment dev
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment = 'dev',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 PulseOps AWS Deployment Script" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host ""

# Configuration
$PROJECT_ROOT = Split-Path $PSScriptRoot -Parent
$API_DIR = Join-Path $PROJECT_ROOT "services\api"
$UI_DIR = Join-Path $PROJECT_ROOT "services\ui"
$REGION = "us-east-1"
$BUCKET_NAME = "pulseops-ui-$Environment-$(Get-Date -Format 'yyyyMMdd')"

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Cyan

# Check AWS CLI
try {
    $awsVersion = aws --version
    Write-Host "✅ AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install: winget install Amazon.AWSCLI" -ForegroundColor Red
    exit 1
}

# Check credentials
try {
    $accountId = aws sts get-caller-identity --query Account --output text
    Write-Host "✅ AWS Account: $accountId" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured. Run: aws configure" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 1: Deploy Backend API
Write-Host "📦 Step 1: Packaging Backend API..." -ForegroundColor Cyan
Set-Location $API_DIR

# Create deployment package
if (Test-Path "deploy") {
    Remove-Item -Recurse -Force deploy
}
New-Item -ItemType Directory -Force -Path deploy | Out-Null

# Copy application files
Write-Host "  Copying application files..."
Copy-Item -Path "*.py" -Destination "deploy\" -Exclude "test_*","seed_*","reset_*","fix_*"
if (Test-Path "routers") { Copy-Item -Path "routers" -Destination "deploy\routers" -Recurse }
if (Test-Path "models") { Copy-Item -Path "models" -Destination "deploy\models" -Recurse }
Copy-Item -Path "requirements.txt" -Destination "deploy\"

# Install dependencies
Write-Host "  Installing dependencies..."
Set-Location deploy
pip install -r requirements.txt -t . --upgrade --quiet

# Create Lambda handler wrapper
Write-Host "  Creating Lambda handler..."
$handlerCode = @"
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")
"@
Set-Content -Path "lambda_handler.py" -Value $handlerCode

# Create ZIP
Write-Host "  Creating deployment package..."
if (Test-Path "..\pulseops-api.zip") {
    Remove-Item "..\pulseops-api.zip"
}
Compress-Archive -Path * -DestinationPath "..\pulseops-api.zip" -CompressionLevel Optimal

Set-Location ..
Write-Host "✅ Backend package created: pulseops-api.zip" -ForegroundColor Green
Write-Host ""

# Step 2: Create/Update Lambda Function
Write-Host "🔧 Step 2: Deploying Lambda Function..." -ForegroundColor Cyan

$lambdaName = "pulseops-api-$Environment"
$roleName = "pulseops-lambda-role-$Environment"

# Check if Lambda exists
$lambdaExists = $false
try {
    aws lambda get-function --function-name $lambdaName 2>&1 | Out-Null
    $lambdaExists = $true
    Write-Host "  Lambda function exists, updating..." -ForegroundColor Yellow
} catch {
    Write-Host "  Creating new Lambda function..." -ForegroundColor Yellow
}

if (-not $lambdaExists) {
    # Create IAM role
    Write-Host "  Creating IAM role..."
    $trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
"@
    
    aws iam create-role --role-name $roleName --assume-role-policy-document $trustPolicy 2>&1 | Out-Null
    
    # Attach policies
    aws iam attach-role-policy --role-name $roleName `
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    Write-Host "  Waiting for IAM role to propagate..."
    Start-Sleep -Seconds 10
    
    # Create Lambda function
    $roleArn = "arn:aws:iam::${accountId}:role/$roleName"
    
    aws lambda create-function --function-name $lambdaName `
        --runtime python3.11 `
        --role $roleArn `
        --handler lambda_handler.handler `
        --zip-file fileb://pulseops-api.zip `
        --timeout 30 `
        --memory-size 512 `
        --environment "Variables={
            SECRET_KEY=change-this-secret-key-in-production,
            ENVIRONMENT=$Environment
        }" 2>&1 | Out-Null
    
    Write-Host "✅ Lambda function created: $lambdaName" -ForegroundColor Green
} else {
    # Update existing function
    aws lambda update-function-code --function-name $lambdaName `
        --zip-file fileb://pulseops-api.zip 2>&1 | Out-Null
    
    Write-Host "✅ Lambda function updated: $lambdaName" -ForegroundColor Green
}

# Wait for Lambda to be ready
Write-Host "  Waiting for Lambda to be ready..."
Start-Sleep -Seconds 5

Write-Host ""

# Step 3: Create/Update API Gateway
Write-Host "🌐 Step 3: Configuring API Gateway..." -ForegroundColor Cyan

$apiName = "pulseops-api-$Environment"

# Check if API exists
$apiId = aws apigateway get-rest-apis --query "items[?name=='$apiName'].id" --output text

if ([string]::IsNullOrWhiteSpace($apiId)) {
    Write-Host "  Creating new API Gateway..."
    
    # Create API
    $apiId = aws apigateway create-rest-api --name $apiName --query 'id' --output text
    
    # Get root resource
    $rootId = aws apigateway get-resources --rest-api-id $apiId --query 'items[0].id' --output text
    
    # Create proxy resource
    $proxyId = aws apigateway create-resource --rest-api-id $apiId --parent-id $rootId --path-part '{proxy+}' --query 'id' --output text
    
    # Create ANY method
    aws apigateway put-method --rest-api-id $apiId --resource-id $proxyId --http-method ANY --authorization-type NONE 2>&1 | Out-Null
    
    # Integrate with Lambda
    $lambdaArn = "arn:aws:lambda:${REGION}:${accountId}:function:$lambdaName"
    aws apigateway put-integration --rest-api-id $apiId --resource-id $proxyId --http-method ANY `
        --type AWS_PROXY --integration-http-method POST `
        --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/$lambdaArn/invocations" 2>&1 | Out-Null
    
    # Add root method
    aws apigateway put-method --rest-api-id $apiId --resource-id $rootId --http-method ANY --authorization-type NONE 2>&1 | Out-Null
    aws apigateway put-integration --rest-api-id $apiId --resource-id $rootId --http-method ANY `
        --type AWS_PROXY --integration-http-method POST `
        --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/$lambdaArn/invocations" 2>&1 | Out-Null
    
    # Grant API Gateway permission
    aws lambda add-permission --function-name $lambdaName `
        --statement-id apigateway-invoke-$Environment `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${accountId}:${apiId}/*/*" 2>&1 | Out-Null
    
    Write-Host "✅ API Gateway created: $apiId" -ForegroundColor Green
} else {
    Write-Host "  API Gateway exists: $apiId" -ForegroundColor Yellow
}

# Deploy API
aws apigateway create-deployment --rest-api-id $apiId --stage-name $Environment 2>&1 | Out-Null

$apiUrl = "https://${apiId}.execute-api.${REGION}.amazonaws.com/$Environment"
Write-Host "✅ API deployed at: $apiUrl" -ForegroundColor Green
Write-Host ""

# Step 4: Build and Deploy Frontend
Write-Host "🎨 Step 4: Building Frontend..." -ForegroundColor Cyan
Set-Location $UI_DIR

if (-not $SkipBuild) {
    # Create .env.production with API URL
    $envContent = "REACT_APP_API_URL=$apiUrl"
    Set-Content -Path ".env.production" -Value $envContent
    
    Write-Host "  Installing dependencies..."
    npm install --silent 2>&1 | Out-Null
    
    Write-Host "  Building React app..."
    npm run build 2>&1 | Out-Null
    
    Write-Host "✅ Frontend built successfully" -ForegroundColor Green
} else {
    Write-Host "  Skipping build (--SkipBuild)" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Deploy to S3
Write-Host "☁️ Step 5: Deploying to S3..." -ForegroundColor Cyan

# Check if bucket exists
$bucketExists = $false
try {
    aws s3 ls "s3://$BUCKET_NAME" 2>&1 | Out-Null
    $bucketExists = $true
} catch {
}

if (-not $bucketExists) {
    Write-Host "  Creating S3 bucket: $BUCKET_NAME"
    aws s3 mb "s3://$BUCKET_NAME" --region $REGION 2>&1 | Out-Null
    
    # Enable static website hosting
    aws s3 website "s3://$BUCKET_NAME" --index-document index.html --error-document index.html 2>&1 | Out-Null
    
    # Make bucket public
    $policy = @"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
  }]
}
"@
    Set-Content -Path "bucket-policy.json" -Value $policy
    aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json 2>&1 | Out-Null
    Remove-Item "bucket-policy.json"
    
    Write-Host "✅ S3 bucket created: $BUCKET_NAME" -ForegroundColor Green
}

# Upload files
Write-Host "  Uploading files to S3..."
aws s3 sync build/ "s3://$BUCKET_NAME" --delete --quiet

$websiteUrl = "http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
Write-Host "✅ Frontend deployed to S3" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Your Application URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: $websiteUrl" -ForegroundColor White
Write-Host "  API:      $apiUrl" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Test Login:" -ForegroundColor Yellow
Write-Host "  Email:    it@pulseops.com" -ForegroundColor White
Write-Host "  Password: itadmin123" -ForegroundColor White
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open the frontend URL in your browser"
Write-Host "  2. Login with the credentials above"
Write-Host "  3. Test the dashboard functionality"
Write-Host "  4. (Optional) Set up CloudFront for HTTPS"
Write-Host "  5. (Optional) Configure custom domain"
Write-Host ""
Write-Host "💰 Estimated Monthly Cost: ~$20-25" -ForegroundColor Yellow
Write-Host "   (May be $0 with AWS Free Tier)" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Deployment Details:" -ForegroundColor Yellow
Write-Host "  Lambda:  $lambdaName" -ForegroundColor White
Write-Host "  API GW:  $apiId" -ForegroundColor White
Write-Host "  S3:      $BUCKET_NAME" -ForegroundColor White
Write-Host "  Region:  $REGION" -ForegroundColor White
Write-Host ""

# Save deployment info
$deploymentInfo = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    environment = $Environment
    region = $REGION
    lambdaName = $lambdaName
    apiId = $apiId
    apiUrl = $apiUrl
    bucketName = $BUCKET_NAME
    websiteUrl = $websiteUrl
}

$deploymentInfo | ConvertTo-Json | Set-Content -Path "$PROJECT_ROOT\deployment\last-deployment.json"

Set-Location $PROJECT_ROOT
Write-Host "✅ Deployment info saved to deployment\last-deployment.json" -ForegroundColor Green
