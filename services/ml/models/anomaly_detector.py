"""
Anomaly Detection Model
Detects unusual patterns in cost and usage data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import joblib
import os

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.trained = False
    
    def detect(self, historical_costs, current_cost):
        """
        Detect if current cost is anomalous compared to historical data
        
        Args:
            historical_costs (list): List of historical cost values
            current_cost (float): Current cost to check
            
        Returns:
            dict: Anomaly detection results
        """
        if not historical_costs or len(historical_costs) < 3:
            # Not enough data for anomaly detection
            return self._simple_threshold_check(historical_costs, current_cost)
        
        # Convert to numpy array
        costs = np.array(historical_costs)
        
        # Calculate statistical measures
        mean_cost = np.mean(costs)
        std_cost = np.std(costs)
        median_cost = np.median(costs)
        
        # Calculate expected cost using exponential moving average
        alpha = 0.3
        ema_cost = costs[-1]
        for i in range(len(costs) - 2, -1, -1):
            ema_cost = alpha * costs[i] + (1 - alpha) * ema_cost
        
        # Use statistical approach for anomaly detection
        z_score = abs((current_cost - mean_cost) / std_cost) if std_cost > 0 else 0
        
        # Check if anomaly using z-score
        is_anomaly = z_score > 2.5  # 2.5 standard deviations
        
        # Calculate variance
        variance_percent = ((current_cost - mean_cost) / mean_cost * 100) if mean_cost > 0 else 0
        
        # Determine severity
        if abs(variance_percent) > 50:
            severity = "high"
        elif abs(variance_percent) > 25:
            severity = "medium"
        else:
            severity = "low"
        
        # Generate explanation
        if is_anomaly:
            if current_cost > mean_cost:
                explanation = f"Cost is {abs(variance_percent):.1f}% higher than expected. Possible causes: increased usage, new features, or billing errors."
            else:
                explanation = f"Cost is {abs(variance_percent):.1f}% lower than expected. Possible causes: decreased usage or service disruption."
        else:
            explanation = "Cost is within normal range."
        
        # Calculate anomaly score (0-1, higher = more anomalous)
        anomaly_score = min(z_score / 5.0, 1.0)  # Normalize to 0-1
        
        return {
            "is_anomaly": is_anomaly,
            "score": float(anomaly_score),
            "expected_cost": float(mean_cost),
            "variance_percent": float(variance_percent),
            "severity": severity,
            "explanation": explanation,
            "statistics": {
                "mean": float(mean_cost),
                "median": float(median_cost),
                "std_dev": float(std_cost),
                "z_score": float(z_score)
            }
        }
    
    def _simple_threshold_check(self, historical_costs, current_cost):
        """Simple threshold-based check when insufficient data"""
        if not historical_costs:
            return {
                "is_anomaly": False,
                "score": 0.0,
                "expected_cost": current_cost,
                "variance_percent": 0.0,
                "severity": "low",
                "explanation": "Insufficient historical data for anomaly detection"
            }
        
        mean_cost = np.mean(historical_costs)
        variance_percent = ((current_cost - mean_cost) / mean_cost * 100) if mean_cost > 0 else 0
        
        is_anomaly = abs(variance_percent) > 30
        severity = "high" if abs(variance_percent) > 50 else "medium" if abs(variance_percent) > 30 else "low"
        
        return {
            "is_anomaly": is_anomaly,
            "score": min(abs(variance_percent) / 100, 1.0),
            "expected_cost": float(mean_cost),
            "variance_percent": float(variance_percent),
            "severity": severity,
            "explanation": f"Limited data available. Current cost differs by {abs(variance_percent):.1f}%"
        }
    
    def detect_usage_anomaly(self, usage_data):
        """
        Detect anomalies in license usage patterns
        
        Args:
            usage_data (list): List of usage records with timestamps
            
        Returns:
            dict: Usage anomaly results
        """
        if len(usage_data) < 5:
            return {"is_anomaly": False, "message": "Insufficient data"}
        
        # Extract usage hours
        usage_hours = [u.get('usage_hours', 0) for u in usage_data]
        
        # Calculate statistics
        mean_usage = np.mean(usage_hours)
        std_usage = np.std(usage_hours)
        
        # Find users with anomalous usage
        anomalous_users = []
        for record in usage_data:
            usage = record.get('usage_hours', 0)
            z_score = abs((usage - mean_usage) / std_usage) if std_usage > 0 else 0
            
            if z_score > 2.0:
                anomalous_users.append({
                    "user_email": record.get('user_email'),
                    "usage_hours": usage,
                    "expected_usage": mean_usage,
                    "deviation": z_score
                })
        
        return {
            "is_anomaly": len(anomalous_users) > 0,
            "anomalous_users": anomalous_users,
            "avg_usage": float(mean_usage),
            "std_usage": float(std_usage)
        }
    
    def detect_trend_anomaly(self, time_series_data):
        """
        Detect anomalous trends in time series data
        
        Args:
            time_series_data (list): Time series of values
            
        Returns:
            dict: Trend anomaly detection results
        """
        if len(time_series_data) < 7:
            return {"has_anomaly": False, "message": "Insufficient data for trend analysis"}
        
        # Convert to numpy array
        data = np.array(time_series_data)
        
        # Calculate moving average
        window = min(7, len(data) // 2)
        moving_avg = np.convolve(data, np.ones(window)/window, mode='valid')
        
        # Detect sudden spikes or drops
        if len(data) > 1:
            daily_changes = np.diff(data)
            mean_change = np.mean(daily_changes)
            std_change = np.std(daily_changes)
            
            # Find significant changes
            significant_changes = []
            for i, change in enumerate(daily_changes):
                z_score = abs((change - mean_change) / std_change) if std_change > 0 else 0
                if z_score > 2.5:
                    significant_changes.append({
                        "day": i + 1,
                        "change_percent": float((change / data[i] * 100) if data[i] != 0 else 0),
                        "severity": "high" if z_score > 3 else "medium"
                    })
            
            return {
                "has_anomaly": len(significant_changes) > 0,
                "significant_changes": significant_changes,
                "trend": "increasing" if mean_change > 0 else "decreasing",
                "avg_daily_change": float(mean_change)
            }
        
        return {"has_anomaly": False, "message": "Normal trend detected"}