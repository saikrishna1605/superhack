# Quick deployment script for PulseOps AI (PowerShell)
# Usage: .\quick-deploy.ps1 -Environment dev -Region us-east-1

param(
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment = 'dev',
    
    [string]$Region = 'us-east-1'
)

$ErrorActionPreference = "Stop"

$StackName = "pulseops-$Environment"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "PulseOps AI - Quick Deploy" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Environment: $Environment"
Write-Host "Region: $Region"
Write-Host "Stack: $StackName"
Write-Host ""

# Check if AWS CLI is installed
try {
    $null = aws --version
    Write-Host "✅ AWS CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if SAM CLI is installed
try {
    $null = sam --version
    Write-Host "✅ SAM CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ SAM CLI not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Validate AWS credentials
Write-Host ""
Write-Host "🔐 Validating AWS credentials..." -ForegroundColor Yellow
try {
    $null = aws sts get-caller-identity
    Write-Host "✅ AWS credentials valid" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured. Run 'aws configure'" -ForegroundColor Red
    exit 1
}

# Build Lambda packages
Write-Host ""
Write-Host "📦 Building Lambda packages..." -ForegroundColor Yellow
Push-Location ..

# API Service
Write-Host "  Building API service..."
Push-Location services\api
python -m pip install -q -r requirements.txt -t package
Pop-Location

# ML Service
Write-Host "  Building ML service..."
Push-Location services\ml
python -m pip install -q -r requirements.txt -t package
Pop-Location

Write-Host "✅ Lambda packages built" -ForegroundColor Green

# Build UI
Write-Host ""
Write-Host "🎨 Building React UI..." -ForegroundColor Yellow
Push-Location services\ui
if (-not (Test-Path "node_modules")) {
    npm install --silent
}
npm run build
Pop-Location
Write-Host "✅ UI built" -ForegroundColor Green

# SAM Build
Write-Host ""
Write-Host "🏗️  Running SAM build..." -ForegroundColor Yellow
Push-Location infrastructure
sam build --template-file sam-template.yaml | Out-Null
Write-Host "✅ SAM build complete" -ForegroundColor Green

# SAM Deploy
Write-Host ""
Write-Host "🚀 Deploying to AWS..." -ForegroundColor Yellow
sam deploy `
  --stack-name $StackName `
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM `
  --region $Region `
  --parameter-overrides `
    Environment=$Environment `
    DBUsername=pulseops_admin `
    DBPassword=TempPassword123! `
    JWTSecretKey=TempJWTKey123! `
  --no-confirm-changeset `
  --no-fail-on-empty-changeset

Write-Host "✅ Stack deployed" -ForegroundColor Green

# Get outputs
Write-Host ""
Write-Host "📊 Fetching stack outputs..." -ForegroundColor Yellow
$OutputsJson = aws cloudformation describe-stacks `
  --stack-name $StackName `
  --region $Region `
  --query 'Stacks[0].Outputs' `
  --output json | ConvertFrom-Json

$ApiUrl = ($OutputsJson | Where-Object { $_.OutputKey -eq "ApiUrl" }).OutputValue
$UIBucket = ($OutputsJson | Where-Object { $_.OutputKey -eq "UIBucketName" }).OutputValue
$UIUrl = ($OutputsJson | Where-Object { $_.OutputKey -eq "UIUrl" }).OutputValue

# Deploy UI to S3
Write-Host ""
Write-Host "☁️  Deploying UI to S3..." -ForegroundColor Yellow
aws s3 sync ..\services\ui\build s3://$UIBucket --delete --region $Region
Write-Host "✅ UI deployed to S3" -ForegroundColor Green

Pop-Location

# Display results
Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Stack Outputs:" -ForegroundColor Yellow
Write-Host "  API URL: $ApiUrl"
Write-Host "  UI URL: $UIUrl"
Write-Host "  UI Bucket: $UIBucket"
Write-Host ""
Write-Host "📌 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update services/ui/.env.production with API_URL"
Write-Host "  2. Rebuild and redeploy UI"
Write-Host "  3. Run database migrations"
Write-Host "  4. Test the application"
Write-Host ""
Write-Host "💡 Access your application at: $UIUrl" -ForegroundColor Green
Write-Host ""
