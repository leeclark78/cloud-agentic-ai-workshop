# Azure Agentic AI Implementation

## Overview

This section covers building agentic AI systems using Microsoft Azure services. We'll leverage Azure OpenAI Service for advanced language models, Azure Functions for serverless compute, and the comprehensive Azure ecosystem to create intelligent, scalable autonomous agents.

## Architecture Components

### Core Services
* **Azure OpenAI Service**: Access to GPT-4, GPT-3.5, and other OpenAI models
* **Azure Functions**: Serverless compute platform for agent logic
* **Azure Cosmos DB**: Multi-model database for agent state and memory
* **Azure Blob Storage**: Scalable object storage for documents and artifacts
* **Azure Service Bus**: Enterprise messaging for agent communication
* **Azure Container Instances**: Containerised workloads for complex agents

### Supporting Services
* **Azure API Management**: Enterprise API gateway and management
* **Azure Monitor**: Comprehensive monitoring and analytics platform
* **Azure Active Directory**: Identity and access management
* **Azure CDN**: Global content delivery network
* **Azure Key Vault**: Secure secrets and certificate management

## Getting Started

### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Install Bicep for infrastructure as code
az bicep install

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Verify installation
az --version
func --version
```

### Subscription and Resource Group Setup
```bash
# Set your subscription (replace with your subscription ID)
az account set --subscription "your-subscription-id"

# Create a resource group
RESOURCE_GROUP="agentic-ai-workshop-rg"
LOCATION="uksouth"

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

## Lab Exercises

### Lab 1: Azure OpenAI Agent Foundation
Create your first agent using Azure OpenAI Service and Azure Functions.

**Objectives:**
* Configure Azure OpenAI resource and models
* Build serverless agent with Python Azure Functions
* Implement conversation handling and response generation

### Lab 2: Cognitive Services Integration
Enhance your agent with multiple Azure Cognitive Services.

**Objectives:**
* Add speech recognition and synthesis
* Integrate Computer Vision for image analysis
* Implement Language Understanding (LUIS) for intent recognition

### Lab 3: Persistent Memory with Cosmos DB
Implement sophisticated memory and context management.

**Objectives:**
* Design conversation history storage
* Build semantic search capabilities
* Implement long-term memory patterns

### Lab 4: Enterprise-Scale Agent Architecture
Create production-ready agents with enterprise features.

**Objectives:**
* Implement robust error handling and retry logic
* Add comprehensive monitoring and alerting
* Build multi-tenant agent architectures

## Code Examples

### Azure OpenAI Integration
```python
import json
import logging
import os
from typing import Dict, Any
import azure.functions as func
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function entry point for agent processing."""
    
    try:
        # Parse request body
        req_body = req.get_json()
        user_message = req_body.get('message', '')
        
        if not user_message:
            return func.HttpResponse(
                json.dumps({"error": "Message is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Generate agent response
        response = generate_agent_response(user_message)
        
        return func.HttpResponse(
            json.dumps({"response": response}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

def generate_agent_response(user_message: str) -> str:
    """Generate response using Azure OpenAI."""
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_KEY"],
        api_version="2024-02-01"
    )
    
    system_prompt = """You are an intelligent AI assistant running on Microsoft Azure.
    You can help users with various tasks including:
    - Answering questions and providing detailed information
    - Problem-solving and analytical thinking
    - Providing recommendations and actionable advice
    
    Be thorough, accurate, and helpful. If you cannot assist with something,
    explain the limitations clearly and suggest alternatives."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Deployment name in Azure OpenAI
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=0.95
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling Azure OpenAI: {str(e)}")
        return "I apologise, but I'm experiencing technical difficulties. Please try again shortly."
```

