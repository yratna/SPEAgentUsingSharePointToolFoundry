"""
Unit tests for SharePoint Tool Foundry

Test suite covering the main functionality of the SharePoint agent,
configuration management, and error handling scenarios.
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

from config import Config
from sharepoint_agent import SharePointAgent, AgentResponse


class TestConfig(unittest.TestCase):
    """Test cases for configuration management."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_env_vars = {
            "PROJECT_ENDPOINT": "https://test-endpoint.com",
            "SHAREPOINT_RESOURCE_NAME": "test-sharepoint-connection",
            "MODEL_DEPLOYMENT_NAME": "test-model",
            "DEBUG_LOGGING": "true"
        }
    
    @patch.dict(os.environ, {"PROJECT_ENDPOINT": "https://test.com", 
                             "SHAREPOINT_RESOURCE_NAME": "test-sp",
                             "MODEL_DEPLOYMENT_NAME": "test-model"})
    def test_config_initialization_success(self):
        """Test successful configuration initialization."""
        config = Config()
        self.assertEqual(config.project_endpoint, "https://test.com")
        self.assertEqual(config.sharepoint_resource_name, "test-sp")
        self.assertEqual(config.model_deployment_name, "test-model")
    
    def test_config_missing_variables(self):
        """Test configuration with missing required variables."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.load_dotenv'):  # Mock dotenv to not load from .env file
                with self.assertRaises(ValueError) as context:
                    Config()
                self.assertIn("Missing required environment variables", str(context.exception))
    
    @patch.dict(os.environ, {"PROJECT_ENDPOINT": "https://test.com",
                             "SHAREPOINT_RESOURCE_NAME": "test-sp", 
                             "MODEL_DEPLOYMENT_NAME": "test-model",
                             "DEBUG_LOGGING": "true"})
    def test_debug_logging_enabled(self):
        """Test debug logging configuration."""
        config = Config()
        self.assertTrue(config.debug_logging)
    
    def test_env_file_loading(self):
        """Test loading configuration from .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("PROJECT_ENDPOINT=https://file-test.com\n")
            f.write("SHAREPOINT_RESOURCE_NAME=file-sp\n")
            f.write("MODEL_DEPLOYMENT_NAME=file-model\n")
            env_file = f.name
        
        try:
            config = Config(env_file)
            self.assertEqual(config.project_endpoint, "https://file-test.com")
            self.assertEqual(config.sharepoint_resource_name, "file-sp")
            self.assertEqual(config.model_deployment_name, "file-model")
        finally:
            os.unlink(env_file)


class TestSharePointAgent(unittest.TestCase):
    """Test cases for SharePoint agent functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_config.project_endpoint = "https://test-endpoint.com"
        self.mock_config.sharepoint_resource_name = "test-sharepoint"
        self.mock_config.model_deployment_name = "test-model"
        self.mock_config.debug_logging = False
    
    @patch('sharepoint_agent.AIProjectClient')
    @patch('sharepoint_agent.DefaultAzureCredential')
    def test_agent_initialization_success(self, mock_credential, mock_client):
        """Test successful agent initialization."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.agents = Mock()
        
        agent = SharePointAgent(self.mock_config)
        
        self.assertIsNotNone(agent.project_client)
        self.assertIsNotNone(agent.agents_client)
        mock_client.assert_called_once_with(
            endpoint=self.mock_config.project_endpoint,
            credential=mock_credential.return_value
        )
    
    @patch('sharepoint_agent.AIProjectClient')
    @patch('sharepoint_agent.DefaultAzureCredential')
    def test_agent_initialization_auth_failure(self, mock_credential, mock_client):
        """Test agent initialization with authentication failure."""
        from azure.core.exceptions import ClientAuthenticationError
        
        mock_client.side_effect = ClientAuthenticationError("Auth failed")
        
        with self.assertRaises(RuntimeError) as context:
            SharePointAgent(self.mock_config)
        
        self.assertIn("Failed to authenticate", str(context.exception))
    
    @patch('sharepoint_agent.AIProjectClient')
    @patch('sharepoint_agent.DefaultAzureCredential')
    def test_sharepoint_tool_setup(self, mock_credential, mock_client):
        """Test SharePoint tool setup."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.agents = Mock()
        
        mock_connection = Mock()
        mock_connection.id = "test-connection-id"
        mock_client_instance.connections.get.return_value = mock_connection
        
        with patch('sharepoint_agent.SharepointTool') as mock_sharepoint_tool:
            agent = SharePointAgent(self.mock_config)
            agent._setup_sharepoint_tool()
            
            mock_client_instance.connections.get.assert_called_once_with(
                name=self.mock_config.sharepoint_resource_name
            )
            mock_sharepoint_tool.assert_called_once_with(connection_id="test-connection-id")
    
    @patch('sharepoint_agent.AIProjectClient')
    @patch('sharepoint_agent.DefaultAzureCredential')
    def test_create_agent_success(self, mock_credential, mock_client):
        """Test successful agent creation."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_agents_client = Mock()
        mock_client_instance.agents = mock_agents_client
        
        mock_connection = Mock()
        mock_connection.id = "test-connection-id"
        mock_client_instance.connections.get.return_value = mock_connection
        
        mock_agent = Mock()
        mock_agent.id = "test-agent-id"
        mock_agents_client.create_agent.return_value = mock_agent
        
        with patch('sharepoint_agent.SharepointTool') as mock_sharepoint_tool:
            mock_tool_instance = Mock()
            mock_tool_instance.definitions = ["tool-def"]
            mock_sharepoint_tool.return_value = mock_tool_instance
            
            agent = SharePointAgent(self.mock_config)
            agent.create_agent("test-agent", "test instructions")
            
            mock_agents_client.create_agent.assert_called_once_with(
                model=self.mock_config.model_deployment_name,
                name="test-agent",
                instructions="test instructions", 
                tools=["tool-def"]
            )
            self.assertEqual(agent.agent, mock_agent)
    
    @patch('sharepoint_agent.AIProjectClient')
    @patch('sharepoint_agent.DefaultAzureCredential')
    def test_query_success(self, mock_credential, mock_client):
        """Test successful query execution."""
        # Setup comprehensive mocks
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_agents_client = Mock()
        mock_client_instance.agents = mock_agents_client
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.id = "test-connection-id"
        mock_client_instance.connections.get.return_value = mock_connection
        
        # Mock agent creation
        mock_agent = Mock()
        mock_agent.id = "test-agent-id"
        mock_agents_client.create_agent.return_value = mock_agent
        
        # Mock thread operations
        mock_thread = Mock()
        mock_thread.id = "test-thread-id"
        mock_agents_client.threads.create.return_value = mock_thread
        
        # Mock message operations
        mock_message = Mock()
        mock_message.id = "test-message-id"
        mock_agents_client.messages.create.return_value = mock_message
        
        # Mock run operations
        mock_run = Mock()
        mock_run.id = "test-run-id"
        mock_run.status = "completed"
        mock_agents_client.runs.create_and_process.return_value = mock_run
        
        # Mock message retrieval
        mock_response_message = Mock()
        mock_response_message.role = "assistant"
        mock_text_message = Mock()
        mock_text_message.text.value = "Test response"
        mock_response_message.text_messages = [mock_text_message]
        mock_agents_client.messages.list.return_value = [mock_response_message]
        
        with patch('sharepoint_agent.SharepointTool') as mock_sharepoint_tool:
            mock_tool_instance = Mock()
            mock_tool_instance.definitions = ["tool-def"]
            mock_sharepoint_tool.return_value = mock_tool_instance
            
            agent = SharePointAgent(self.mock_config)
            response = agent.query("Test question")
            
            self.assertTrue(response.success)
            self.assertEqual(response.content, "Test response")
            self.assertEqual(response.run_id, "test-run-id")
            self.assertIsNotNone(response.execution_time)


