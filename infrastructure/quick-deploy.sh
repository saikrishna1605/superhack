#!/bin/bash

# Quick deployment script for PulseOps AI
# Usage: ./quick-deploy.sh [dev|prod] [region]

set -e  # Exit on error

ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
STACK_NAME="pulseops-${ENVIRONMENT}"

echo "=================================="
echo "PulseOps AI - Quick Deploy"
echo "=================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Stack: ${STACK_NAME}"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ SAM CLI not found. Please install it first.${NC}"
    exit 1
fi

# Validate AWS credentials
echo "🔐 Validating AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure'${NC}"
    exit 1
fi
echo -e "${GREEN}✅ AWS credentials valid${NC}"

# Build Lambda packages
echo ""
echo "📦 Building Lambda packages..."
cd ..

# API Service
echo "  Building API service..."
cd services/api
pip install -q -r requirements.txt -t package 2>&1 | grep -v "already satisfied" || true
cd ../..

# ML Service
echo "  Building ML service..."
cd services/ml
pip install -q -r requirements.txt -t package 2>&1 | grep -v "already satisfied" || true
cd ../..

echo -e "${GREEN}✅ Lambda packages built${NC}"

# Build UI
echo ""
echo "🎨 Building React UI..."
cd services/ui
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
npm run build --silent
cd ../..
echo -e "${GREEN}✅ UI built${NC}"

# SAM Build
echo ""
echo "🏗️  Running SAM build..."
cd infrastructure
sam build --template-file sam-template.yaml > /dev/null
echo -e "${GREEN}✅ SAM build complete${NC}"

# SAM Deploy
echo ""
echo "🚀 Deploying to AWS..."
sam deploy \
  --stack-name ${STACK_NAME} \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region ${REGION} \
  --parameter-overrides \
    Environment=${ENVIRONMENT} \
    DBUsername=pulseops_admin \
    DBPassword=TempPassword123! \
    JWTSecretKey=TempJWTKey123! \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

echo -e "${GREEN}✅ Stack deployed${NC}"

# Get outputs
echo ""
echo "📊 Fetching stack outputs..."
OUTPUTS=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --query 'Stacks[0].Outputs' \
  --output json)

API_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="ApiUrl") | .OutputValue')
UI_BUCKET=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="UIBucketName") | .OutputValue')
UI_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="UIUrl") | .OutputValue')

# Deploy UI to S3
echo ""
echo "☁️  Deploying UI to S3..."
aws s3 sync ../services/ui/build s3://${UI_BUCKET} --delete --region ${REGION}
echo -e "${GREEN}✅ UI deployed to S3${NC}"

# Display results
echo ""
echo "=================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=================================="
echo ""
echo -e "${YELLOW}📋 Stack Outputs:${NC}"
echo "  API URL: ${API_URL}"
echo "  UI URL: ${UI_URL}"
echo "  UI Bucket: ${UI_BUCKET}"
echo ""
echo -e "${YELLOW}📌 Next Steps:${NC}"
echo "  1. Update services/ui/.env.production with API_URL"
echo "  2. Rebuild and redeploy UI"
echo "  3. Run database migrations"
echo "  4. Test the application"
echo ""
echo -e "${GREEN}💡 Access your application at: ${UI_URL}${NC}"
echo ""
