"""
PulseOps AI - ML Service
Machine learning models for predictions and recommendations
"""

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import joblib
import os
from datetime import datetime

from models.churn_predictor import ChurnPredictor
from models.anomaly_detector import AnomalyDetector
from models.recommendation_engine import RecommendationEngine
from models.health_score_calculator import HealthScoreCalculator
from utils.feature_engineering import FeatureEngineer

app = Flask(__name__)
api = Api(app)

# Initialize ML models
churn_predictor = ChurnPredictor()
anomaly_detector = AnomalyDetector()
recommendation_engine = RecommendationEngine()
health_calculator = HealthScoreCalculator()
feature_engineer = FeatureEngineer()

@app.route('/')
def home():
    return jsonify({
        "service": "PulseOps ML Service",
        "status": "operational",
        "models": {
            "churn_predictor": "loaded",
            "anomaly_detector": "loaded",
            "recommendation_engine": "loaded",
            "health_calculator": "loaded"
        },
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

class ChurnPrediction(Resource):
    def post(self):
        """Predict client churn probability"""
        try:
            data = request.get_json()
            
            # Extract features
            features = feature_engineer.extract_client_features(data)
            
            # Make prediction
            result = churn_predictor.predict(features)
            
            return {
                "churn_probability": result["probability"],
                "churn_risk": result["risk_level"],
                "risk_factors": result["factors"],
                "recommendations": result["recommendations"]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 400

class AnomalyDetection(Resource):
    def post(self):
        """Detect cost anomalies in software spending"""
        try:
            data = request.get_json()
            
            # Extract time series data
            cost_data = data.get("cost_history", [])
            current_cost = data.get("current_cost")
            software_name = data.get("software_name")
            
            # Detect anomalies
            result = anomaly_detector.detect(cost_data, current_cost)
            
            return {
                "is_anomaly": result["is_anomaly"],
                "anomaly_score": result["score"],
                "expected_cost": result["expected_cost"],
                "actual_cost": current_cost,
                "variance_percent": result["variance_percent"],
                "severity": result["severity"],
                "explanation": result["explanation"]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 400

class HealthScoreCalculation(Resource):
    def post(self):
        """Calculate client health score"""
        try:
            data = request.get_json()
            
            # Calculate health score
            result = health_calculator.calculate(data)
            
            return {
                "health_score": result["overall_score"],
                "factors": result["factor_scores"],
                "trend": result["trend"],
                "insights": result["insights"]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 400

class RecommendationGeneration(Resource):
    def post(self):
        """Generate AI-powered recommendations"""
        try:
            data = request.get_json()
            user_role = data.get("role")  # 'msp' or 'it_admin'
            context = data.get("context", {})
            
            # Generate recommendations
            recommendations = recommendation_engine.generate(user_role, context)
            
            return {
                "recommendations": recommendations,
                "count": len(recommendations)
            }, 200
        except Exception as e:
            return {"error": str(e)}, 400

class UtilizationOptimization(Resource):
    def post(self):
        """Optimize license utilization and identify savings"""
        try:
            data = request.get_json()
            licenses = data.get("licenses", [])
            
            optimizations = []
            total_savings = 0
            
            for license in licenses:
                if license.get("utilization_percent", 100) < 50:
                    unused = license["total_licenses"] - license["active_users"]
                    cost_per_license = license["monthly_cost"] / license["total_licenses"]
                    potential_savings = unused * cost_per_license
                    
                    optimizations.append({
                        "software_name": license["software_name"],
                        "unused_licenses": unused,
                        "utilization_percent": license["utilization_percent"],
                        "potential_monthly_savings": potential_savings,
                        "potential_annual_savings": potential_savings * 12,
                        "recommendation": f"Deactivate {unused} unused licenses"
                    })
                    total_savings += potential_savings
            
            return {
                "optimizations": optimizations,
                "total_monthly_savings": total_savings,
                "total_annual_savings": total_savings * 12,
                "count": len(optimizations)
            }, 200
        except Exception as e:
            return {"error": str(e)}, 400

# Register API endpoints
api.add_resource(ChurnPrediction, '/api/predict/churn')
api.add_resource(AnomalyDetection, '/api/detect/anomaly')
api.add_resource(HealthScoreCalculation, '/api/calculate/health-score')
api.add_resource(RecommendationGeneration, '/api/generate/recommendations')
api.add_resource(UtilizationOptimization, '/api/optimize/utilization')

# Lambda handler for AWS Lambda deployment
def handler(event, context):
    """AWS Lambda handler"""
    from werkzeug.wrappers import Request, Response
    
    # Convert Lambda event to WSGI environ
    environ = {
        'REQUEST_METHOD': event.get('httpMethod', 'GET'),
        'SCRIPT_NAME': '',
        'PATH_INFO': event.get('path', '/'),
        'QUERY_STRING': event.get('queryStringParameters', {}),
        'SERVER_NAME': 'lambda',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': event.get('body', ''),
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Process request
    response = Response.from_app(app, environ)
    
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)