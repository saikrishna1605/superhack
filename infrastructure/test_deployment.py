#!/usr/bin/env python3
"""
Test AWS Deployment
Validates that all services are running correctly
"""

import requests
import json
import sys
import argparse
from datetime import datetime

class DeploymentTester:
    def __init__(self, api_url, ml_url, ui_url):
        self.api_url = api_url.rstrip('/')
        self.ml_url = ml_url.rstrip('/')
        self.ui_url = ui_url.rstrip('/')
        self.token = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    def print_result(self, test_name, passed, message=""):
        if passed:
            print(f"  ✅ {test_name}")
            self.tests_passed += 1
        else:
            print(f"  ❌ {test_name}")
            if message:
                print(f"     Error: {message}")
            self.tests_failed += 1
    
    def test_api_health(self):
        """Test API health endpoint"""
        print("\n🔍 Testing API Service...")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            passed = response.status_code == 200
            self.print_result("API health check", passed, 
                            f"Status: {response.status_code}" if not passed else "")
            
            if passed:
                data = response.json()
                print(f"     Status: {data.get('status')}")
                print(f"     Timestamp: {data.get('timestamp')}")
            
            return passed
        except Exception as e:
            self.print_result("API health check", False, str(e))
            return False
    
    def test_api_docs(self):
        """Test API documentation"""
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=10)
            passed = response.status_code == 200
            self.print_result("API docs accessible", passed)
            return passed
        except Exception as e:
            self.print_result("API docs accessible", False, str(e))
            return False
    
    def test_api_auth(self):
        """Test API authentication"""
        print("\n🔐 Testing Authentication...")
        
        try:
            # Test login (using correct API prefix)
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                data={
                    "email": "msp@pulseops.com",
                    "password": "msp123"
                },
                timeout=10
            )
            
            passed = response.status_code == 200
            self.print_result("Login endpoint", passed,
                            f"Status: {response.status_code}" if not passed else "")
            
            if passed:
                data = response.json()
                self.token = data.get('access_token')
                print(f"     Token obtained: {self.token[:20]}...")
            
            return passed
        except Exception as e:
            self.print_result("Login endpoint", False, str(e))
            return False
    
    def test_api_endpoints(self):
        """Test protected API endpoints"""
        print("\n📡 Testing API Endpoints...")
        
        if not self.token:
            print("  ⚠️  Skipping (no auth token)")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        endpoints = [
            ("/api/msp/dashboard", "MSP dashboard"),
            ("/api/msp/clients", "Client list"),
            ("/api/analytics/revenue", "Revenue analytics"),
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                passed = response.status_code == 200
                self.print_result(f"{name} endpoint", passed,
                                f"Status: {response.status_code}" if not passed else "")
                all_passed = all_passed and passed
            except Exception as e:
                self.print_result(f"{name} endpoint", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_ml_service(self):
        """Test ML service"""
        print("\n🤖 Testing ML Service...")
        
        try:
            # Health check
            response = requests.get(f"{self.ml_url}/health", timeout=10)
            passed = response.status_code == 200
            self.print_result("ML service health", passed)
            
            if not passed:
                return False
            
            # Test churn prediction
            test_data = {
                "client_id": 1,
                "features": {
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
            }
            
            response = requests.post(
                f"{self.ml_url}/predict/churn",
                json=test_data,
                timeout=15
            )
            
            passed = response.status_code == 200
            self.print_result("Churn prediction", passed,
                            f"Status: {response.status_code}" if not passed else "")
            
            if passed:
                data = response.json()
                print(f"     Churn risk: {data.get('churn_risk', 'N/A')}")
                print(f"     Probability: {data.get('churn_probability', 'N/A')}")
            
            return passed
            
        except Exception as e:
            self.print_result("ML service", False, str(e))
            return False
    
    def test_ui_accessible(self):
        """Test UI accessibility"""
        print("\n🎨 Testing UI Service...")
        
        try:
            response = requests.get(self.ui_url, timeout=10)
            passed = response.status_code == 200
            self.print_result("UI accessible", passed,
                            f"Status: {response.status_code}" if not passed else "")
            
            if passed:
                # Check for React app indicators
                html = response.text
                has_root = 'id="root"' in html
                self.print_result("React root element found", has_root)
            
            return passed
        except Exception as e:
            self.print_result("UI accessible", False, str(e))
            return False
    
    def test_cors(self):
        """Test CORS configuration"""
        print("\n🔗 Testing CORS...")
        
        try:
            response = requests.options(
                f"{self.api_url}/health",
                headers={
                    "Origin": self.ui_url,
                    "Access-Control-Request-Method": "GET"
                },
                timeout=10
            )
            
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            passed = cors_header is not None
            self.print_result("CORS configured", passed)
            
            if passed:
                print(f"     Allowed origins: {cors_header}")
            
            return passed
        except Exception as e:
            self.print_result("CORS configured", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("="*60)
        print("🧪 PulseOps AI - Deployment Tests")
        print("="*60)
        print(f"\nAPI URL: {self.api_url}")
        print(f"ML URL: {self.ml_url}")
        print(f"UI URL: {self.ui_url}")
        print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        self.test_api_health()
        self.test_api_docs()
        self.test_api_auth()
        self.test_api_endpoints()
        self.test_ml_service()
        self.test_ui_accessible()
        self.test_cors()
        
        # Summary
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        print(f"\n✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {self.tests_passed / (self.tests_passed + self.tests_failed) * 100:.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! Deployment is healthy.")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please investigate.")
            return False

def main():
    parser = argparse.ArgumentParser(description='Test PulseOps AWS deployment')
    parser.add_argument('--api-url', required=True, help='API Gateway URL')
    parser.add_argument('--ml-url', required=True, help='ML API URL')
    parser.add_argument('--ui-url', required=True, help='CloudFront UI URL')
    
    args = parser.parse_args()
    
    tester = DeploymentTester(args.api_url, args.ml_url, args.ui_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
