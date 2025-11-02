"""
Feature Engineering Utilities
Prepare and transform data for ML models
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class FeatureEngineer:
    def __init__(self):
        pass
    
    def extract_client_features(self, client_data):
        """
        Extract features from client data for ML models
        
        Args:
            client_data (dict): Raw client data
            
        Returns:
            dict: Engineered features
        """
        features = {}
        
        # Basic features
        features['contract_value'] = client_data.get('contract_value', 0)
        features['monthly_spend'] = client_data.get('monthly_spend', 0)
        features['total_licenses'] = client_data.get('total_licenses', 0)
        features['total_users'] = client_data.get('total_users', 0)
        
        # Derived features
        if features['contract_value'] > 0:
            features['spend_ratio'] = features['monthly_spend'] * 12 / features['contract_value']
        else:
            features['spend_ratio'] = 0
        
        if features['total_licenses'] > 0:
            features['user_to_license_ratio'] = features['total_users'] / features['total_licenses']
        else:
            features['user_to_license_ratio'] = 0
        
        # Time-based features
        created_at = client_data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            features['contract_age_days'] = (datetime.utcnow() - created_at).days
            features['contract_age_months'] = features['contract_age_days'] / 30
        else:
            features['contract_age_days'] = 0
            features['contract_age_months'] = 0
        
        last_ticket = client_data.get('last_support_ticket')
        if last_ticket:
            if isinstance(last_ticket, str):
                last_ticket = datetime.fromisoformat(last_ticket.replace('Z', '+00:00'))
            features['days_since_last_ticket'] = (datetime.utcnow() - last_ticket).days
        else:
            features['days_since_last_ticket'] = 365
        
        # Engagement features
        features['support_ticket_frequency'] = client_data.get('support_ticket_frequency', 0)
        features['engagement_score'] = client_data.get('engagement_score', 0.5)
        features['payment_history_score'] = client_data.get('payment_history_score', 0.8)
        
        # Health score
        features['health_score'] = client_data.get('health_score', 70)
        
        return features
    
    def extract_software_features(self, software_data):
        """
        Extract features from software license data
        
        Args:
            software_data (dict): Raw software data
            
        Returns:
            dict: Engineered features
        """
        features = {}
        
        # Basic features
        features['total_licenses'] = software_data.get('total_licenses', 0)
        features['active_users'] = software_data.get('active_users', 0)
        features['monthly_cost'] = software_data.get('monthly_cost', 0)
        features['annual_cost'] = software_data.get('annual_cost', 0)
        
        # Utilization features
        if features['total_licenses'] > 0:
            features['utilization_percent'] = (features['active_users'] / features['total_licenses']) * 100
            features['unused_licenses'] = features['total_licenses'] - features['active_users']
            features['cost_per_license'] = features['monthly_cost'] / features['total_licenses']
        else:
            features['utilization_percent'] = 0
            features['unused_licenses'] = 0
            features['cost_per_license'] = 0
        
        # Waste calculation
        features['wasted_licenses'] = max(0, features['unused_licenses'])
        features['wasted_cost'] = features['wasted_licenses'] * features.get('cost_per_license', 0)
        
        # Time-based features
        renewal_date = software_data.get('renewal_date')
        if renewal_date:
            if isinstance(renewal_date, str):
                renewal_date = datetime.fromisoformat(renewal_date.replace('Z', '+00:00'))
            features['days_until_renewal'] = max(0, (renewal_date - datetime.utcnow()).days)
        else:
            features['days_until_renewal'] = 365
        
        return features
    
    def create_time_series_features(self, time_series_data, window=7):
        """
        Create features from time series data
        
        Args:
            time_series_data (list): Time series values
            window (int): Rolling window size
            
        Returns:
            dict: Time series features
        """
        if not time_series_data or len(time_series_data) == 0:
            return {}
        
        data = np.array(time_series_data)
        
        features = {
            'mean': float(np.mean(data)),
            'median': float(np.median(data)),
            'std': float(np.std(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'range': float(np.max(data) - np.min(data))
        }
        
        # Trend features
        if len(data) > 1:
            features['trend'] = float(np.polyfit(range(len(data)), data, 1)[0])
            features['last_value'] = float(data[-1])
            features['first_value'] = float(data[0])
            features['change_percent'] = float(((data[-1] - data[0]) / data[0] * 100) if data[0] != 0 else 0)
        
        # Rolling features
        if len(data) >= window:
            rolling_mean = np.convolve(data, np.ones(window)/window, mode='valid')
            features['rolling_mean'] = float(rolling_mean[-1])
            features['rolling_std'] = float(np.std(data[-window:]))
        
        return features
    
    def normalize_features(self, features_dict):
        """
        Normalize feature values to 0-1 range
        
        Args:
            features_dict (dict): Raw features
            
        Returns:
            dict: Normalized features
        """
        normalized = {}
        
        # Define normalization ranges for common features
        ranges = {
            'contract_value': (0, 100000),
            'monthly_spend': (0, 10000),
            'total_licenses': (0, 500),
            'total_users': (0, 1000),
            'health_score': (0, 100),
            'utilization_percent': (0, 100),
            'days_since_last_ticket': (0, 365)
        }
        
        for key, value in features_dict.items():
            if key in ranges:
                min_val, max_val = ranges[key]
                normalized[key] = min(max((value - min_val) / (max_val - min_val), 0), 1)
            else:
                normalized[key] = value
        
        return normalized
    
    def create_aggregate_features(self, items_list, group_by_field='department'):
        """
        Create aggregate features from multiple items
        
        Args:
            items_list (list): List of items to aggregate
            group_by_field (str): Field to group by
            
        Returns:
            dict: Aggregate features by group
        """
        if not items_list:
            return {}
        
        df = pd.DataFrame(items_list)
        
        if group_by_field not in df.columns:
            return {}
        
        aggregates = {}
        
        for group_name, group_data in df.groupby(group_by_field):
            aggregates[group_name] = {
                'count': len(group_data),
                'total_cost': float(group_data.get('monthly_cost', pd.Series([0])).sum()),
                'avg_utilization': float(group_data.get('utilization_percent', pd.Series([0])).mean()),
                'total_licenses': int(group_data.get('total_licenses', pd.Series([0])).sum())
            }
        
        return aggregates