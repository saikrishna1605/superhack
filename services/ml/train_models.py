"""
Training script for ML models
Run this to train or retrain models with actual data
"""

import sys
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.churn_predictor import ChurnPredictor
from models.anomaly_detector import AnomalyDetector

def generate_synthetic_training_data(n_samples=1000):
    """Generate synthetic data for model training"""
    print(f"Generating {n_samples} synthetic training samples...")
    
    np.random.seed(42)
    
    # Generate client features
    data = {
        'contract_value': np.random.uniform(5000, 100000, n_samples),
        'monthly_spend': np.random.uniform(500, 10000, n_samples),
        'total_licenses': np.random.randint(10, 500, n_samples),
        'total_users': np.random.randint(10, 1000, n_samples),
        'days_since_last_ticket': np.random.randint(1, 365, n_samples),
        'support_ticket_frequency': np.random.uniform(0, 1, n_samples),
        'payment_history_score': np.random.uniform(0.5, 1.0, n_samples),
        'contract_age_days': np.random.randint(30, 1095, n_samples),
        'engagement_score': np.random.uniform(0.2, 1.0, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate churn labels based on business logic
    churn = np.zeros(n_samples)
    for i in range(n_samples):
        churn_score = 0
        
        # Low engagement increases churn risk
        if df.loc[i, 'engagement_score'] < 0.4:
            churn_score += 0.4
        
        # High support tickets increase churn risk
        if df.loc[i, 'support_ticket_frequency'] > 0.7:
            churn_score += 0.3
        
        # Low payment history increases churn risk
        if df.loc[i, 'payment_history_score'] < 0.7:
            churn_score += 0.3
        
        # No recent contact increases churn risk
        if df.loc[i, 'days_since_last_ticket'] > 180:
            churn_score += 0.3
        
        # Low spend relative to contract value
        spend_ratio = (df.loc[i, 'monthly_spend'] * 12) / df.loc[i, 'contract_value']
        if spend_ratio < 0.5:
            churn_score += 0.2
        
        churn[i] = 1 if churn_score > 0.6 else 0
    
    df['churned'] = churn
    
    return df

def train_churn_model():
    """Train the churn prediction model"""
    print("\n=== Training Churn Prediction Model ===")
    
    # Generate training data
    df = generate_synthetic_training_data(1500)
    
    # Split features and target
    feature_cols = ['contract_value', 'monthly_spend', 'total_licenses', 'total_users',
                    'days_since_last_ticket', 'support_ticket_frequency',
                    'payment_history_score', 'contract_age_days', 'engagement_score']
    
    X = df[feature_cols].values
    y = df['churned'].values
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    predictor = ChurnPredictor()
    
    # Fit scaler
    X_train_scaled = predictor.scaler.fit_transform(X_train)
    X_test_scaled = predictor.scaler.transform(X_test)
    
    # Train model
    predictor.model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = predictor.model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Churn', 'Churn']))
    
    # Save model
    os.makedirs('trained_models', exist_ok=True)
    joblib.dump(predictor.model, 'trained_models/churn_model.pkl')
    joblib.dump(predictor.scaler, 'trained_models/churn_scaler.pkl')
    
    print("\n✅ Churn model trained and saved!")
    
    # Feature importance
    if hasattr(predictor.model, 'feature_importances_'):
        importances = predictor.model.feature_importances_
        feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
        
        print("\nFeature Importance:")
        for feature, importance in feature_importance[:5]:
            print(f"  {feature}: {importance:.4f}")

def test_models():
    """Test the trained models with sample data"""
    print("\n=== Testing Trained Models ===")
    
    # Test churn predictor
    predictor = ChurnPredictor()
    
    test_client = {
        'contract_value': 25000,
        'monthly_spend': 1000,
        'total_licenses': 100,
        'total_users': 60,
        'last_support_ticket': '2024-08-15',
        'support_ticket_frequency': 0.8,
        'payment_history_score': 0.6,
        'created_at': '2023-01-01',
        'engagement_score': 0.3
    }
    
    result = predictor.predict(test_client)
    
    print("\nChurn Prediction Test:")
    print(f"  Churn Probability: {result['probability']:.3f}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Risk Factors: {len(result['factors'])}")
    print(f"  Recommendations: {len(result['recommendations'])}")
    
    # Test anomaly detector
    detector = AnomalyDetector()
    
    historical_costs = [2500, 2600, 2450, 2550, 2500, 2600, 2500]
    current_cost = 4200
    
    anomaly_result = detector.detect(historical_costs, current_cost)
    
    print("\nAnomaly Detection Test:")
    print(f"  Is Anomaly: {anomaly_result['is_anomaly']}")
    print(f"  Severity: {anomaly_result['severity']}")
    print(f"  Variance: {anomaly_result['variance_percent']:.1f}%")
    
    print("\n✅ Model testing complete!")

if __name__ == '__main__':
    print("PulseOps AI - Model Training Script")
    print("=" * 50)
    
    # Train models
    train_churn_model()
    
    # Test models
    test_models()
    
    print("\n" + "=" * 50)
    print("Training complete! Models are ready for deployment.")
