#!/usr/bin/env python3
"""
PulseOps AI Deployment Script
Deploys the serverless application to AWS
"""

import os
import subprocess
import sys
import boto3
import zipfile
import tempfile
from pathlib import Path

class PulseOpsDeployer:
    def __init__(self, environment='dev'):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.services_dir = self.project_root / 'services'
        
    def deploy_infrastructure(self):
        """Deploy AWS infrastructure using SAM"""
        print("🚀 Deploying AWS infrastructure...")
        
        cmd = [
            'sam', 'deploy',
            '--template-file', str(self.project_root / 'infrastructure' / 'template.yaml'),
            '--stack-name', f'pulseops-{self.environment}',
            '--capabilities', 'CAPABILITY_IAM',
            '--parameter-overrides', f'Environment={self.environment}',
            '--resolve-s3'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Infrastructure deployment failed: {result.stderr}")
            return False
        
        print("✅ Infrastructure deployed successfully!")
        return True
    
    def package_lambda_function(self, service_name):
        """Package Lambda function with dependencies"""
        print(f"📦 Packaging {service_name} service...")
        
        service_dir = self.services_dir / service_name
        requirements_file = service_dir / 'requirements.txt'
        
        # Create temporary directory for packaging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Install dependencies
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    '-r', str(requirements_file),
                    '-t', str(temp_path)
                ], check=True)
            
            # Copy service code
            for py_file in service_dir.glob('*.py'):
                subprocess.run(['cp', str(py_file), str(temp_path)], check=True)
            
            # Create zip file
            zip_path = self.project_root / 'deployment' / f'{service_name}.zip'
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(temp_path)
                        zipf.write(file_path, arcname)
            
            print(f"✅ {service_name} packaged to {zip_path}")
            return zip_path
    
    def deploy_ui(self):
        """Build and deploy React UI to S3"""
        print("🎨 Building and deploying UI...")
        
        ui_dir = self.services_dir / 'ui'
        
        # Build React app
        subprocess.run(['npm', 'run', 'build'], cwd=ui_dir, check=True)
        
        # Deploy to S3
        bucket_name = f'pulseops-ui-{self.environment}'
        subprocess.run([
            'aws', 's3', 'sync',
            str(ui_dir / 'build'),
            f's3://{bucket_name}',
            '--delete'
        ], check=True)
        
        print("✅ UI deployed successfully!")
    
    def deploy(self):
        """Full deployment pipeline"""
        print(f"🚀 Starting PulseOps AI deployment to {self.environment}")
        
        try:
            # Deploy infrastructure
            if not self.deploy_infrastructure():
                return False
            
            # Package and deploy Lambda functions
            self.package_lambda_function('api')
            self.package_lambda_function('ml')
            
            # Deploy UI
            self.deploy_ui()
            
            print("🎉 PulseOps AI deployed successfully!")
            print("\n📊 Access your dashboards:")
            print(f"   MSP Dashboard: https://your-cloudfront-url.com/msp")
            print(f"   IT Dashboard: https://your-cloudfront-url.com/it")
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            return False

if __name__ == '__main__':
    environment = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    deployer = PulseOpsDeployer(environment)
    success = deployer.deploy()
    sys.exit(0 if success else 1)