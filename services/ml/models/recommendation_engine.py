"""
Recommendation Engine
Generates intelligent recommendations for MSPs and IT teams
"""

import random
from datetime import datetime, timedelta

class RecommendationEngine:
    def __init__(self):
        self.msp_rules = self._initialize_msp_rules()
        self.it_rules = self._initialize_it_rules()
    
    def _initialize_msp_rules(self):
        """Initialize recommendation rules for MSPs"""
        return {
            'upsell': [
                {
                    'trigger': lambda c: c.get('health_score', 0) > 80 and c.get('contract_value', 0) < 50000,
                    'template': "Client {name} has high satisfaction. Consider upselling premium support or additional services.",
                    'value_multiplier': 0.3
                },
                {
                    'trigger': lambda c: c.get('license_utilization', 0) > 85,
                    'template': "Client {name} at {utilization}% license capacity. Recommend capacity expansion.",
                    'value_multiplier': 0.2
                }
            ],
            'retention': [
                {
                    'trigger': lambda c: c.get('churn_risk') == 'high',
                    'template': "URGENT: Client {name} at high churn risk. Schedule retention call immediately.",
                    'priority': 'high'
                },
                {
                    'trigger': lambda c: c.get('days_since_contact', 0) > 60,
                    'template': "Client {name} inactive for {days} days. Proactive outreach recommended.",
                    'priority': 'medium'
                }
            ],
            'optimization': [
                {
                    'trigger': lambda c: c.get('support_tickets_per_month', 0) > 10,
                    'template': "Client {name} has high ticket volume. Offer training or process optimization.",
                    'priority': 'medium'
                }
            ]
        }
    
    def _initialize_it_rules(self):
        """Initialize recommendation rules for IT teams"""
        return {
            'cost_saving': [
                {
                    'trigger': lambda s: s.get('utilization_percent', 100) < 50,
                    'template': "Software {name}: {unused} unused licenses. Potential monthly savings: ${savings}",
                    'calculate_value': lambda s: s.get('monthly_cost', 0) * (1 - s.get('utilization_percent', 50) / 100)
                },
                {
                    'trigger': lambda s: s.get('total_licenses', 0) > 100 and s.get('vendor') in ['Microsoft', 'Adobe', 'Salesforce'],
                    'template': "Software {name}: Large license pool. Negotiate enterprise discount with {vendor}.",
                    'calculate_value': lambda s: s.get('annual_cost', 0) * 0.15
                }
            ],
            'consolidation': [
                {
                    'trigger': lambda ctx: len(ctx.get('duplicate_tools', [])) > 0,
                    'template': "Overlapping functionality detected: {tools}. Consider consolidation.",
                    'calculate_value': lambda ctx: sum([t.get('cost', 0) for t in ctx.get('duplicate_tools', [])])
                }
            ],
            'renewal': [
                {
                    'trigger': lambda s: s.get('days_until_renewal', 365) < 60,
                    'template': "Software {name} renewal in {days} days. Negotiate or review alternatives.",
                    'priority': 'high'
                }
            ]
        }
    
    def generate(self, role, context):
        """
        Generate recommendations based on role and context
        
        Args:
            role (str): 'msp' or 'it_admin'
            context (dict): Context data for recommendations
            
        Returns:
            list: List of recommendations
        """
        if role == 'msp':
            return self._generate_msp_recommendations(context)
        elif role == 'it_admin':
            return self._generate_it_recommendations(context)
        else:
            return []
    
    def _generate_msp_recommendations(self, context):
        """Generate MSP-specific recommendations"""
        recommendations = []
        clients = context.get('clients', [])
        
        for client in clients:
            # Check upsell opportunities
            for rule in self.msp_rules['upsell']:
                if rule['trigger'](client):
                    potential_value = client.get('monthly_spend', 0) * 12 * rule.get('value_multiplier', 0.2)
                    recommendations.append({
                        'type': 'upsell',
                        'title': f"Upsell Opportunity: {client.get('name')}",
                        'description': rule['template'].format(
                            name=client.get('name'),
                            utilization=client.get('license_utilization', 0)
                        ),
                        'potential_value': potential_value,
                        'priority': 'medium',
                        'client_id': client.get('client_id')
                    })
            
            # Check retention needs
            for rule in self.msp_rules['retention']:
                if rule['trigger'](client):
                    recommendations.append({
                        'type': 'churn_prevention',
                        'title': f"Retention Alert: {client.get('name')}",
                        'description': rule['template'].format(
                            name=client.get('name'),
                            days=client.get('days_since_contact', 0)
                        ),
                        'potential_value': client.get('contract_value', 0),
                        'priority': rule.get('priority', 'high'),
                        'client_id': client.get('client_id')
                    })
            
            # Check optimization opportunities
            for rule in self.msp_rules['optimization']:
                if rule['trigger'](client):
                    recommendations.append({
                        'type': 'optimization',
                        'title': f"Service Optimization: {client.get('name')}",
                        'description': rule['template'].format(
                            name=client.get('name')
                        ),
                        'potential_value': client.get('monthly_spend', 0) * 0.1,
                        'priority': rule.get('priority', 'medium'),
                        'client_id': client.get('client_id')
                    })
        
        # Sort by priority and value
        recommendations.sort(key=lambda x: (
            {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 2),
            -x.get('potential_value', 0)
        ))
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _generate_it_recommendations(self, context):
        """Generate IT admin-specific recommendations"""
        recommendations = []
        software_licenses = context.get('software_licenses', [])
        
        for software in software_licenses:
            # Check cost saving opportunities
            for rule in self.it_rules['cost_saving']:
                if rule['trigger'](software):
                    potential_value = rule['calculate_value'](software)
                    unused_licenses = software.get('total_licenses', 0) - software.get('active_users', 0)
                    
                    recommendations.append({
                        'type': 'cost_saving',
                        'title': f"Cost Savings: {software.get('software_name')}",
                        'description': rule['template'].format(
                            name=software.get('software_name'),
                            unused=unused_licenses,
                            savings=f"{potential_value:.2f}",
                            vendor=software.get('vendor', 'vendor')
                        ),
                        'potential_value': potential_value,
                        'priority': 'high' if potential_value > 1000 else 'medium',
                        'software_id': software.get('id')
                    })
            
            # Check renewal opportunities
            renewal_date = software.get('renewal_date')
            if renewal_date:
                if isinstance(renewal_date, str):
                    renewal_date = datetime.fromisoformat(renewal_date.replace('Z', '+00:00'))
                days_until = (renewal_date - datetime.utcnow()).days
                
                if 0 < days_until < 60:
                    for rule in self.it_rules['renewal']:
                        if rule['trigger']({'days_until_renewal': days_until}):
                            recommendations.append({
                                'type': 'renewal',
                                'title': f"Upcoming Renewal: {software.get('software_name')}",
                                'description': rule['template'].format(
                                    name=software.get('software_name'),
                                    days=days_until
                                ),
                                'potential_value': software.get('annual_cost', 0) * 0.1,
                                'priority': 'high' if days_until < 30 else 'medium',
                                'software_id': software.get('id')
                            })
        
        # Check for consolidation opportunities
        duplicate_tools = self._find_duplicate_tools(software_licenses)
        if duplicate_tools:
            for category, tools in duplicate_tools.items():
                if len(tools) > 1:
                    total_cost = sum(t.get('monthly_cost', 0) for t in tools)
                    recommendations.append({
                        'type': 'consolidation',
                        'title': f"Consolidation Opportunity: {category}",
                        'description': f"Multiple {category} tools detected: {', '.join([t.get('software_name') for t in tools])}. Consider consolidation.",
                        'potential_value': total_cost * 0.3,  # Assume 30% savings
                        'priority': 'medium'
                    })
        
        # Sort by priority and value
        recommendations.sort(key=lambda x: (
            {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 2),
            -x.get('potential_value', 0)
        ))
        
        return recommendations[:15]  # Top 15 recommendations
    
    def _find_duplicate_tools(self, software_licenses):
        """Find duplicate or overlapping software tools"""
        categories = {
            'Communication': ['Slack', 'Teams', 'Zoom', 'Google Meet'],
            'Productivity': ['Microsoft 365', 'Google Workspace', 'Notion'],
            'Project Management': ['Jira', 'Asana', 'Monday.com', 'Trello'],
            'CRM': ['Salesforce', 'HubSpot', 'Zoho'],
            'Analytics': ['Tableau', 'Power BI', 'Looker']
        }
        
        duplicates = {}
        
        for category, keywords in categories.items():
            matching_tools = [
                s for s in software_licenses
                if any(kw.lower() in s.get('software_name', '').lower() for kw in keywords)
            ]
            if len(matching_tools) > 1:
                duplicates[category] = matching_tools
        
        return duplicates