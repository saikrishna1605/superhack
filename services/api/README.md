# PulseOps AI - API Service

FastAPI backend for PulseOps AI platform.

## Features

- **Authentication**: JWT-based authentication with role-based access control
- **MSP Endpoints**: Client management, health scores, churn prediction, upsell opportunities
- **IT Team Endpoints**: Software license tracking, cost anomaly detection, automated deactivation
- **Analytics**: Revenue trends, cost optimization, executive reports

## Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=pulseops
export DB_USER=postgres
export DB_PASSWORD=your_password
export SECRET_KEY=your-secret-key

# Run database migrations
alembic upgrade head

# Seed sample data
python seed_data.py
```

### Run Locally
```bash
# Development server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### MSP Features
- `GET /api/msp/dashboard` - MSP dashboard with key metrics
- `GET /api/msp/clients` - List all clients
- `POST /api/msp/clients` - Add new client
- `GET /api/msp/clients/{id}` - Get client details
- `GET /api/msp/clients/{id}/health-score` - Get detailed health score
- `GET /api/msp/recommendations` - Get AI recommendations

### IT Team Features
- `GET /api/it/dashboard` - IT dashboard with cost insights
- `GET /api/it/software` - List all software licenses
- `POST /api/it/software` - Add new software license
- `GET /api/it/software/{id}/usage` - Get detailed usage stats
- `GET /api/it/anomalies` - Get cost anomalies
- `POST /api/it/software/{id}/deactivate-unused` - Auto-deactivate unused licenses
- `GET /api/it/spend/department` - Department spend breakdown

### Analytics
- `GET /api/analytics/trends/revenue` - Revenue trends (MSP)
- `GET /api/analytics/trends/cost` - Cost trends (IT)
- `GET /api/analytics/reports/executive-summary` - Executive summary

## Test Credentials

After running `seed_data.py`:
- **MSP User**: demo-msp@example.com / password123
- **IT Admin**: demo-it@example.com / password123

## AWS Lambda Deployment

The application uses Mangum to make FastAPI compatible with AWS Lambda:

```python
from mangum import Mangum
handler = Mangum(app)
```

Deploy using AWS SAM:
```bash
sam build
sam deploy --guided
```