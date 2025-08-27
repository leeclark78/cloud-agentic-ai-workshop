#!/bin/bash

# Cloud-Hosted Agentic AI Workshop - Complete Deployment Script
# This script deploys the workshop infrastructure across AWS, GCP, and Azure

set -e  # Exit on any error

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
WORKSHOP_PREFIX="agentic-ai-workshop"
TIMESTAMP=$(date +%s)
PROJECT_NAME="${WORKSHOP_PREFIX}-${TIMESTAMP}"

# Function to print coloured messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check required commands
    local required_commands=("aws" "gcloud" "az" "terraform" "python3" "node" "npm")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is not installed. Please install it before continuing."
            exit 1
        fi
    done
    
    # Check authentication status
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI not authenticated. Run 'aws configure' first."
        exit 1
    fi
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        print_error "Google Cloud CLI not authenticated. Run 'gcloud auth login' first."
        exit 1
    fi
    
    if ! az account show &> /dev/null; then
        print_error "Azure CLI not authenticated. Run 'az login' first."
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

# Function to deploy AWS infrastructure
deploy_aws() {
    print_status "Deploying AWS infrastructure..."
    
    cd aws/infrastructure
    
    # Install CDK dependencies
    npm install
    
    # Bootstrap CDK if needed
    if ! aws cloudformation describe-stacks --stack-name CDKToolkit &> /dev/null; then
        print_status "Bootstrapping AWS CDK..."
        npx cdk bootstrap
    fi
    
    # Deploy the stack
    print_status "Deploying AWS CDK stack..."
    npx cdk deploy --require-approval never
    
    # Get outputs
    AWS_API_URL=$(aws cloudformation describe-stacks --stack-name BasicAgentStack --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text)
    
    print_success "AWS deployment completed!"
    print_status "AWS API URL: $AWS_API_URL"
    
    cd ../..
}

# Function to deploy GCP infrastructure
deploy_gcp() {
    print_status "Deploying GCP infrastructure..."
    
    cd gcp/infrastructure
    
    # Set up GCP project
    local gcp_project_id="${PROJECT_NAME}-gcp"
    
    # Create project
    if ! gcloud projects describe $gcp_project_id &> /dev/null; then
        print_status "Creating GCP project: $gcp_project_id"
        gcloud projects create $gcp_project_id
    fi
    
    gcloud config set project $gcp_project_id
    
    # Enable required APIs
    print_status "Enabling required GCP APIs..."
    gcloud services enable aiplatform.googleapis.com
    gcloud services enable cloudfunctions.googleapis.com
    gcloud services enable firestore.googleapis.com
    gcloud services enable pubsub.googleapis.com
    gcloud services enable run.googleapis.com
    
    # Initialize Terraform
    terraform init
    
    # Plan and apply Terraform configuration
    terraform plan -var="project_id=$gcp_project_id" -out=tfplan
    terraform apply tfplan
    
    # Get outputs
    GCP_FUNCTION_URL=$(terraform output -raw function_url)
    
    print_success "GCP deployment completed!"
    print_status "GCP Function URL: $GCP_FUNCTION_URL"
    
    cd ../..
}

# Function to deploy Azure infrastructure
deploy_azure() {
    print_status "Deploying Azure infrastructure..."
    
    cd azure/infrastructure
    
    # Set variables
    local resource_group="${PROJECT_NAME}-rg"
    local location="uksouth"
    
    # Create resource group
    print_status "Creating Azure resource group: $resource_group"
    az group create --name $resource_group --location $location
    
    # Deploy Bicep template
    print_status "Deploying Azure Bicep template..."
    az deployment group create \
        --resource-group $resource_group \
        --template-file main.bicep \
        --parameters functionAppName="${PROJECT_NAME}-func"
    
    # Get outputs
    AZURE_FUNCTION_URL=$(az deployment group show --resource-group $resource_group --name main --query properties.outputs.functionAppUrl.value --output tsv)
    
    print_success "Azure deployment completed!"
    print_status "Azure Function URL: $AZURE_FUNCTION_URL"
    
    cd ../..
}

