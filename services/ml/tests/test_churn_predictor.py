"""
Tests for churn prediction model
"""
import pytest
from models.churn_predictor import ChurnPredictor


def test_churn_predictor_initialization():
    """Test churn predictor can be initialized"""
    predictor = ChurnPredictor()
    assert predictor is not None
    assert predictor.model is not None


def test_predict_churn_low_risk(sample_features):
    """Test prediction for low churn risk client"""
    predictor = ChurnPredictor()
    
    # Modify features for low risk
    features = sample_features.copy()
    features["satisfaction_score"] = 4.8
    features["payment_delays"] = 0
    features["ticket_count"] = 5
    
    result = predictor.predict(1, features)
    
    assert "churn_probability" in result
    assert "churn_risk" in result
    assert result["churn_risk"] in ["low", "medium", "high"]
    assert 0 <= result["churn_probability"] <= 1


def test_predict_churn_high_risk(sample_features):
    """Test prediction for high churn risk client"""
    predictor = ChurnPredictor()
    
    # Modify features for high risk
    features = sample_features.copy()
    features["satisfaction_score"] = 2.0
    features["payment_delays"] = 5
    features["ticket_count"] = 50
    
    result = predictor.predict(1, features)
    
    assert result["churn_risk"] in ["medium", "high"]
    assert "risk_factors" in result


def test_predict_missing_features():
    """Test prediction with missing features"""
    predictor = ChurnPredictor()
    
    incomplete_features = {
        "monthly_revenue": 10000,
        "contract_length_days": 365
    }
    
    with pytest.raises((KeyError, ValueError)):
        predictor.predict(1, incomplete_features)


def test_feature_importance():
    """Test that feature importance is available"""
    predictor = ChurnPredictor()
    
    if hasattr(predictor.model, 'feature_importances_'):
        importances = predictor.model.feature_importances_
        assert len(importances) > 0
        assert all(0 <= imp <= 1 for imp in importances)
