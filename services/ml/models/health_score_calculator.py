"""
Health Score Calculator
Calculates comprehensive health scores for clients
"""

import numpy as np
from datetime import datetime, timedelta

class HealthScoreCalculator:
    def __init__(self):
        # Weight for each health factor
        self.weights = {
            'payment_history': 0.25,
            'support_engagement': 0.20,
            'license_utilization': 0.20,
            'contract_stability': 0.15,
            'feature_adoption': 0.10,
            'communication_frequency': 0.10
        }
    
    def calculate(self, client_data):
        """
        Calculate overall health score and factor breakdown
        
        Args:
            client_data (dict): Client information and metrics
            
        Returns:
            dict: Health score results with factor breakdown
        """
        # Calculate individual factor scores
        factor_scores = {}
        
        factor_scores['payment_history'] = self._calculate_payment_score(client_data)
        factor_scores['support_engagement'] = self._calculate_support_score(client_data)
        factor_scores['license_utilization'] = self._calculate_utilization_score(client_data)
        factor_scores['contract_stability'] = self._calculate_contract_score(client_data)
        factor_scores['feature_adoption'] = self._calculate_adoption_score(client_data)
        factor_scores['communication_frequency'] = self._calculate_communication_score(client_data)
        
        # Calculate weighted overall score
        overall_score = sum(
            factor_scores[factor] * self.weights[factor]
            for factor in self.weights
        )
        
        # Determine trend
        trend = self._calculate_trend(client_data, factor_scores)
        
        # Generate insights
        insights = self._generate_insights(factor_scores, overall_score)
        
        return {
            "overall_score": float(overall_score),
            "factor_scores": {k: float(v) for k, v in factor_scores.items()},
            "trend": trend,
            "insights": insights,
            "health_status": self._get_health_status(overall_score)
        }
    
    def _calculate_payment_score(self, data):
        """Calculate payment history score (0-100)"""
        # Simulated based on payment timeliness and history
        on_time_payments = data.get('on_time_payments', 0.95)
        payment_history_months = data.get('payment_history_months', 12)
        
        base_score = on_time_payments * 100
        
        # Bonus for long payment history
        history_bonus = min(payment_history_months / 24 * 10, 10)
        
        return min(base_score + history_bonus, 100)
    
    def _calculate_support_score(self, data):
        """Calculate support engagement score (0-100)"""
        # Moderate support tickets are good (shows engagement)
        # Too many or too few is concerning
        
        tickets_per_month = data.get('support_tickets_per_month', 2)
        avg_resolution_time = data.get('avg_resolution_time_days', 2)
        satisfaction_score = data.get('support_satisfaction', 0.85)
        
        # Optimal ticket frequency is 1-4 per month
        if 1 <= tickets_per_month <= 4:
            frequency_score = 100
        elif tickets_per_month < 1:
            frequency_score = 70  # Low engagement
        elif tickets_per_month > 8:
            frequency_score = 60  # Too many issues
        else:
            frequency_score = 85
        
        # Resolution time score
        resolution_score = max(0, 100 - (avg_resolution_time * 10))
        
        # Combined score
        return (frequency_score * 0.3 + resolution_score * 0.3 + satisfaction_score * 100 * 0.4)
    
    def _calculate_utilization_score(self, data):
        """Calculate license utilization score (0-100)"""
        total_licenses = data.get('total_licenses', 50)
        active_users = data.get('total_users', 40)
        
        if total_licenses == 0:
            return 50
        
        utilization = (active_users / total_licenses) * 100
        
        # Optimal utilization is 70-90%
        if 70 <= utilization <= 90:
            return 100
        elif 60 <= utilization < 70 or 90 < utilization <= 95:
            return 85
        elif utilization > 95:
            return 75  # Over-capacity might indicate need for upgrade
        else:
            return max(0, utilization)
    
    def _calculate_contract_score(self, data):
        """Calculate contract stability score (0-100)"""
        contract_age_days = data.get('contract_age_days', 365)
        contract_value = data.get('contract_value', 10000)
        monthly_spend = data.get('monthly_spend', 2000)
        
        # Longer contracts are more stable
        age_score = min(contract_age_days / 730 * 100, 100)  # 2 years = max
        
        # Spending close to contract value indicates commitment
        if contract_value > 0:
            spend_ratio = (monthly_spend * 12) / contract_value
            spend_score = min(spend_ratio * 100, 100)
        else:
            spend_score = 50
        
        return (age_score * 0.5 + spend_score * 0.5)
    
    def _calculate_adoption_score(self, data):
        """Calculate feature adoption score (0-100)"""
        # Based on features used vs available
        features_used = data.get('features_used', 8)
        features_available = data.get('features_available', 15)
        
        if features_available == 0:
            return 50
        
        adoption_rate = (features_used / features_available) * 100
        
        # Good adoption is 50%+
        if adoption_rate >= 70:
            return 100
        elif adoption_rate >= 50:
            return 85
        else:
            return max(adoption_rate, 30)
    
    def _calculate_communication_score(self, data):
        """Calculate communication frequency score (0-100)"""
        days_since_last_contact = data.get('days_since_last_contact', 30)
        
        # Optimal contact is within 30 days
        if days_since_last_contact <= 14:
            return 100
        elif days_since_last_contact <= 30:
            return 85
        elif days_since_last_contact <= 60:
            return 70
        elif days_since_last_contact <= 90:
            return 50
        else:
            return max(0, 100 - days_since_last_contact)
    
    def _calculate_trend(self, data, factor_scores):
        """Determine if health is improving or declining"""
        # Compare with historical data if available
        previous_score = data.get('previous_health_score')
        current_score = sum(
            factor_scores[factor] * self.weights[factor]
            for factor in self.weights
        )
        
        if previous_score:
            if current_score > previous_score + 5:
                return "improving"
            elif current_score < previous_score - 5:
                return "declining"
        
        return "stable"
    
    def _generate_insights(self, factor_scores, overall_score):
        """Generate actionable insights based on scores"""
        insights = []
        
        # Identify weak areas
        weak_factors = [(factor, score) for factor, score in factor_scores.items() if score < 70]
        weak_factors.sort(key=lambda x: x[1])
        
        for factor, score in weak_factors[:3]:  # Top 3 concerns
            if factor == 'payment_history':
                insights.append("Payment history needs attention. Consider automated payment reminders.")
            elif factor == 'support_engagement':
                insights.append("Support engagement could be improved. Proactive check-ins recommended.")
            elif factor == 'license_utilization':
                insights.append("Low license utilization detected. Consider optimization or training.")
            elif factor == 'contract_stability':
                insights.append("Contract stability at risk. Review and strengthen engagement.")
            elif factor == 'feature_adoption':
                insights.append("Low feature adoption. Provide training on available features.")
            elif factor == 'communication_frequency':
                insights.append("Communication gaps detected. Increase touchpoint frequency.")
        
        # Identify strengths
        strong_factors = [(factor, score) for factor, score in factor_scores.items() if score >= 90]
        if strong_factors:
            insights.append(f"Strong performance in: {', '.join([f[0] for f in strong_factors])}")
        
        # Overall health insight
        if overall_score >= 85:
            insights.append("Client is healthy and engaged. Consider upsell opportunities.")
        elif overall_score < 60:
            insights.append("Client health is concerning. Immediate intervention recommended.")
        
        return insights
    
    def _get_health_status(self, score):
        """Get health status label"""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "at_risk"