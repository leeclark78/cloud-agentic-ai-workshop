---
layout: default
title: Workshop Prerequisites & Setup Guide
description: Complete setup guide for cloud accounts, development environment, and dependencies
---

# 🛠️ Workshop Prerequisites & Setup Guide

## Overview

This document outlines everything you need to successfully complete the Cloud-Hosted Agentic AI Systems workshop. Please ensure you have all prerequisites in place before starting the hands-on exercises.

## Technical Requirements

### 1. Development Environment

**Operating System:**
* Linux (Ubuntu 20.04+ recommended)
* macOS (10.15+)  
* Windows 10/11 with WSL2

**Required Software:**
* Git (version 2.20+)
* Python 3.9 or higher
* Node.js 16+ and npm
* Docker Desktop
* Code editor (VS Code recommended)

**Installation Commands (Ubuntu/Debian):**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential

# Install Python and pip
sudo apt install -y python3.11 python3.11-pip python3.11-venv

# Install Node.js (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Verify installations
python3 --version
node --version
docker --version
git --version
```

### 2. Cloud Account Setup

You will need active accounts on all three major cloud platforms:

#### Amazon Web Services (AWS)
* **Account Type**: Free Tier eligible account
* **Required Permissions**:
  * IAM User with programmatic access
  * Permissions for: Lambda, API Gateway, DynamoDB, S3, Bedrock, CloudFormation
* **Cost Estimate**: £0-£20 for workshop exercises
* **Setup Guide**: [AWS Free Tier Setup](https://aws.amazon.com/free/)

#### Google Cloud Platform (GCP)
* **Account Type**: Free Tier account with £300 credits
* **Required Permissions**:
  * Project Owner or Editor role
  * APIs enabled: Vertex AI, Cloud Functions, Firestore, Cloud Storage
* **Cost Estimate**: £0-£15 for workshop exercises
* **Setup Guide**: [GCP Free Tier Setup](https://cloud.google.com/free)

#### Microsoft Azure
* **Account Type**: Free account with £150 credits
* **Required Permissions**:
  * Subscription Contributor access
  * Resource group creation rights
* **Cost Estimate**: £0-£25 for workshop exercises
* **Setup Guide**: [Azure Free Account](https://azure.microsoft.com/free/)

### 3. API Access and Quotas

**Important**: Some services require approval or have waiting lists:

* **AWS Bedrock**: Request model access (usually approved within hours)
* **GCP Vertex AI**: May require quota increases for certain models
* **Azure OpenAI**: Requires application approval (can take 1-10 days)

**Pre-Workshop Tasks:**
1. Apply for Azure OpenAI access immediately
2. Request AWS Bedrock model access
3. Verify GCP AI/ML API quotas

## Knowledge Prerequisites

### Essential Skills
* **Python Programming**: Intermediate level
  * Functions, classes, error handling
  * Working with APIs and JSON
  * Basic understanding of async/await patterns

* **Cloud Computing Fundamentals**:
  * Understanding of serverless computing
  * Basic networking concepts (HTTP/HTTPS, APIs)
  * Infrastructure as Code concepts

* **Command Line Proficiency**:
  * Navigation and file operations
  * Environment variables
  * Package management (pip, npm)

### Recommended Knowledge
* Experience with REST APIs
* Basic understanding of databases (SQL/NoSQL)
* Familiarity with version control (Git)
* Understanding of authentication and security concepts

### Pre-Workshop Learning Resources

If you need to brush up on any topics:

**Python Resources:**
* [Python Official Tutorial](https://docs.python.org/3/tutorial/)
* [Real Python - Working with APIs](https://realpython.com/api-integration-in-python/)

**Cloud Computing:**
* [AWS Cloud Practitioner Essentials](https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/)
* [Google Cloud Digital Leader](https://cloud.google.com/training/digital-leader)
* [Azure Fundamentals](https://docs.microsoft.com/learn/paths/azure-fundamentals/)

## Workshop Setup Verification

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-org/cloud-agentic-ai-workshop.git
cd cloud-agentic-ai-workshop
```

### Step 2: Environment Setup
```bash
# Create Python virtual environment
python3 -m venv workshop-env
source workshop-env/bin/activate  # On Windows: workshop-env\Scripts\activate

# Install common dependencies
pip install -r requirements.txt
```

### Step 3: Cloud CLI Installation

**AWS CLI:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

**Google Cloud CLI:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud --version
```

**Azure CLI:**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az --version
```

### Step 4: Authentication Test

Run the verification script to ensure everything is configured correctly:

```bash
python scripts/verify_setup.py
```

This script will check:
* Python environment and dependencies
* Cloud CLI installations
* Account access and permissions
* API availability and quotas

## Workshop Structure and Time Commitment

### Session Breakdown
* **Session 1**: Introduction and AWS (2 hours)
* **Session 2**: Google Cloud Platform (2 hours)  
* **Session 3**: Microsoft Azure (2 hours)
* **Session 4**: Advanced Patterns and Deployment (1-2 hours)

### Recommended Schedule
* **Self-Paced**: Complete over 2-3 days
* **Workshop Format**: Full day intensive
* **Evening Classes**: 4 sessions over 2 weeks

## Common Issues and Troubleshooting

### Issue: AWS Bedrock Access Denied
**Solution**: Request model access in AWS Console → Bedrock → Model Access

### Issue: GCP Quota Exceeded
**Solution**: Request quota increase in GCP Console → IAM & Admin → Quotas

### Issue: Azure OpenAI Not Available
**Solution**: Ensure you've applied for access and been approved

### Issue: Python Dependencies Fail
**Solution**: 
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### Issue: Docker Permission Denied
**Solution**:
```bash
sudo usermod -aG docker $USER
# Log out and back in, or run:
newgrp docker
```

## Support During Workshop

If you encounter issues during the workshop:

1. **Check the troubleshooting section** in each module
2. **Review error messages carefully** - they often contain the solution
3. **Ask for help** - don't struggle in silence
4. **Use the discussion forum** for community support

## Data and Privacy

### Workshop Data
* All examples use synthetic or public data
* No personal or sensitive information required
* Generated content is for educational purposes only

### Account Security
* Use dedicated accounts for workshop if possible
* Clean up resources after completion
* Review and understand pricing before deployment

## Post-Workshop Cleanup

To avoid unexpected charges:

```bash
# Run cleanup scripts for each platform
./scripts/cleanup-aws.sh
./scripts/cleanup-gcp.sh  
./scripts/cleanup-azure.sh
```

## Ready to Begin?

Once you've completed all prerequisites:

1. ✅ Development environment set up
2. ✅ Cloud accounts configured and verified  
3. ✅ API access approved
4. ✅ Repository cloned and dependencies installed
5. ✅ Authentication tested successfully

You're ready to start building cloud-hosted agentic AI systems!

---

**Need Help?** Create an issue in the workshop repository or contact the workshop organisers.