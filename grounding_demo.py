#!/usr/bin/env python3
"""
SharePoint Grounding Demonstration

This script shows how the SharePoint agent grounds its responses in actual
SharePoint content rather than just providing generic answers.
"""

from sharepoint_agent import SharePointAgent
from config import Config

def demonstrate_grounding():
    """Demonstrate SharePoint grounding capabilities."""
    
    print("🔗 SharePoint Grounding Demonstration")
    print("=" * 60)
    
    try:
        # Initialize the agent (this connects to SharePoint)
        print("1. Initializing SharePoint Agent...")
        config = Config()
        agent = SharePointAgent(config)
        agent.create_agent("SharePoint Grounding Demo")
        print("   ✅ Agent connected to SharePoint")
        
        # Example queries that demonstrate grounding
        grounding_examples = [
            {
                "query": "What documents are available in my SharePoint site?",
                "demonstrates": "Document discovery and listing"
            },
            {
                "query": "Can you summarize the content of any Word documents you find?",
                "demonstrates": "Content analysis and summarization"
            },
            {
                "query": "What types of files are stored in SharePoint and their sizes?",
                "demonstrates": "Metadata analysis"
            },
            {
                "query": "Search for documents containing 'project' or 'meeting'",
                "demonstrates": "Content-based search"
            }
        ]
        
        print(f"\n2. Grounding Examples:")
        print(f"   The following queries will demonstrate how the agent")
        print(f"   grounds responses in actual SharePoint content:\n")
        
        for i, example in enumerate(grounding_examples, 1):
            print(f"   Example {i}: {example['query']}")
            print(f"   Demonstrates: {example['demonstrates']}")
            print()
        
        # Note about what grounding provides
        print("3. What SharePoint Grounding Provides:")
        print("   ✅ Access to real SharePoint documents")
        print("   ✅ Content-based answers (not hallucinations)")
        print("   ✅ Document metadata and properties")
        print("   ✅ Search across SharePoint content")
        print("   ✅ File type and structure analysis")
        print("   ✅ References to specific documents")
        
        print(f"\n4. How to Test Grounding:")
        print(f"   1. Set up your .env file with SharePoint connection")
        print(f"   2. Run: python interactive_cli.py")
        print(f"   3. Ask questions about your SharePoint content")
        print(f"   4. Notice how responses reference actual documents")
        
        print(f"\n🎯 Key Insight:")
        print(f"   Without grounding: 'SharePoint typically contains documents...'")
        print(f"   With grounding: 'I found 5 documents in your site: Project_Plan.docx, Meeting_Notes.pdf...'")
        
    except Exception as e:
        print(f"❌ Error demonstrating grounding: {e}")
        print(f"\n💡 To see grounding in action:")
        print(f"   1. Configure your .env file")
        print(f"   2. Ensure SharePoint connection is set up")
        print(f"   3. Run the interactive CLI")

if __name__ == "__main__":
    demonstrate_grounding()
