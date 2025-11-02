"""
Churn Prediction Model
Predicts the probability of client churn using ML
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta

class ChurnPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'contract_value', 'monthly_spend', 'total_licenses', 'total_users',
            'days_since_last_ticket', 'support_ticket_frequency',
            'payment_history_score', 'contract_age_days', 'engagement_score'
        ]
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the churn prediction model"""
        model_path = os.path.join('trained_models', 'churn_model.pkl')
        
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            # Initialize a new model with default parameters
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            # Train with synthetic data for demo
            self._train_demo_model()
    
    def _train_demo_model(self):
        """Train model with synthetic data for demonstration"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Create features
        X = np.random.randn(n_samples, len(self.feature_names))
        
        # Create target (churn) based on some rules
        y = np.zeros(n_samples)
        
        # High churn probability if:
        # - Low engagement score
        # - High support ticket frequency
        # - Old contract with declining spend
        for i in range(n_samples):
            score = 0
            if X[i, 8] < -0.5:  # Low engagement
                score += 0.3
            if X[i, 5] > 0.5:  # High ticket frequency
                score += 0.3
            if X[i, 7] > 1.0 and X[i, 1] < 0:  # Old contract, low spend
                score += 0.4
            
            y[i] = 1 if score > 0.5 else 0
        
        # Fit scaler and model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        # Save model
        os.makedirs('trained_models', exist_ok=True)
        joblib.dump(self.model, os.path.join('trained_models', 'churn_model.pkl'))
        joblib.dump(self.scaler, os.path.join('trained_models', 'churn_scaler.pkl'))
    
    def predict(self, features):
        """
        Predict churn probability for a client
        
        Args:
            features (dict): Client features
            
        Returns:
            dict: Prediction results with probability and risk factors
        """
        # Extract and prepare features
        X = self._prepare_features(features)
        
        # Scale features
        X_scaled = self.scaler.transform(X.reshape(1, -1))
        
        # Get prediction probability
        churn_probability = self.model.predict_proba(X_scaled)[0][1]
        
        # Determine risk level
        if churn_probability < 0.3:
            risk_level = "low"
        elif churn_probability < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(features, X)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, risk_factors)
        
        return {
            "probability": float(churn_probability),
            "risk_level": risk_level,
            "factors": risk_factors,
            "recommendations": recommendations
        }
    
    def _prepare_features(self, features):
        """Prepare features for prediction"""
        feature_values = []
        
        # Extract features in the correct order
        feature_values.append(features.get('contract_value', 10000))
        feature_values.append(features.get('monthly_spend', 2000))
        feature_values.append(features.get('total_licenses', 50))
        feature_values.append(features.get('total_users', 100))
        
        # Calculate days since last support ticket
        last_ticket = features.get('last_support_ticket')
        if last_ticket:
            if isinstance(last_ticket, str):
                last_ticket = datetime.fromisoformat(last_ticket.replace('Z', '+00:00'))
            days_since = (datetime.utcnow() - last_ticket).days
        else:
            days_since = 365
        feature_values.append(days_since)
        
        # Support ticket frequency (estimated)
        feature_values.append(features.get('support_ticket_frequency', 0.1))
        
        # Payment history score (simulated)
        feature_values.append(features.get('payment_history_score', 0.8))
        
        # Contract age in days
        created_at = features.get('created_at', datetime.utcnow())
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        contract_age = (datetime.utcnow() - created_at).days
        feature_values.append(contract_age)
        
        # Engagement score (simulated)
        feature_values.append(features.get('engagement_score', 0.7))
        
        return np.array(feature_values)
    
    def _identify_risk_factors(self, features, X):
        """Identify key risk factors contributing to churn"""
        factors = []
        
        # Check various risk indicators
        if X[4] > 60:  # Days since last ticket
            factors.append({
                "factor": "Low engagement",
                "severity": "high",
                "description": f"No support tickets in {int(X[4])} days"
            })
        
        if X[5] > 0.5:  # High ticket frequency
            factors.append({
                "factor": "High support burden",
                "severity": "medium",
                "description": "Above average support ticket frequency"
            })
        
        if X[1] < features.get('contract_value', 10000) * 0.05:  # Low spend relative to contract
            factors.append({
                "factor": "Underutilization",
                "severity": "medium",
                "description": "Monthly spend much lower than contract value"
            })
        
        if X[8] < 0.5:  # Low engagement score
            factors.append({
                "factor": "Declining engagement",
                "severity": "high",
                "description": "User engagement trending downward"
            })
        
        return factors
    
    def _generate_recommendations(self, risk_level, risk_factors):
        """Generate actionable recommendations based on risk"""
        recommendations = []
        
        if risk_level == "high":
            recommendations.append("Schedule immediate check-in call with client")
            recommendations.append("Review service quality and address pain points")
            recommendations.append("Consider offering incentives or upgrades")
        
        elif risk_level == "medium":
            recommendations.append("Monitor engagement metrics closely")
            recommendations.append("Proactive outreach to ensure satisfaction")
        
        # Add specific recommendations based on factors
        for factor in risk_factors:
            if factor["factor"] == "Low engagement":
                recommendations.append("Increase touchpoints and engagement activities")
            elif factor["factor"] == "High support burden":
                recommendations.append("Provide additional training or documentation")
            elif factor["factor"] == "Underutilization":
                recommendations.append("Offer optimization consultation to increase value")
        
        return recommendations