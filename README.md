# PulseOps AI

An autonomous AI agent designed to help Managed Service Providers (MSPs) grow profitably while enabling IT teams to optimize budget and software usage.

## Features

### For MSPs:
- 📊 Client profitability tracking and health scores
- ⚠️ Churn risk detection and early warning alerts
- 💰 Upsell opportunity identification
- 📈 Actionable revenue growth recommendations

### For IT Teams:
- 💳 Departmental spend and SaaS license monitoring
- 🔍 Cost anomaly detection and alerts
- 🤖 Automated license deactivation for unused software
- 💡 Budget optimization recommendations

## Architecture

- **Frontend**: React.js deployed to S3 + CloudFront
- **API**: FastAPI running on AWS Lambda + API Gateway
- **ML**: Python ML models on Lambda + SageMaker
- **Database**: RDS PostgreSQL + DynamoDB
- **Storage**: S3 for data and model artifacts

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS CLI v2
- AWS SAM CLI v1.x

### Local Development
```bash
# Install dependencies
cd services/api && pip install -r requirements.txt
cd ../ml && pip install -r requirements.txt
cd ../ui && npm install

# Start services
cd services/api && uvicorn main:app --reload
cd services/ml && python -m flask run
cd services/ui && npm start
```

### AWS Deployment

#### Quick Deploy (Recommended)
```bash
# Configure AWS credentials
aws configure

# Deploy to development
cd infrastructure
python deploy.py --environment dev --region us-east-1

# Or use PowerShell script
.\quick-deploy.ps1 -Environment dev -Region us-east-1
```

#### Manual Deploy
```bash
# Build services
cd infrastructure
sam build --template-file sam-template.yaml

# Deploy stack
sam deploy \
  --stack-name pulseops-dev \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides Environment=dev

# Deploy UI to S3
aws s3 sync ../services/ui/build s3://<bucket-name>
```

See [infrastructure/DEPLOYMENT.md](infrastructure/DEPLOYMENT.md) for detailed deployment instructions.

### Database Setup
```bash
# Initialize database
cd infrastructure
python setup_database.py \
  --db-url postgresql://user:pass@host/pulseops \
  --action create

# Seed with sample data
python setup_database.py \
  --db-url postgresql://user:pass@host/pulseops \
  --action seed
```

### Testing Deployment
```bash
# Test all services
cd infrastructure
python test_deployment.py \
  --api-url https://your-api.execute-api.region.amazonaws.com/Prod \
  --ml-url https://your-ml-api.execute-api.region.amazonaws.com/Prod \
  --ui-url https://your-cloudfront-url.cloudfront.net
```

## CI/CD Pipeline

### Automated Workflows

The project includes comprehensive GitHub Actions workflows:

- **Continuous Integration**: Automated testing on all PRs
- **Continuous Deployment**: Auto-deploy to dev/prod
- **Security Scanning**: Daily vulnerability scans
- **Dependency Updates**: Weekly update reports

### Quick Setup

1. **Configure Secrets** (Settings → Secrets → Actions)
   ```
   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
   DEV_DB_USERNAME, DEV_DB_PASSWORD, DEV_JWT_SECRET
   PROD_DB_USERNAME, PROD_DB_PASSWORD, PROD_JWT_SECRET
   ```

2. **Create Environments**
   - `development` (no protection)
   - `production` (required reviewers)

3. **Push and Deploy**
   ```bash
   git push origin develop  # Auto-deploys to dev
   git push origin main     # Requires approval for prod
   ```

See [CI/CD Guide](.github/CI_CD_GUIDE.md) for complete documentation.

## Project Structure
```
pulseops/
├── .github/
│   ├── workflows/    # CI/CD pipelines
│   └── ISSUE_TEMPLATE/
├── services/
│   ├── api/          # FastAPI backend + tests
│   ├── ml/           # ML models + tests
│   └── ui/           # React frontend + tests
├── infrastructure/   # AWS SAM/CloudFormation
├── data/            # Sample data
└── docs/            # Documentation
```

## Documentation

- [Deployment Guide](infrastructure/DEPLOYMENT.md)
- [CI/CD Guide](.github/CI_CD_GUIDE.md)
- [Project Summary](PROJECT_SUMMARY.md)
- [API Documentation](https://api-url/docs) (after deployment)

## Tech Stack

**Backend**: FastAPI 0.104.1, SQLAlchemy 2.0.23, PostgreSQL 15.4  
**ML/AI**: Scikit-learn 1.3.2, Gradient Boosting, Statistical Analysis  
**Frontend**: React 18.2.0, Material-UI 5.15.0, Recharts 2.8.0  
**Infrastructure**: AWS Lambda, API Gateway, S3, CloudFront, RDS, DynamoDB  
**CI/CD**: GitHub Actions, pytest, Jest, Trivy, Snyk  

## Project Status

✅ **100% Complete** - All 6 steps implemented:
1. ✅ Project Structure
2. ✅ FastAPI Backend  
3. ✅ ML Service
4. ✅ React UI
5. ✅ AWS Infrastructure
6. ✅ CI/CD Pipeline

**Ready for production deployment!** 🚀

## License

MIT