# SharePoint Tool Foundry

A Python-based Azure AI Foundry agent that integrates with SharePoint to provide intelligent document analysis and insights.

## Overview

This project implements an Azure AI agent using the SharePoint tool from Azure AI Foundry Agent Service. The agent can analyze SharePoint documents, summarize content, and provide intelligent responses based on your SharePoint resources.

## Features

- **SharePoint Integration**: Direct connection to SharePoint resources through Azure AI Foundry
- **Document Analysis**: Intelligent analysis and summarization of SharePoint documents
- **Secure Authentication**: Uses Azure Managed Identity for secure access
- **Conversation Threading**: Maintains context across multiple interactions
- **Error Handling**: Robust error handling with proper logging

## Prerequisites

Before running this agent, ensure you have:

1. **Azure AI Foundry Project**: Your project endpoint from the Azure AI Foundry portal
2. **SharePoint Connection**: A configured SharePoint connection in your Azure AI Foundry project
3. **Model Deployment**: A deployed AI model in your Azure AI Foundry project
4. **Python Environment**: Python 3.8+ with required packages

## Environment Variables

Set the following environment variables:

```bash
export PROJECT_ENDPOINT="your-ai-foundry-endpoint"
export SHAREPOINT_RESOURCE_NAME="your-sharepoint-connection-name"
export MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables
4. Run the agent:
   ```bash
   python sharepoint_agent.py
   ```

## Usage

The agent can:
- Summarize SharePoint documents
- Answer questions about document content
- Provide insights from your SharePoint resources
- Maintain conversation context

## Security

This implementation follows Azure security best practices:
- Uses Azure Managed Identity for authentication
- No hardcoded credentials
- Proper error handling and logging
- Secure connection handling

## Architecture

The agent is built using:
- **Azure AI Projects SDK**: For project client management
- **Azure AI Agents SDK**: For agent creation and management
- **SharePoint Tool**: For SharePoint integration
- **Azure Identity**: For secure authentication

## License

MIT License - see LICENSE file for details.
