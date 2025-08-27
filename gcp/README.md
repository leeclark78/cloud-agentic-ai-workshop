# Google Cloud Agentic AI Implementation

## Overview

This section demonstrates building agentic AI systems using Google Cloud Platform services. We'll utilise Vertex AI for advanced ML capabilities, Cloud Functions for serverless compute, and various GCP services to create sophisticated autonomous agents.

## Architecture Components

### Core Services
* **Vertex AI**: Unified ML platform with foundation models and custom training
* **Cloud Functions**: Serverless functions for agent logic execution
* **Firestore**: NoSQL document database for agent state and memory
* **Cloud Storage**: Object storage for documents, artifacts, and model assets
* **Pub/Sub**: Messaging service for agent communication and event handling
* **Cloud Run**: Containerised applications for more complex agent workloads

### Supporting Services
* **Cloud API Gateway**: Managed API gateway for agent endpoints
* **Cloud Monitoring**: Comprehensive monitoring and alerting
* **Identity and Access Management (IAM)**: Security and access control
* **Cloud CDN**: Content delivery and caching
* **Secret Manager**: Secure storage for API keys and credentials

## Getting Started

### Prerequisites
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialise gcloud
gcloud init
gcloud auth application-default login

# Install Terraform for infrastructure
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
gcloud --version
terraform --version
```

### Project Setup
```bash
# Create a new GCP project
export PROJECT_ID="agentic-ai-workshop-$(date +%s)"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

## Lab Exercises

### Lab 1: Vertex AI Agent Foundation
Build your first agent using Vertex AI's foundation models and Cloud Functions.

**Objectives:**
* Configure Vertex AI model access
* Create serverless agent logic
* Implement reasoning and natural language understanding

### Lab 2: Multi-Modal Agent
Create an agent that can process text, images, and documents.

**Objectives:**
* Integrate Vision AI for image processing
* Handle document analysis with Document AI
* Combine multi-modal inputs for comprehensive responses

### Lab 3: Agent Memory and Context
Implement sophisticated memory management using Firestore.

**Objectives:**
* Design conversation history storage
* Implement semantic search for context retrieval
* Build knowledge graphs for agent reasoning

### Lab 4: Event-Driven Agent Architecture
Create reactive agents using Pub/Sub for event-driven responses.

**Objectives:**
* Design event-driven workflows
* Implement agent-to-agent communication
* Handle complex orchestration patterns

## Code Examples

### Basic Vertex AI Integration
```python
from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel

def generate_agent_response(prompt: str, context: str = "") -> str:
    """Generate response using Vertex AI PaLM model."""
    
    model = TextGenerationModel.from_pretrained("text-bison@002")
    
    full_prompt = f"""
    You are an intelligent AI agent running on Google Cloud Platform.
    
    Context: {context}
    
    User Request: {prompt}
    
    Provide a helpful, accurate, and concise response:
    """
    
    response = model.predict(
        prompt=full_prompt,
        max_output_tokens=1024,
        temperature=0.7,
        top_p=0.95,
        top_k=40
    )
    
    return response.text
```

### Firestore Memory Management
```python
from google.cloud import firestore
from datetime import datetime
from typing import List, Dict

class AgentMemory:
    def __init__(self, agent_id: str):
        self.db = firestore.Client()
        self.agent_id = agent_id
        
    def store_conversation(self, user_message: str, agent_response: str):
        """Store conversation in Firestore."""
        doc_ref = self.db.collection('conversations').document()
        doc_ref.set({
            'agent_id': self.agent_id,
            'user_message': user_message,
            'agent_response': agent_response,
            'timestamp': datetime.utcnow(),
            'session_id': self.get_current_session()
        })
        
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversation history."""
        docs = (self.db.collection('conversations')
                .where('agent_id', '==', self.agent_id)
                .order_by('timestamp', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream())
        
        return [doc.to_dict() for doc in docs]
```

## Infrastructure as Code

We use Terraform for consistent, reproducible deployments:

### Main Configuration
```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Vertex AI resources
resource "google_vertex_ai_endpoint" "agent_endpoint" {
  name         = "agent-endpoint"
  display_name = "Agentic AI Endpoint"
  location     = var.region
}

# Cloud Function for agent logic
resource "google_cloudfunctions2_function" "agent_function" {
  name        = "agent-processor"
  location    = var.region
  description = "Main agent processing function"

  build_config {
    runtime     = "python311"
    entry_point = "process_request"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    min_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
    
    environment_variables = {
      PROJECT_ID = var.project_id
      REGION     = var.region
    }
  }
}
```

## Cost Considerations

### Estimated Costs (per month for moderate usage):
* Vertex AI: £40-£150 depending on model usage
* Cloud Functions: £3-£15 for compute time
* Firestore: £8-£25 for storage and operations
* Cloud Storage: £3-£12 for storage
* Pub/Sub: £2-£8 for messaging
* Other services: £5-£20

### Cost Optimisation Strategies:
* Use appropriate model sizes for tasks
* Implement intelligent caching
* Optimise function memory allocation
* Regular cost monitoring and alerts

## Security Best Practices

* Implement least-privilege IAM roles
* Use Secret Manager for sensitive data
* Enable audit logging for all services
* Regular security assessments
* VPC configurations for network isolation
* Encryption at rest and in transit

## Monitoring and Observability

### Cloud Monitoring Setup
```python
from google.cloud import monitoring_v3

def create_agent_metrics():
    """Create custom metrics for agent monitoring."""
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{PROJECT_ID}"
    
    # Define custom metric for agent response time
    descriptor = monitoring_v3.MetricDescriptor(
        type="custom.googleapis.com/agent/response_time",
        metric_kind=monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
        value_type=monitoring_v3.MetricDescriptor.ValueType.DOUBLE,
        description="Agent response time in seconds"
    )
    
    client.create_metric_descriptor(
        name=project_name, 
        metric_descriptor=descriptor
    )
```

## Advanced Features

### Multi-Agent Orchestration
* Implement workflow orchestration with Cloud Workflows
* Design agent specialisation patterns
* Handle complex task decomposition

### Integration Patterns
* Connect to enterprise systems via Cloud Integration
* Implement real-time data processing
* Build custom connectors and APIs

## Next Steps

After completing the GCP section:
* Compare implementation approaches across clouds
* Explore hybrid and multi-cloud architectures
* Learn platform-specific optimisation techniques

## Resources

* [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
* [Cloud Functions Best Practices](https://cloud.google.com/functions/docs/bestpractices)
* [Firestore Data Modelling](https://cloud.google.com/firestore/docs/data-model)