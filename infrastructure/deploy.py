#!/usr/bin/env python3
"""
AWS Infrastructure Deployment Script
Deploys PulseOps AI to AWS using SAM CLI
"""

import subprocess
import sys
import os
import argparse
import json
from pathlib import Path

class AWSDeployer:
    def __init__(self, environment='dev', region='us-east-1'):
        self.environment = environment
        self.region = region
        self.project_root = Path(__file__).parent.parent
        self.infrastructure_dir = self.project_root / 'infrastructure'
        
    def check_prerequisites(self):
        """Check if required tools are installed"""
        print("🔍 Checking prerequisites...")
        
        tools = {
            'sam': 'AWS SAM CLI',
            'aws': 'AWS CLI',
            'python': 'Python 3',
            'npm': 'Node.js/NPM'
        }
        
        missing = []
        for cmd, name in tools.items():
            try:
                subprocess.run([cmd, '--version'], 
                             capture_output=True, 
                             check=True)
                print(f"  ✅ {name} installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"  ❌ {name} not found")
                missing.append(name)
        
        if missing:
            print(f"\n❌ Missing required tools: {', '.join(missing)}")
            print("\nInstallation instructions:")
            print("  - AWS SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html")
            print("  - AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
            return False
        
        return True
    
    def validate_aws_credentials(self):
        """Validate AWS credentials"""
        print("\n🔐 Validating AWS credentials...")
        
        try:
            result = subprocess.run(['aws', 'sts', 'get-caller-identity'],
                                  capture_output=True,
                                  text=True,
                                  check=True)
            identity = json.loads(result.stdout)
            print(f"  ✅ Authenticated as: {identity['Arn']}")
            print(f"  📍 Account: {identity['Account']}")
            return True
        except subprocess.CalledProcessError:
            print("  ❌ AWS credentials not configured")
            print("\nConfigure credentials with: aws configure")
            return False
    
    def build_api_service(self):
        """Build API Lambda function"""
        print("\n📦 Building API service...")
        
        api_dir = self.project_root / 'services' / 'api'
        
        try:
            # Install dependencies
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                '-r', str(api_dir / 'requirements.txt'),
                '-t', str(api_dir / 'package')
            ], check=True)
            
            print("  ✅ API service built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to build API service: {e}")
            return False
    
    def build_ml_service(self):
        """Build ML Lambda function"""
        print("\n🤖 Building ML service...")
        
        ml_dir = self.project_root / 'services' / 'ml'
        
        try:
            # Install dependencies
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                '-r', str(ml_dir / 'requirements.txt'),
                '-t', str(ml_dir / 'package')
            ], check=True)
            
            print("  ✅ ML service built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to build ML service: {e}")
            return False
    
    def build_ui(self):
        """Build React UI"""
        print("\n🎨 Building React UI...")
        
        ui_dir = self.project_root / 'services' / 'ui'
        
        try:
            # Install dependencies
            subprocess.run(['npm', 'install'], 
                         cwd=ui_dir, 
                         check=True)
            
            # Build production bundle
            subprocess.run(['npm', 'run', 'build'], 
                         cwd=ui_dir, 
                         check=True)
            
            print("  ✅ UI built successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to build UI: {e}")
            return False
    
    def sam_build(self):
        """Run SAM build"""
        print("\n🏗️  Running SAM build...")
        
        try:
            subprocess.run([
                'sam', 'build',
                '--template-file', str(self.infrastructure_dir / 'sam-template.yaml'),
                '--use-container'
            ], cwd=self.infrastructure_dir, check=True)
            
            print("  ✅ SAM build completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ SAM build failed: {e}")
            return False
    
    def sam_deploy(self):
        """Deploy with SAM"""
        print(f"\n🚀 Deploying to AWS ({self.environment})...")
        
        try:
            cmd = [
                'sam', 'deploy',
                '--template-file', str(self.infrastructure_dir / 'sam-template.yaml'),
                '--stack-name', f'pulseops-{self.environment}',
                '--capabilities', 'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM',
                '--region', self.region,
                '--parameter-overrides',
                f'Environment={self.environment}',
                'DBUsername=pulseops_admin',
                'DBPassword=ChangeThisPassword123!',  # Should be from secrets
                'JWTSecretKey=ChangeThisSecretKey123!',
                '--no-confirm-changeset',
                '--no-fail-on-empty-changeset'
            ]
            
            subprocess.run(cmd, cwd=self.infrastructure_dir, check=True)
            
            print("  ✅ Stack deployed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Deployment failed: {e}")
            return False
    
    def get_stack_outputs(self):
        """Get CloudFormation stack outputs"""
        print("\n📊 Fetching stack outputs...")
        
        try:
            result = subprocess.run([
                'aws', 'cloudformation', 'describe-stacks',
                '--stack-name', f'pulseops-{self.environment}',
                '--region', self.region
            ], capture_output=True, text=True, check=True)
            
            stacks = json.loads(result.stdout)
            if stacks['Stacks']:
                outputs = stacks['Stacks'][0].get('Outputs', [])
                
                print("\n✅ Deployment Complete!")
                print("\n" + "="*60)
                print("📋 Stack Outputs:")
                print("="*60)
                
                for output in outputs:
                    print(f"\n{output['OutputKey']}:")
                    print(f"  {output['OutputValue']}")
                    if 'Description' in output:
                        print(f"  ({output['Description']})")
                
                return outputs
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Could not fetch stack outputs: {e}")
            return []
    
    def deploy_ui_to_s3(self, bucket_name=None):
        """Deploy UI build to S3"""
        print("\n☁️  Deploying UI to S3...")
        
        if not bucket_name:
            # Try to get bucket name from stack outputs
            try:
                result = subprocess.run([
                    'aws', 'cloudformation', 'describe-stacks',
                    '--stack-name', f'pulseops-{self.environment}',
                    '--query', 'Stacks[0].Outputs[?OutputKey==`UIBucketName`].OutputValue',
                    '--output', 'text',
                    '--region', self.region
                ], capture_output=True, text=True, check=True)
                bucket_name = result.stdout.strip()
            except subprocess.CalledProcessError:
                print("  ⚠️  Could not determine S3 bucket name")
                return False
        
        if not bucket_name:
            print("  ❌ No bucket name specified")
            return False
        
        ui_build_dir = self.project_root / 'services' / 'ui' / 'build'
        
        try:
            subprocess.run([
                'aws', 's3', 'sync',
                str(ui_build_dir),
                f's3://{bucket_name}',
                '--delete',
                '--region', self.region
            ], check=True)
            
            print(f"  ✅ UI deployed to s3://{bucket_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to deploy UI: {e}")
            return False
    
    def run_database_migrations(self, db_endpoint):
        """Run database migrations"""
        print("\n🗄️  Running database migrations...")
        
        # This would use Alembic or similar
        print("  ℹ️  Database migrations should be run manually with Alembic")
        print(f"  Database endpoint: {db_endpoint}")
        return True
    
    def full_deployment(self):
        """Execute full deployment pipeline"""
        print("="*60)
        print("🚀 PulseOps AI - AWS Deployment")
        print("="*60)
        print(f"\nEnvironment: {self.environment}")
        print(f"Region: {self.region}\n")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        if not self.validate_aws_credentials():
            return False
        
        # Build services
        if not self.build_api_service():
            return False
        
        if not self.build_ml_service():
            return False
        
        if not self.build_ui():
            return False
        
        # SAM build and deploy
        if not self.sam_build():
            return False
        
        if not self.sam_deploy():
            return False
        
        # Get outputs
        outputs = self.get_stack_outputs()
        
        # Deploy UI
        self.deploy_ui_to_s3()
        
        print("\n" + "="*60)
        print("🎉 Deployment Complete!")
        print("="*60)
        print("\n📌 Next Steps:")
        print("  1. Update UI environment variables with API URL")
        print("  2. Run database migrations")
        print("  3. Seed initial data")
        print("  4. Test the application")
        print("\n💡 Access your application:")
        print("  - UI: Check CloudFront URL in outputs above")
        print("  - API: Check API Gateway URL in outputs above")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Deploy PulseOps AI to AWS')
    parser.add_argument('--environment', '-e', 
                       choices=['dev', 'staging', 'prod'],
                       default='dev',
                       help='Deployment environment')
    parser.add_argument('--region', '-r',
                       default='us-east-1',
                       help='AWS region')
    parser.add_argument('--skip-build', 
                       action='store_true',
                       help='Skip building services')
    
    args = parser.parse_args()
    
    deployer = AWSDeployer(args.environment, args.region)
    success = deployer.full_deployment()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()