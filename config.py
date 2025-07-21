"""
SharePoint Tool Foundry Configuration

This module handles configuration management for the SharePoint agent,
including environment variable loading and validation.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for SharePoint Tool Foundry agent."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration by loading environment variables.
        
        Args:
            env_file: Optional path to .env file. If None, uses default .env
        """
        # Load environment variables from .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self._validate_required_vars()
        self._setup_logging()
    
    @property
    def project_endpoint(self) -> str:
        """Azure AI Foundry project endpoint."""
        return os.environ["PROJECT_ENDPOINT"]
    
    @property
    def sharepoint_resource_name(self) -> str:
        """SharePoint connection resource name."""
        return os.environ["SHAREPOINT_RESOURCE_NAME"]
    
    @property
    def model_deployment_name(self) -> str:
        """AI model deployment name."""
        return os.environ["MODEL_DEPLOYMENT_NAME"]
    
    @property
    def debug_logging(self) -> bool:
        """Whether debug logging is enabled."""
        return os.getenv("DEBUG_LOGGING", "false").lower() == "true"
    
    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are set."""
        required_vars = [
            "PROJECT_ENDPOINT",
            "SHAREPOINT_RESOURCE_NAME", 
            "MODEL_DEPLOYMENT_NAME"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please set these variables or create a .env file based on .env.example"
            )
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        level = logging.DEBUG if self.debug_logging else logging.INFO
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('sharepoint_agent.log')
            ]
        )
        
        # Suppress verbose Azure SDK logging unless debug is enabled
        if not self.debug_logging:
            logging.getLogger('azure').setLevel(logging.WARNING)
            logging.getLogger('azure.identity').setLevel(logging.WARNING)