class TestAgentResponse(unittest.TestCase):
    """Test cases for AgentResponse dataclass."""
    
    def test_agent_response_success(self):
        """Test successful response creation."""
        response = AgentResponse(
            success=True,
            content="Test content",
            run_id="test-run-id",
            thread_id="thread_abc123",
            execution_time=1.5
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.content, "Test content")
        self.assertEqual(response.run_id, "test-run-id")
        self.assertEqual(response.thread_id, "thread_abc123")
        self.assertEqual(response.execution_time, 1.5)
        self.assertIsNone(response.error_message)
    
    def test_agent_response_failure(self):
        """Test failure response creation."""
        response = AgentResponse(
            success=False,
            content="",
            thread_id="thread_abc123",
            error_message="Test error",
            execution_time=0.5
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.content, "")
        self.assertEqual(response.thread_id, "thread_abc123")
        self.assertEqual(response.error_message, "Test error")
        self.assertEqual(response.execution_time, 0.5)
        self.assertIsNone(response.run_id)


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end functionality."""
    
    @patch.dict(os.environ, {
        "PROJECT_ENDPOINT": "https://test-endpoint.com",
        "SHAREPOINT_RESOURCE_NAME": "test-sharepoint", 
        "MODEL_DEPLOYMENT_NAME": "test-model"
    })
    @patch('sharepoint_agent.AIProjectClient')
    @patch('sharepoint_agent.DefaultAzureCredential')
    def test_end_to_end_workflow(self, mock_credential, mock_client):
        """Test complete workflow from configuration to query."""
        # Setup mocks for complete workflow
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_agents_client = Mock()
        mock_client_instance.agents = mock_agents_client
        
        # Mock all required operations
        mock_connection = Mock()
        mock_connection.id = "test-connection-id"
        mock_client_instance.connections.get.return_value = mock_connection
        
        mock_agent = Mock()
        mock_agent.id = "test-agent-id"
        mock_agents_client.create_agent.return_value = mock_agent
        
        mock_thread = Mock()
        mock_thread.id = "test-thread-id"
        mock_agents_client.threads.create.return_value = mock_thread
        
        mock_message = Mock()
        mock_message.id = "test-message-id"
        mock_agents_client.messages.create.return_value = mock_message
        
        mock_run = Mock()
        mock_run.id = "test-run-id"
        mock_run.status = "completed"
        mock_agents_client.runs.create_and_process.return_value = mock_run
        
        mock_response_message = Mock()
        mock_response_message.role = "assistant"
        mock_text_message = Mock()
        mock_text_message.text.value = "Integration test response"
        mock_response_message.text_messages = [mock_text_message]
        mock_agents_client.messages.list.return_value = [mock_response_message]
        
        with patch('sharepoint_agent.SharepointTool') as mock_sharepoint_tool:
            mock_tool_instance = Mock()
            mock_tool_instance.definitions = ["tool-def"]
            mock_sharepoint_tool.return_value = mock_tool_instance
            
            # Run complete workflow
            config = Config()
            with SharePointAgent(config) as agent:
                response = agent.query("Integration test query")
                
                self.assertTrue(response.success)
                self.assertEqual(response.content, "Integration test response")
                self.assertIsNotNone(response.execution_time)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
