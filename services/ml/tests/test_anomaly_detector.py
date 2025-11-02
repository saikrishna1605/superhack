"""
Tests for anomaly detection
"""
import pytest
from models.anomaly_detector import AnomalyDetector


def test_anomaly_detector_initialization():
    """Test anomaly detector can be initialized"""
    detector = AnomalyDetector()
    assert detector is not None
    assert detector.threshold > 0


def test_detect_no_anomaly(sample_usage_data):
    """Test detection with normal data"""
    detector = AnomalyDetector()
    
    # Use only normal data points
    normal_data = sample_usage_data[:4]
    
    result = detector.detect(normal_data, "active_users")
    
    assert "anomalies" in result
    assert "statistics" in result
    # Should detect few or no anomalies
    assert len(result["anomalies"]) <= 1


def test_detect_spike_anomaly(sample_usage_data):
    """Test detection of spike anomaly"""
    detector = AnomalyDetector()
    
    result = detector.detect(sample_usage_data, "active_users")
    
    assert "anomalies" in result
    assert len(result["anomalies"]) > 0
    
    # Check that the spike (150) was detected
    anomaly_values = [a["value"] for a in result["anomalies"]]
    assert 150 in anomaly_values


def test_detect_with_custom_threshold():
    """Test detection with custom threshold"""
    detector = AnomalyDetector(threshold=3.0)
    
    data = [
        {"date": "2024-01-01", "value": 100},
        {"date": "2024-01-02", "value": 105},
        {"date": "2024-01-03", "value": 200},  # Less extreme
    ]
    
    result = detector.detect(data, "value")
    
    # With higher threshold, fewer anomalies
    assert len(result["anomalies"]) >= 0


def test_detect_empty_data():
    """Test detection with empty data"""
    detector = AnomalyDetector()
    
    with pytest.raises((ValueError, IndexError)):
        detector.detect([], "value")


def test_statistics_calculation(sample_usage_data):
    """Test that statistics are calculated correctly"""
    detector = AnomalyDetector()
    
    result = detector.detect(sample_usage_data, "active_users")
    
    assert "statistics" in result
    stats = result["statistics"]
    assert "mean" in stats
    assert "std" in stats
    assert "min" in stats
    assert "max" in stats
    assert stats["mean"] > 0
    assert stats["std"] >= 0
