# PulseOps AI - ML Service

Machine Learning service for PulseOps AI platform.

## Features

### ML Models
- **Churn Predictor**: Predicts client churn probability using Gradient Boosting
- **Anomaly Detector**: Detects cost and usage anomalies using statistical methods
- **Health Score Calculator**: Calculates comprehensive client health scores
- **Recommendation Engine**: Generates AI-powered recommendations for MSPs and IT teams

### Capabilities
- Real-time predictions via REST API
- Feature engineering and data preprocessing
- Model training and evaluation
- AWS Lambda deployment support

## Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Train models with sample data
python train_models.py
```

### Run Locally
```bash
# Development server
python main.py

# Service will be available at http://localhost:5000
```

## API Endpoints

### Churn Prediction
```bash
POST /api/predict/churn
Content-Type: application/json

{
  "contract_value": 25000,
  "monthly_spend": 2000,
  "total_licenses": 100,
  "total_users": 80,
  "last_support_ticket": "2024-10-15",
  "support_ticket_frequency": 0.5,
  "payment_history_score": 0.85,
  "created_at": "2023-01-01",
  "engagement_score": 0.7
}
```

Response:
```json
{
  "churn_probability": 0.35,
  "churn_risk": "medium",
  "risk_factors": [...],
  "recommendations": [...]
}
```

### Anomaly Detection
```bash
POST /api/detect/anomaly
Content-Type: application/json

{
  "cost_history": [2500, 2600, 2450, 2550, 2500],
  "current_cost": 4200,
  "software_name": "AWS Services"
}
```

Response:
```json
{
  "is_anomaly": true,
  "anomaly_score": 0.85,
  "expected_cost": 2520,
  "actual_cost": 4200,
  "variance_percent": 66.7,
  "severity": "high",
  "explanation": "Cost is 66.7% higher than expected..."
}
```

### Health Score Calculation
```bash
POST /api/calculate/health-score
Content-Type: application/json

{
  "on_time_payments": 0.95,
  "support_tickets_per_month": 3,
  "total_licenses": 100,
  "total_users": 85,
  "contract_age_days": 365,
  "contract_value": 25000,
  "monthly_spend": 2000
}
```

Response:
```json
{
  "health_score": 82.5,
  "factors": {
    "payment_history": 95.0,
    "support_engagement": 87.5,
    "license_utilization": 85.0,
    ...
  },
  "trend": "improving",
  "insights": [...]
}
```

### Recommendation Generation
```bash
POST /api/generate/recommendations
Content-Type: application/json

{
  "role": "it_admin",
  "context": {
    "software_licenses": [...]
  }
}
```

### Utilization Optimization
```bash
POST /api/optimize/utilization
Content-Type: application/json

{
  "licenses": [
    {
      "software_name": "Adobe Creative Suite",
      "total_licenses": 50,
      "active_users": 20,
      "utilization_percent": 40,
      "monthly_cost": 2500
    }
  ]
}
```

## Model Training

Train models with your own data:

```python
from models.churn_predictor import ChurnPredictor
import pandas as pd

# Load your data
df = pd.read_csv('your_data.csv')

# Initialize predictor
predictor = ChurnPredictor()

# Train
X = df[feature_columns]
y = df['churned']
predictor.model.fit(X, y)

# Save
import joblib
joblib.dump(predictor.model, 'trained_models/churn_model.pkl')
```

## AWS Lambda Deployment

The service includes a Lambda handler for serverless deployment:

```python
# In main.py
def handler(event, context):
    # Lambda handler implementation
    ...
```

Deploy using SAM or Serverless Framework.

## Model Performance

### Churn Prediction Model
- Algorithm: Gradient Boosting Classifier
- Features: 9 key indicators
- Expected Accuracy: ~85%

### Anomaly Detection
- Method: Statistical Z-score analysis
- Threshold: 2.5 standard deviations
- False Positive Rate: <10%

## Architecture

```
ml/
├── main.py                      # Flask API server
├── train_models.py              # Model training script
├── models/
│   ├── churn_predictor.py      # Churn prediction
│   ├── anomaly_detector.py     # Anomaly detection
│   ├── health_score_calculator.py
│   └── recommendation_engine.py
├── utils/
│   └── feature_engineering.py  # Feature processing
└── trained_models/             # Saved model files
```