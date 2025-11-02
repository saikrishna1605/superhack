"""
Test configuration for ML service
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_features():
    """Sample feature data for testing"""
    return {
        "monthly_revenue": 25000,
        "contract_length_days": 730,
        "ticket_count": 15,
        "avg_response_time": 3.5,
        "satisfaction_score": 4.2,
        "license_utilization": 85,
        "support_incidents": 8,
        "payment_delays": 0,
        "contract_changes": 2
    }


@pytest.fixture
def sample_usage_data():
    """Sample usage data for testing"""
    return [
        {"usage_date": "2024-01-01", "active_users": 80},
        {"usage_date": "2024-01-02", "active_users": 82},
        {"usage_date": "2024-01-03", "active_users": 85},
        {"usage_date": "2024-01-04", "active_users": 78},
        {"usage_date": "2024-01-05", "active_users": 150},  # Anomaly
    ]
