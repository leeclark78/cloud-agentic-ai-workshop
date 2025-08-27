#!/usr/bin/env python3
"""
Workshop Setup Verification Script
This script verifies that all prerequisites are met for the workshop.
"""

import os
import sys
import subprocess
import json
from typing import Dict, List, Tuple
import importlib
import platform

class SetupVerifier:
    """Verifies workshop setup requirements."""
    
    def __init__(self):
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {
            'system': [],
            'python': [],
            'cloud_cli': [],
            'authentication': [],
            'permissions': []
        }
        
    def run_command(self, command: str, shell: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)
    
    def check_system_requirements(self):
        """Check basic system requirements."""
        print("🖥️  Checking System Requirements...")
        
        # Check Python version
        python_version = sys.version_info
        python_ok = python_version >= (3, 9)
        self.results['system'].append((
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro}",
            python_ok,
            "✅ Compatible" if python_ok else "❌ Need Python 3.9+"
        ))
        
        # Check Node.js
        node_ok, node_output = self.run_command("node --version")
        self.results['system'].append((
            "Node.js",
            node_ok,
            f"✅ {node_output.strip()}" if node_ok else "❌ Not installed"
        ))
        
        # Check Git
        git_ok, git_output = self.run_command("git --version")
        self.results['system'].append((
            "Git",
            git_ok,
            f"✅ Installed" if git_ok else "❌ Not installed"
        ))
        
        # Check Docker
        docker_ok, docker_output = self.run_command("docker --version")
        self.results['system'].append((
            "Docker",
            docker_ok,
            f"✅ {docker_output.strip()}" if docker_ok else "❌ Not installed"
        ))
    
    def check_python_dependencies(self):
        """Check Python package dependencies."""
        print("🐍 Checking Python Dependencies...")
        
        required_packages = [
            'boto3', 'google-cloud-aiplatform', 'azure-functions',
            'requests', 'openai', 'azure-identity'
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
                self.results['python'].append((
                    package,
                    True,
                    "✅ Installed"
                ))
            except ImportError:
                self.results['python'].append((
                    package,
                    False,
                    "❌ Not installed"
                ))
    
    def check_cloud_cli_tools(self):
        """Check cloud CLI tools installation."""
        print("☁️  Checking Cloud CLI Tools...")
        
        # AWS CLI
        aws_ok, aws_output = self.run_command("aws --version")
        self.results['cloud_cli'].append((
            "AWS CLI",
            aws_ok,
            f"✅ {aws_output.split()[0]}" if aws_ok else "❌ Not installed"
        ))
        
        # Google Cloud CLI
        gcloud_ok, gcloud_output = self.run_command("gcloud --version")
        self.results['cloud_cli'].append((
            "Google Cloud CLI",
            gcloud_ok,
            "✅ Installed" if gcloud_ok else "❌ Not installed"
        ))
        
        # Azure CLI
        az_ok, az_output = self.run_command("az --version")
        self.results['cloud_cli'].append((
            "Azure CLI",
            az_ok,
            "✅ Installed" if az_ok else "❌ Not installed"
        ))
        
        # CDK (optional but recommended)
        cdk_ok, cdk_output = self.run_command("cdk --version")
        self.results['cloud_cli'].append((
            "AWS CDK",
            cdk_ok,
            f"✅ {cdk_output.strip()}" if cdk_ok else "⚠️  Optional - not installed"
        ))
        
        # Terraform (optional)
        terraform_ok, terraform_output = self.run_command("terraform --version")
        self.results['cloud_cli'].append((
            "Terraform",
            terraform_ok,
            f"✅ {terraform_output.split()[1]}" if terraform_ok else "⚠️  Optional - not installed"
        ))
    
    def check_authentication(self):
        """Check cloud authentication status."""
        print("🔐 Checking Cloud Authentication...")
        
        # AWS Authentication
        aws_auth_ok, aws_auth_output = self.run_command("aws sts get-caller-identity")
        if aws_auth_ok:
            try:
                aws_info = json.loads(aws_auth_output)
                self.results['authentication'].append((
                    "AWS",
                    True,
                    f"✅ Authenticated as {aws_info.get('Arn', 'Unknown')}"
                ))
            except json.JSONDecodeError:
                self.results['authentication'].append((
                    "AWS",
                    False,
                    "❌ Authentication response invalid"
                ))
        else:
            self.results['authentication'].append((
                "AWS",
                False,
                "❌ Not authenticated - run 'aws configure'"
            ))
        
        # GCP Authentication
        gcp_auth_ok, gcp_auth_output = self.run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'")
        if gcp_auth_ok and gcp_auth_output.strip():
            self.results['authentication'].append((
                "Google Cloud",
                True,
                f"✅ Authenticated as {gcp_auth_output.strip()}"
            ))
        else:
            self.results['authentication'].append((
                "Google Cloud",
                False,
                "❌ Not authenticated - run 'gcloud auth login'"
            ))
        
        # Azure Authentication  
        az_auth_ok, az_auth_output = self.run_command("az account show --query 'user.name' -o tsv")
        if az_auth_ok and az_auth_output.strip():
            self.results['authentication'].append((
                "Azure",
                True,
                f"✅ Authenticated as {az_auth_output.strip()}"
            ))
        else:
            self.results['authentication'].append((
                "Azure",
                False,
                "❌ Not authenticated - run 'az login'"
            ))
    
    def check_service_permissions(self):
        """Check basic service permissions and access."""
        print("🛡️  Checking Service Permissions...")
        
        # AWS Bedrock check
        aws_bedrock_ok, bedrock_output = self.run_command("aws bedrock list-foundation-models --region us-east-1")
        self.results['permissions'].append((
            "AWS Bedrock Access",
            aws_bedrock_ok,
            "✅ Can list models" if aws_bedrock_ok else "❌ No access or not enabled"
        ))
        
        # GCP Vertex AI check
        gcp_vertex_ok, vertex_output = self.run_command("gcloud ai models list --region=us-central1 --limit=1")
        self.results['permissions'].append((
            "GCP Vertex AI Access",
            gcp_vertex_ok,
            "✅ Can list models" if gcp_vertex_ok else "❌ No access or API not enabled"
        ))
        
        # Azure OpenAI check (this might fail if not approved)
        az_openai_ok, openai_output = self.run_command("az cognitiveservices account list --query '[?kind==`OpenAI`]'")
        self.results['permissions'].append((
            "Azure OpenAI Access",
            az_openai_ok,
            "✅ Can list OpenAI resources" if az_openai_ok else "❌ No access or not approved"
        ))
    
    def print_results(self):
        """Print verification results in a formatted way."""
        print("\n" + "="*60)
        print("🎯 WORKSHOP SETUP VERIFICATION RESULTS")
        print("="*60)
        
        total_checks = 0
        passed_checks = 0
        
        for category, checks in self.results.items():
            if not checks:
                continue
                
            print(f"\n📋 {category.replace('_', ' ').title()}:")
            print("-" * 40)
            
            for name, status, message in checks:
                total_checks += 1
                if status:
                    passed_checks += 1
                print(f"  {name:<20} {message}")
        
        print("\n" + "="*60)
        print(f"📊 SUMMARY: {passed_checks}/{total_checks} checks passed")
        
        if passed_checks == total_checks:
            print("🎉 Excellent! You're ready for the workshop!")
        elif passed_checks >= total_checks * 0.8:
            print("⚠️  Most requirements met. Check failed items above.")
        else:
            print("❌ Several requirements missing. Please install missing components.")
        
        print("="*60)
    
    def generate_fix_commands(self):
        """Generate commands to fix common issues."""
        print("\n🔧 QUICK FIX COMMANDS:")
        print("-" * 30)
        
        failed_items = []
        for category, checks in self.results.items():
            for name, status, _ in checks:
                if not status:
                    failed_items.append((category, name))
        
        if not failed_items:
            print("✅ No fixes needed!")
            return
        
        fix_commands = {
            'python': {
                'boto3': "pip install boto3",
                'google-cloud-aiplatform': "pip install google-cloud-aiplatform", 
                'azure-functions': "pip install azure-functions",
                'requests': "pip install requests",
                'openai': "pip install openai",
                'azure-identity': "pip install azure-identity"
            },
            'system': {
                'Node.js': "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs",
                'Git': "sudo apt install -y git",
                'Docker': "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh"
            },
            'cloud_cli': {
                'AWS CLI': "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install",
                'Google Cloud CLI': "curl https://sdk.cloud.google.com | bash && exec -l $SHELL",
                'Azure CLI': "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash",
                'AWS CDK': "npm install -g aws-cdk",
                'Terraform': "wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip && unzip terraform_1.6.0_linux_amd64.zip && sudo mv terraform /usr/local/bin/"
            },
            'authentication': {
                'AWS': "aws configure",
                'Google Cloud': "gcloud auth login && gcloud auth application-default login",
                'Azure': "az login"
            }
        }
        
        for category, name in failed_items:
            if category in fix_commands and name in fix_commands[category]:
                print(f"{name}: {fix_commands[category][name]}")
    
    def run_all_checks(self):
        """Run all verification checks."""
        print("🚀 Starting Workshop Setup Verification...\n")
        
        self.check_system_requirements()
        self.check_python_dependencies()
        self.check_cloud_cli_tools()
        self.check_authentication()
        self.check_service_permissions()
        
        self.print_results()
        self.generate_fix_commands()

def main():
    """Main function to run setup verification."""
    verifier = SetupVerifier()
    verifier.run_all_checks()

if __name__ == "__main__":
    main()