### Cosmos DB Memory Management
```python
from azure.cosmos import CosmosClient, PartitionKey
from datetime import datetime
from typing import List, Dict, Optional
import json

class AzureAgentMemory:
    """Memory management for Azure-based agents using Cosmos DB."""
    
    def __init__(self, connection_string: str, database_name: str = "agent_memory"):
        self.client = CosmosClient.from_connection_string(connection_string)
        self.database = self.client.get_database_client(database_name)
        self.container = self.database.get_container_client("conversations")
        
    def store_conversation_turn(
        self, 
        agent_id: str, 
        session_id: str, 
        user_message: str, 
        agent_response: str,
        metadata: Optional[Dict] = None
    ):
        """Store a conversation turn in Cosmos DB."""
        
        conversation_item = {
            "id": f"{session_id}_{datetime.utcnow().isoformat()}",
            "agent_id": agent_id,
            "session_id": session_id,
            "user_message": user_message,
            "agent_response": agent_response,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "partitionKey": agent_id
        }
        
        try:
            self.container.create_item(body=conversation_item)
            return True
        except Exception as e:
            logger.error(f"Failed to store conversation: {str(e)}")
            return False
    
    def get_conversation_history(
        self, 
        agent_id: str, 
        session_id: str, 
        limit: int = 20
    ) -> List[Dict]:
        """Retrieve conversation history for a session."""
        
        query = """
        SELECT TOP @limit c.user_message, c.agent_response, c.timestamp 
        FROM c 
        WHERE c.agent_id = @agent_id AND c.session_id = @session_id
        ORDER BY c.timestamp ASC
        """
        
        parameters = [
            {"name": "@agent_id", "value": agent_id},
            {"name": "@session_id", "value": session_id},
            {"name": "@limit", "value": limit}
        ]
        
        try:
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                partition_key=agent_id
            ))
            return items
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {str(e)}")
            return []
```

## Infrastructure as Code with Bicep

### Main Bicep Template
```bicep
@description('The name of the function app')
param functionAppName string = 'agent-functions-${uniqueString(resourceGroup().id)}'

@description('The location of the resources')
param location string = resourceGroup().location

@description('The SKU for the hosting plan')
param sku string = 'Y1'

// Storage account for the function app
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'agentstore${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'agent-insights-${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
  }
}

// Hosting Plan
resource hostingPlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: 'agent-hosting-plan'
  location: location
  sku: {
    name: sku
  }
  properties: {}
}

// Azure OpenAI Service
resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'agent-openai-${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: 'agent-openai-${uniqueString(resourceGroup().id)}'
    publicNetworkAccess: 'Enabled'
  }
}

// Cosmos DB Account
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: 'agent-cosmos-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
}

// Function App
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAI.properties.endpoint
        }
        {
          name: 'AZURE_OPENAI_KEY'
          value: openAI.listKeys().key1
        }
        {
          name: 'COSMOS_CONNECTION_STRING'
          value: cosmosAccount.listConnectionStrings().connectionStrings[0].connectionString
        }
      ]
      pythonVersion: '3.11'
    }
  }
}

// Outputs
output functionAppName string = functionApp.name
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output openAIEndpoint string = openAI.properties.endpoint
```

## Cost Considerations

### Estimated Monthly Costs (moderate usage):
* Azure OpenAI Service: £60-£250 depending on model and usage
* Azure Functions: £4-£18 for compute
* Cosmos DB (Serverless): £12-£35 for storage and operations
* Blob Storage: £4-£15 for storage
* Application Insights: £3-£12 for monitoring
* Other services: £8-£25

### Cost Optimisation Tips:
* Use consumption-based pricing where possible
* Implement appropriate caching strategies
* Monitor token usage for OpenAI calls
* Set up cost alerts and budgets

## Security Best Practices

* Use Azure Active Directory for authentication
* Implement Managed Identity for service-to-service auth
* Store secrets in Azure Key Vault
* Enable network security groups and firewalls
* Regular security assessments and compliance checks
* Audit logging for all operations

## Monitoring and Observability

### Application Insights Integration
```python
from applicationinsights import TelemetryClient
from applicationinsights.requests import WSGIApplication
import os

# Initialize Application Insights
tc = TelemetryClient(os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY'))

def track_agent_interaction(user_message: str, response: str, duration: float):
    """Track agent interactions for monitoring."""
    
    # Track custom event
    tc.track_event(
        'AgentInteraction',
        properties={
            'message_length': len(user_message),
            'response_length': len(response),
            'processing_duration': duration
        }
    )
    
    # Track custom metric
    tc.track_metric('ResponseTime', duration)
    tc.flush()
```

## Next Steps

After completing the Azure section:
* Compare approaches across all three cloud platforms
* Understand the unique strengths of each platform
* Learn multi-cloud and hybrid deployment strategies

## Resources

* [Azure OpenAI Service Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
* [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
* [Azure Cosmos DB Documentation](https://docs.microsoft.com/azure/cosmos-db/)