"""
SharePoint Tool Foundry Agent

A comprehensive Azure AI agent that integrates with SharePoint to provide
intelligent document analysis and insights using Azure AI Foundry Agent Service.

This implementation follows Azure security best practices:
- Uses Azure Managed Identity for authentication
- Implements proper error handling and retry logic
- Includes comprehensive logging and monitoring
- Follows secure connection patterns
"""

import os
import logging
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import SharepointTool
from azure.core.exceptions import (
    ResourceNotFoundError,
    ServiceRequestError,
    ClientAuthenticationError
)

from config import Config


@dataclass
class AgentResponse:
    """Structured response from the SharePoint agent."""
    success: bool
    content: str
    run_id: Optional[str] = None
    thread_id: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class SharePointAgent:
    """
    Azure AI Foundry agent with SharePoint integration.
    
    This agent can analyze SharePoint documents, provide summaries,
    and answer questions about SharePoint content using Azure AI capabilities.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the SharePoint agent.
        
        Args:
            config: Configuration object with Azure settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.project_client: Optional[AIProjectClient] = None
        self.agents_client = None
        self.agent = None
        self.sharepoint_tool = None
        
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize Azure AI clients with proper error handling."""
        try:
            self.logger.info("Initializing Azure AI Project client...")
            
            # Initialize the AIProjectClient with managed identity
            self.project_client = AIProjectClient(
                endpoint=self.config.project_endpoint,
                credential=DefaultAzureCredential(),
            )
            
            self.agents_client = self.project_client.agents
            self.logger.info("Successfully initialized Azure AI clients")
            
        except ClientAuthenticationError as e:
            self.logger.error(f"Authentication failed: {e}")
            raise RuntimeError(
                "Failed to authenticate with Azure. Ensure you have proper permissions "
                "and Azure credentials are configured."
            ) from e
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure clients: {e}")
            raise RuntimeError(f"Client initialization failed: {e}") from e
    
    def _setup_sharepoint_tool(self) -> None:
        """Setup SharePoint tool with connection validation."""
        try:
            self.logger.info(f"Setting up SharePoint tool with connection: {self.config.sharepoint_resource_name}")
            
            # Get SharePoint connection
            connection = self.project_client.connections.get(
                name=self.config.sharepoint_resource_name
            )
            
            if not connection:
                raise ResourceNotFoundError(
                    f"SharePoint connection '{self.config.sharepoint_resource_name}' not found"
                )
            
            self.logger.info(f"Found SharePoint connection with ID: {connection.id}")
            
            # Initialize SharePoint tool with connection
            self.sharepoint_tool = SharepointTool(connection_id=connection.id)
            self.logger.info("Successfully setup SharePoint tool")
            
        except ResourceNotFoundError as e:
            self.logger.error(f"SharePoint connection not found: {e}")
            raise RuntimeError(
                f"SharePoint connection '{self.config.sharepoint_resource_name}' not found. "
                f"Please verify the connection name in your Azure AI Foundry project."
            ) from e
        except Exception as e:
            self.logger.error(f"Failed to setup SharePoint tool: {e}")
            raise RuntimeError(f"SharePoint tool setup failed: {e}") from e
    
    def create_agent(self, 
                    name: str = "sharepoint-agent",
                    instructions: str = None) -> None:
        """
        Create an AI agent with SharePoint tool enabled.
        
        Args:
            name: Name for the agent
            instructions: Custom instructions for the agent behavior
        """
        try:
            if not self.sharepoint_tool:
                self._setup_sharepoint_tool()
            
            if not instructions:
                instructions = (
                    "You are a helpful AI assistant specialized in analyzing SharePoint content. "
                    "You can summarize documents, answer questions about SharePoint resources, "
                    "and provide insights based on the content available. Always be thorough "
                    "and provide specific references to the documents you analyze."
                )
            
            self.logger.info(f"Creating agent '{name}' with SharePoint tool...")
            
            self.agent = self.agents_client.create_agent(
                model=self.config.model_deployment_name,
                name=name,
                instructions=instructions,
                tools=self.sharepoint_tool.definitions,
            )
            
            self.logger.info(f"Successfully created agent with ID: {self.agent.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create agent: {e}")
            raise RuntimeError(f"Agent creation failed: {e}") from e
    
    def _create_thread(self) -> str:
        """Create a new conversation thread."""
        try:
            thread = self.agents_client.threads.create()
            self.logger.debug(f"Created thread with ID: {thread.id}")
            return thread.id
        except Exception as e:
            self.logger.error(f"Failed to create thread: {e}")
            raise RuntimeError(f"Thread creation failed: {e}") from e
    
    def _send_message(self, thread_id: str, content: str) -> str:
        """Send a message to the thread."""
        try:
            message = self.agents_client.messages.create(
                thread_id=thread_id,
                role="user",
                content=content,
            )
            self.logger.debug(f"Created message with ID: {message.id}")
            return message.id
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise RuntimeError(f"Message sending failed: {e}") from e
    
    def _execute_run_with_retry(self, thread_id: str, max_retries: int = 3) -> Any:
        """Execute agent run with retry logic for transient failures."""
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Executing run (attempt {attempt + 1}/{max_retries})")
                
                run = self.agents_client.runs.create_and_process(
                    thread_id=thread_id, 
                    agent_id=self.agent.id
                )
                
                return run
                
            except ServiceRequestError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(
                        f"Transient error on attempt {attempt + 1}: {e}. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Non-retryable error during run execution: {e}")
                raise
    
    def _get_response_content(self, thread_id: str) -> str:
        """Extract the response content from the thread messages."""
        try:
            messages = self.agents_client.messages.list(thread_id=thread_id)
            
            # Find the latest assistant message
            for message in messages:
                if message.role == "assistant" and message.text_messages:
                    last_text = message.text_messages[-1]
                    return last_text.text.value
            
            return "No response received from agent"
            
        except Exception as e:
            self.logger.error(f"Failed to get response content: {e}")
            return f"Error retrieving response: {e}"
    
    def query(self, 
              question: str, 
              thread_id: Optional[str] = None) -> AgentResponse:
        """
        Query the SharePoint agent with a question.
        
        Args:
            question: The question to ask the agent
            thread_id: Optional existing thread ID for conversation continuity
            
        Returns:
            AgentResponse with the agent's response and metadata
        """
        start_time = time.time()
        
        try:
            if not self.agent:
                self.create_agent()
            
            # Create or use existing thread
            if not thread_id:
                thread_id = self._create_thread()
            
            # Send message
            message_id = self._send_message(thread_id, question)
            
            # Execute run with retry logic
            run = self._execute_run_with_retry(thread_id)
            
            execution_time = time.time() - start_time
            
            if run.status == "completed":
                content = self._get_response_content(thread_id)
                
                self.logger.info(
                    f"Successfully processed query in {execution_time:.2f}s. "
                    f"Run ID: {run.id}"
                )
                
                return AgentResponse(
                    success=True,
                    content=content,
                    run_id=run.id,
                    thread_id=thread_id,
                    execution_time=execution_time
                )
            
            elif run.status == "failed":
                error_msg = f"Agent run failed: {run.last_error if run.last_error else 'Unknown error'}"
                self.logger.error(error_msg)
                
                return AgentResponse(
                    success=False,
                    content="",
                    run_id=run.id,
                    thread_id=thread_id,
                    error_message=error_msg,
                    execution_time=execution_time
                )
            
            else:
                error_msg = f"Unexpected run status: {run.status}"
                self.logger.warning(error_msg)
                
                return AgentResponse(
                    success=False,
                    content="",
                    run_id=run.id,
                    thread_id=thread_id,
                    error_message=error_msg,
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Query execution failed: {e}"
            self.logger.error(error_msg)
            
            return AgentResponse(
                success=False,
                content="",
                thread_id=thread_id,
                error_message=error_msg,
                execution_time=execution_time
            )
    
    def cleanup(self) -> None:
        """Clean up resources by deleting the agent."""
        try:
            if self.agent and self.agents_client:
                self.agents_client.delete_agent(self.agent.id)
                self.logger.info(f"Deleted agent with ID: {self.agent.id}")
                self.agent = None
        except Exception as e:
            self.logger.warning(f"Failed to cleanup agent: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()


def main():
    """Main function demonstrating SharePoint agent usage."""
    try:
        # Load configuration
        config = Config()
        
        # Create and use the SharePoint agent
        with SharePointAgent(config) as agent:
            
            # Example queries
            queries = [
                "Hello, can you help me summarize key points from SharePoint documents?",
                "What types of documents are available in our SharePoint resources?",
                "Can you provide insights from the most recent documents?"
            ]
            
            print("SharePoint Tool Foundry Agent - Demo")
            print("=" * 50)
            
            for i, query in enumerate(queries, 1):
                print(f"\nQuery {i}: {query}")
                print("-" * 30)
                
                response = agent.query(query)
                
                if response.success:
                    print(f"Response: {response.content}")
                    print(f"Execution time: {response.execution_time:.2f}s")
                else:
                    print(f"Error: {response.error_message}")
                
                # Small delay between queries
                time.sleep(1)
                
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
