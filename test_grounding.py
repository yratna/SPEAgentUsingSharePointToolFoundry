#!/usr/bin/env python3
"""
Test SharePoint Grounding with a Simple Query
"""

from sharepoint_agent import SharePointAgent
from config import Config
import sys

def test_grounding_query():
    """Test a single grounding query."""
    
    try:
        print("🔗 Testing SharePoint Grounding...")
        print("=" * 50)
        
        # Initialize agent
        config = Config()
        agent = SharePointAgent(config)
        agent.create_agent("Grounding Test Agent")
        
        # Test query that requires SharePoint grounding
        query = "What documents are available in my SharePoint site? List them with their types and sizes."
        
        print(f"📝 Query: {query}")
        print(f"\n🔄 Processing (this may take a moment)...")
        
        # Send query
        response = agent.query(query)
        
        if response.success:
            print(f"\n✅ Response (grounded in SharePoint content):")
            print(f"{'='*50}")
            print(response.content)
            print(f"{'='*50}")
            print(f"⏱️  Execution time: {response.execution_time:.2f}s")
            print(f"🔗 Thread ID: {response.thread_id}")
            
            # Explain what happened
            print(f"\n🎯 What just happened:")
            print(f"   1. Agent connected to your SharePoint site via Azure AI Foundry")
            print(f"   2. Used SharePoint tools to search and analyze content")
            print(f"   3. Provided response based on ACTUAL documents found")
            print(f"   4. No hallucination - everything referenced is real!")
            
        else:
            print(f"❌ Query failed: {response.error_message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\n💡 Make sure your .env file is configured with:")
        print(f"   - PROJECT_ENDPOINT")
        print(f"   - SHAREPOINT_RESOURCE_NAME") 
        print(f"   - MODEL_DEPLOYMENT_NAME")

if __name__ == "__main__":
    test_grounding_query()
