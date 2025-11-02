# PulseOps AI - Hackathon Project

A sophisticated AI-powered platform designed to help Managed Service Providers (MSPs) optimize their operations and enable IT teams to better manage their software resources.

## Project Overview

PulseOps AI is a comprehensive solution that combines:
- 🤖 Advanced ML algorithms for predictive analytics
- 📊 Real-time monitoring and alerting
- 💼 Client management and profitability tracking
- 🔑 Software license optimization

## Key Features

### For MSPs
- 📈 Real-time client health monitoring
- ⚠️ Proactive churn prediction
- 💰 Revenue optimization suggestions
- 🎯 Targeted upsell recommendations

### For IT Teams
- 📱 Software license usage tracking
- 💳 Budget optimization
- 🔍 Anomaly detection
- 🤖 Automated license management

## Technical Architecture

- **Frontend**: React.js with modern UI components
- **Backend**: FastAPI for high-performance API
- **ML Services**: Python-based ML models
- **Database**: PostgreSQL for relational data

## Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database

### Local Development Setup

1. **Clone the Repository**
```bash
git clone https://github.com/simisgithome/SuperOps-hackathon.git
cd SuperOps-hackathon
```

2. **Start Backend API Server**
```bash
cd services/api
python main.py
# The API server will start on http://localhost:8000
```

3. **Start Frontend UI Server**
```bash
cd services/ui
npm install    # Only needed first time or when dependencies change
npm start
# The UI will automatically open in your default browser at http://localhost:3000
```

### Login Credentials

#### MSP Dashboard
- Username: admin
- Password: admin

#### IT Dashboard
- Username: it_user
- Password: password

## Project Structure

```
services/
├── api/           # Backend FastAPI service
├── ml/            # Machine Learning services
└── ui/            # React frontend application
```

## API Documentation

- API documentation is available at `http://localhost:8000/docs` when the backend server is running
- Swagger UI provides interactive API testing interface

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'feat: add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## License

This project is part of the SuperOps Hackathon and is subject to the hackathon's terms and conditions.

# Make a small change
echo "# Testing CI/CD" >> TEST.md

# Commit and push
git add TEST.md
git commit -m "test: CI/CD pipeline"
git push origin feature/test-ci-cd

# Create a Pull Request on GitHub
# Watch the CI/CD pipeline run!
```

## Workflow Triggers

### Automatic

- **Push to `develop`** → Tests + Deploy to Dev
- **Push to `main`** → Tests + Security + Deploy to Prod (with approval)
- **Pull Request** → All tests and checks
- **Monday 9 AM UTC** → Dependency update report
- **Daily 2 AM UTC** → Security audit + cleanup

### Manual

1. Go to **Actions** tab
2. Select **CI/CD Pipeline**
3. Click **Run workflow**
4. Choose environment (dev/staging/prod)
5. Click **Run workflow**

## Pipeline Flow

```
┌─────────────┐
│   Push/PR   │
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌─────────────┐                      ┌────────────┐
│  Test API   │                      │  Test ML   │
└──────┬──────┘                      └──────┬─────┘
       │                                    │
       ├────────────────────┬───────────────┤
       │                    │               │
       ▼                    ▼               ▼
┌─────────────┐      ┌────────────┐  ┌──────────────┐
│  Test UI    │      │  Security  │  │ Code Quality │
└──────┬──────┘      │   Scan     │  └──────────────┘
       │             └─────┬──────┘
       │                   │
       └───────────┬───────┘
                   │
                   ▼
         ┌──────────────────┐
         │  All Tests Pass? │
         └────────┬─────────┘
                  │
         ┌────────┴────────┐
         │ Yes             │ No
         ▼                 ▼
┌─────────────────┐   ┌─────────┐
│ Deploy (if dev  │   │  Stop   │
│ or main branch) │   └─────────┘
└─────────────────┘
```

## What Happens on Deployment

1. **Build Phase**
   - Install Python dependencies for API/ML
   - Install npm dependencies for UI
   - Build production UI bundle
   - Create Lambda packages

2. **Deploy Phase**
   - Run SAM build
   - Deploy CloudFormation stack
   - Sync UI to S3
   - Invalidate CloudFront cache

3. **Verify Phase**
   - Run deployment tests
   - Check API health
   - Verify ML service
   - Test UI accessibility

4. **Notification**
   - Comment on PR (if applicable)
   - Create GitHub release (for prod)
   - Display deployment URLs

## Monitoring

### View Deployment Status

- **GitHub Actions**: Real-time workflow logs
- **AWS CloudFormation**: Stack events and outputs
- **CloudWatch**: Lambda logs and metrics

### Check Deployment Health

```bash
# Test deployment
cd infrastructure
python test_deployment.py \
  --api-url https://your-api.execute-api.region.amazonaws.com/Prod \
  --ml-url https://your-ml-api.execute-api.region.amazonaws.com/Prod \
  --ui-url https://your-cloudfront-url.cloudfront.net
```

## Rollback

### Via Git Revert
```bash
git revert <commit-hash>
git push origin main
# Triggers automatic redeployment
```

### Via Manual Deploy
```bash
git checkout <previous-good-commit>
cd infrastructure
python deploy.py --environment prod
```

## Best Practices

### Branch Strategy
```
main       ──●────●────●──  (Production)
              │    │    │
develop    ──●────●────●──  (Development)
              │
feature    ──●  (Feature branches)
```

### Commit Messages
```bash
feat(api): add new analytics endpoint
fix(ui): resolve dashboard loading issue
docs: update deployment guide
test: add tests for churn prediction
chore(deps): update dependencies
```

### Before Pushing
```bash
# Run tests locally
cd services/api && pytest
cd services/ml && pytest
cd services/ui && npm test

# Run linters
flake8 services/api services/ml
cd services/ui && npm run lint
```

## Troubleshooting

### Pipeline Fails on First Run

**Issue**: Missing secrets or permissions

**Solution**:
1. Check all secrets are configured
2. Verify AWS credentials have correct permissions
3. Enable workflow permissions in Settings → Actions

### Deployment Stuck

**Issue**: CloudFormation stack update in progress

**Solution**:
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name pulseops-dev

# If needed, cancel update
aws cloudformation cancel-update-stack --stack-name pulseops-dev
```

### Tests Failing

**Issue**: Tests pass locally but fail in CI

**Solution**:
1. Check Python/Node versions match
2. Review test dependencies
3. Check environment variables
4. Look at workflow logs for details

## Next Steps

1. ✅ Configure GitHub secrets
2. ✅ Set up environments with protection rules
3. ✅ Push code and watch pipeline run
4. ✅ Create a test PR to verify checks
5. ✅ Deploy to development
6. ✅ Review and deploy to production

## Support

For issues with CI/CD:
- Check `.github/CI_CD_GUIDE.md` for detailed docs
- Review workflow logs in Actions tab
- Check GitHub Actions status page
- Contact DevOps team

---

**🎉 Congratulations! Your CI/CD pipeline is ready!**

Push your code and watch the magic happen! ✨