# Function to run tests
run_tests() {
    print_status "Running deployment verification tests..."
    
    # Create test configuration file
    cat > test_config.json << EOF
{
    "aws_api_url": "$AWS_API_URL",
    "gcp_function_url": "$GCP_FUNCTION_URL", 
    "azure_function_url": "$AZURE_FUNCTION_URL"
}
EOF
    
    # Run verification script
    python3 scripts/test_deployment.py
    
    if [ $? -eq 0 ]; then
        print_success "All deployment tests passed!"
    else
        print_warning "Some deployment tests failed. Check the logs above."
    fi
}

# Function to generate workshop documentation
generate_documentation() {
    print_status "Generating workshop documentation..."
    
    # Create workshop info file
    cat > WORKSHOP_DEPLOYMENT.md << EOF
# Workshop Deployment Information

Generated on: $(date)
Project Name: $PROJECT_NAME

## Deployed Resources

### AWS
- **Stack Name**: BasicAgentStack
- **API URL**: $AWS_API_URL
- **Region**: $(aws configure get region)

### Google Cloud Platform  
- **Project ID**: ${PROJECT_NAME}-gcp
- **Function URL**: $GCP_FUNCTION_URL
- **Region**: us-central1

### Microsoft Azure
- **Resource Group**: ${PROJECT_NAME}-rg
- **Function URL**: $AZURE_FUNCTION_URL
- **Location**: uksouth

## Workshop Access

Use the following URLs to test your deployed agents:

1. **AWS Agent**: $AWS_API_URL
2. **GCP Agent**: $GCP_FUNCTION_URL  
3. **Azure Agent**: $AZURE_FUNCTION_URL

## Clean-up Commands

To remove all resources after the workshop:

\`\`\`bash
# Clean up AWS
cd aws/infrastructure && npx cdk destroy

# Clean up GCP
cd gcp/infrastructure && terraform destroy

# Clean up Azure  
az group delete --name ${PROJECT_NAME}-rg --yes
\`\`\`

## Cost Monitoring

Monitor costs in each platform:
- **AWS**: CloudWatch Billing Dashboard
- **GCP**: Cloud Billing Console  
- **Azure**: Cost Management + Billing

## Support

If you encounter issues:
1. Check the troubleshooting section in each platform's README
2. Review the deployment logs above
3. Create an issue in the workshop repository
EOF

    print_success "Workshop documentation generated: WORKSHOP_DEPLOYMENT.md"
}

# Function to clean up on failure
cleanup_on_failure() {
    print_error "Deployment failed. Cleaning up partial deployments..."
    
    # Clean up AWS
    if aws cloudformation describe-stacks --stack-name BasicAgentStack &> /dev/null; then
        print_status "Cleaning up AWS stack..."
        cd aws/infrastructure && npx cdk destroy --force && cd ../..
    fi
    
    # Clean up GCP
    if gcloud projects describe ${PROJECT_NAME}-gcp &> /dev/null; then
        print_status "Cleaning up GCP resources..."
        cd gcp/infrastructure && terraform destroy -auto-approve && cd ../..
    fi
    
    # Clean up Azure
    if az group exists --name ${PROJECT_NAME}-rg | grep -q true; then
        print_status "Cleaning up Azure resource group..."
        az group delete --name ${PROJECT_NAME}-rg --yes --no-wait
    fi
}

# Main deployment function
main() {
    print_status "Starting Cloud-Hosted Agentic AI Workshop deployment..."
    print_status "Project Name: $PROJECT_NAME"
    
    # Set up error handling
    trap cleanup_on_failure ERR
    
    # Run deployment steps
    check_prerequisites
    
    # Deploy to all platforms
    deploy_aws
    deploy_gcp  
    deploy_azure
    
    # Verify deployments
    run_tests
    
    # Generate documentation
    generate_documentation
    
    print_success "🎉 Workshop deployment completed successfully!"
    print_status "Check WORKSHOP_DEPLOYMENT.md for access information"
    print_warning "Remember to clean up resources after the workshop to avoid charges"
}

# Handle script arguments
case "${1:-all}" in
    "aws")
        check_prerequisites
        deploy_aws
        ;;
    "gcp")
        check_prerequisites  
        deploy_gcp
        ;;
    "azure")
        check_prerequisites
        deploy_azure
        ;;
    "test")
        run_tests
        ;;
    "cleanup")
        cleanup_on_failure
        ;;
    "all"|*)
        main
        ;;
esac