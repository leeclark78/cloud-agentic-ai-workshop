# Lab 1: Basic Agent with AWS Bedrock

## Objective
Create your first autonomous agent using AWS Bedrock and Lambda that can understand requests, reason about them, and provide intelligent responses.

## Duration
45-60 minutes

## Prerequisites
* AWS CLI configured with appropriate permissions
* Python 3.9+ installed locally
* Basic understanding of serverless functions

## Architecture Overview

```
User Request → API Gateway → Lambda Function → Bedrock → Response
```

## Step 1: Enable AWS Bedrock Access

Before we can use Bedrock models, we need to request access:

1. Navigate to AWS Bedrock in the console
2. Go to "Model access" in the left sidebar
3. Request access to Claude 3.5 Sonnet and Llama 3.1 models
4. Wait for approval (usually takes a few minutes)

## Step 2: Create the Agent Lambda Function

Create a new file: `basic_agent.py`

```python
import json
import boto3
import logging
from typing import Dict, Any

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler for the basic agent.
    """
    try:
        # Extract the user message from the event
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        
        if not user_message:
            return create_response(400, {'error': 'Message is required'})
        
        # Generate response using Bedrock
        agent_response = generate_agent_response(user_message)
        
        return create_response(200, {'response': agent_response})
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def generate_agent_response(user_message: str) -> str:
    """
    Generate a response using AWS Bedrock Claude model.
    """
    
    # System prompt that defines the agent's behaviour
    system_prompt = """You are a helpful AI assistant agent running on AWS. 
    You can help users with various tasks including:
    - Answering questions and providing information
    - Helping with problem-solving and analysis
    - Providing recommendations and suggestions
    
    Be concise, accurate, and helpful in your responses.
    If you cannot help with something, explain why clearly."""
    
    # Prepare the request for Claude 3.5 Sonnet
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    try:
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        agent_response = response_body['content'][0]['text']
        
        logger.info(f"Generated response length: {len(agent_response)}")
        return agent_response
        
    except Exception as e:
        logger.error(f"Error calling Bedrock: {str(e)}")
        return "I apologise, but I'm experiencing technical difficulties. Please try again later."

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a properly formatted HTTP response for API Gateway.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }
```

## Step 3: Create Infrastructure with CDK

Create `cdk_app.py`:

```python
#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Duration
)
from constructs import Construct

class BasicAgentStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create IAM role for Lambda
        lambda_role = iam.Role(
            self, "BasicAgentLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Add Bedrock permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )
        
        # Create Lambda function
        basic_agent_function = _lambda.Function(
            self, "BasicAgentFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("lambda"),
            handler="basic_agent.lambda_handler",
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "LOG_LEVEL": "INFO"
            }
        )
        
        # Create API Gateway
        api = apigateway.RestApi(
            self, "BasicAgentApi",
            rest_api_name="Basic Agent API",
            description="API for basic AI agent interactions",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # Add POST method
        agent_integration = apigateway.LambdaIntegration(
            basic_agent_function,
            request_templates={"application/json": '{"statusCode": 200}'}
        )
        
        api.root.add_method("POST", agent_integration)
        
        # Output the API URL
        cdk.CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="URL for the Basic Agent API"
        )

app = cdk.App()
BasicAgentStack(app, "BasicAgentStack")
app.synth()
```

## Step 4: Deploy the Infrastructure

Create the deployment structure:

```bash
# Create the CDK project
mkdir basic-agent-cdk
cd basic-agent-cdk

# Create lambda directory and copy function code
mkdir lambda
# Copy basic_agent.py to lambda/ directory

# Initialize CDK
cdk init --language python
# Replace the generated files with our code above

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

## Step 5: Test Your Agent

Create a test script `test_agent.py`:

```python
import requests
import json

# Replace with your API Gateway URL from CDK output
API_URL = "YOUR_API_GATEWAY_URL_HERE"

def test_agent(message: str):
    """Test the agent with a message."""
    
    payload = {
        "message": message
    }
    
    try:
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Agent Response: {result['response']}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Request failed: {str(e)}")

if __name__ == "__main__":
    # Test cases
    test_messages = [
        "Hello! Can you help me understand what you can do?",
        "What are the benefits of using serverless architecture?",
        "Can you explain how AWS Bedrock works?",
        "Help me plan a weekend trip to Edinburgh"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        test_agent(message)
        print("-" * 50)
```

## Step 6: Verify and Monitor

1. **Check CloudWatch Logs**: Monitor your Lambda function logs for any errors
2. **Test Different Inputs**: Try various types of questions and requests
3. **Monitor Costs**: Check AWS Bedrock usage in the billing console

## Expected Results

Your agent should:
* Respond to general questions with helpful information
* Maintain a consistent personality and tone
* Handle errors gracefully
* Respond within reasonable time limits (under 10 seconds)

## Troubleshooting

### Common Issues:

**Bedrock Access Denied**
* Ensure you've requested and received model access
* Check IAM permissions for Bedrock

**Lambda Timeout**
* Increase timeout in CDK configuration
* Optimise the request/response handling

**API Gateway Errors**
* Verify CORS configuration
* Check request/response format

## Next Steps

In Lab 2, we'll enhance this agent to:
* Use multiple AWS services as tools
* Implement more sophisticated reasoning
* Add persistent memory capabilities

## Clean Up

To avoid ongoing charges:
```bash
cdk destroy
```

This will remove all resources created during this lab.