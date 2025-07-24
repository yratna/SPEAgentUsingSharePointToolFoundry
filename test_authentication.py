"""
Authentication Test Script for SharePoint Tool Foundry

This script demonstrates how to test and verify the authentication flow
without running the full agent.
"""

import os
import logging
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.core.exceptions import ClientAuthenticationError
from config import Config

def test_authentication():
    """Test the authentication flow step by step."""
    
    print("🔐 SharePoint Tool Foundry - Authentication Test")
    print("=" * 60)
    
    try:
        # Step 1: Load configuration
        print("📋 Step 1: Loading configuration...")
        config = Config()
        print(f"✅ Project Endpoint: {config.project_endpoint}")
        print(f"✅ SharePoint Resource: {config.sharepoint_resource_name}")
        print(f"✅ Model Deployment: {config.model_deployment_name}")
        
        # Step 2: Test credential acquisition
        print("\n🎫 Step 2: Testing credential acquisition...")
        credential = DefaultAzureCredential()
        
        # Get token for Cognitive Services scope
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        print(f"✅ Token acquired successfully")
        print(f"✅ Token expires at: {token.expires_on}")
        
        # Step 3: Test AI Project Client
        print("\n🏗️  Step 3: Testing AI Project Client initialization...")
        project_client = AIProjectClient(
            endpoint=config.project_endpoint,
            credential=credential,
        )
        print("✅ AI Project Client initialized successfully")
        
        # Step 4: Test SharePoint connection
        print("\n📁 Step 4: Testing SharePoint connection...")
        try:
            connection = project_client.connections.get(
                name=config.sharepoint_resource_name
            )
            
            if connection:
                print(f"✅ SharePoint connection found: {connection.id}")
                print(f"✅ Connection type: {getattr(connection, 'connection_type', 'Unknown')}")
            else:
                print("❌ SharePoint connection not found")
                return False
                
        except Exception as e:
            print(f"❌ Error accessing SharePoint connection: {e}")
            return False
        
        # Step 5: List all connections (for debugging)
        print("\n📋 Step 5: Listing all available connections...")
        try:
            connections = project_client.connections.list()
            for conn in connections:
                print(f"   - {conn.name}: {conn.id}")
        except Exception as e:
            print(f"⚠️  Could not list connections: {e}")
        
        print("\n🎉 Authentication test completed successfully!")
        return True
        
    except ClientAuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Run 'az login' to authenticate with Azure CLI")
        print("   2. Set up Managed Identity if running on Azure")
        print("   3. Check your Azure permissions")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def show_authentication_info():
    """Show detailed authentication information."""
    
    print("\n🔍 Authentication Environment Information")
    print("=" * 60)
    
    # Check environment variables
    auth_env_vars = [
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET", 
        "AZURE_TENANT_ID",
        "AZURE_USERNAME",
        "AZURE_PASSWORD"
    ]
    
    print("Environment Variables:")
    for var in auth_env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * len(value)}")  # Mask the value
        else:
            print(f"   ❌ {var}: Not set")
    
    # Check Azure CLI status
    print(f"\nAzure CLI Status:")
    try:
        import subprocess
        result = subprocess.run(['az', 'account', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Azure CLI authenticated")
        else:
            print("   ❌ Azure CLI not authenticated")
    except Exception:
        print("   ❌ Azure CLI not available")
    
    # DefaultAzureCredential chain
    print(f"\nDefaultAzureCredential Chain:")
    print("   1. Environment Variables")
    print("   2. Managed Identity")
    print("   3. Azure CLI")
    print("   4. Azure PowerShell")
    print("   5. Interactive Browser")

def main():
    """Main function to run authentication tests."""
    
    # Enable detailed logging for debugging
    logging.basicConfig(level=logging.INFO)
    
    show_authentication_info()
    
    print("\n" + "=" * 60)
    
    success = test_authentication()
    
    if success:
        print(f"\n✅ All authentication tests passed!")
        print(f"✅ The SharePoint agent should work correctly.")
    else:
        print(f"\n❌ Authentication tests failed.")
        print(f"❌ Please resolve authentication issues before using the agent.")

if __name__ == "__main__":
    main()
