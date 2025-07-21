"""
Interactive SharePoint Agent CLI

A command-line interface for interacting with the SharePoint Tool Foundry agent.
Provides an interactive chat experience with conversation history and context.
"""

import logging
import readline
import sys
from typing import List, Optional

from sharepoint_agent import SharePointAgent, AgentResponse
from config import Config


class InteractiveCLI:
    """Interactive command-line interface for the SharePoint agent."""
    
    def __init__(self):
        """Initialize the interactive CLI."""
        self.config = Config()
        self.agent: Optional[SharePointAgent] = None
        self.thread_id: Optional[str] = None
        self.conversation_history: List[dict] = []
        
        # Setup readline for command history
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set editing-mode emacs")
    
    def _setup_agent(self) -> bool:
        """Setup the SharePoint agent."""
        try:
            print("🔄 Initializing SharePoint agent...")
            self.agent = SharePointAgent(self.config)
            self.agent.create_agent(
                name="sharepoint-cli-agent",
                instructions=(
                    "You are a helpful SharePoint assistant. Provide clear, "
                    "detailed responses about SharePoint content. Always cite "
                    "specific documents when possible and be conversational in your tone."
                )
            )
            print("✅ SharePoint agent ready!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    def _print_response(self, response: AgentResponse, query: str) -> None:
        """Print the agent response in a formatted way."""
        # Add to conversation history
        self.conversation_history.append({
            "query": query,
            "response": response.content if response.success else response.error_message,
            "success": response.success,
            "execution_time": response.execution_time
        })
        
        if response.success:
            print(f"\n🤖 Assistant: {response.content}")
            if response.execution_time:
                print(f"⏱️  Response time: {response.execution_time:.2f}s")
        else:
            print(f"\n❌ Error: {response.error_message}")
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
📖 SharePoint Tool Foundry - Help

Available commands:
  - Ask any question about your SharePoint content
  - /help or /h     - Show this help message
  - /history or /hi - Show conversation history
  - /clear or /c    - Clear conversation history
  - /quit or /q     - Exit the application

Example queries:
  - "Summarize the latest project documents"
  - "What are the key points in the quarterly report?"
  - "Show me documents related to budget planning"
  - "Find information about team policies"

Tips:
  - Be specific in your queries for better results
  - Reference document names or types when possible
  - Ask follow-up questions to dive deeper into topics
        """
        print(help_text)
    
    def _show_history(self) -> None:
        """Show conversation history."""
        if not self.conversation_history:
            print("\n📝 No conversation history yet.")
            return
        
        print(f"\n📝 Conversation History ({len(self.conversation_history)} items):")
        print("=" * 60)
        
        for i, item in enumerate(self.conversation_history, 1):
            status = "✅" if item["success"] else "❌"
            print(f"\n{i}. {status} Query: {item['query'][:80]}{'...' if len(item['query']) > 80 else ''}")
            print(f"   Response: {item['response'][:100]}{'...' if len(item['response']) > 100 else ''}")
            if item.get('execution_time'):
                print(f"   Time: {item['execution_time']:.2f}s")
    
    def _clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        print("\n🗑️  Conversation history cleared.")
    
    def run(self) -> None:
        """Run the interactive CLI."""
        print("🚀 SharePoint Tool Foundry - Interactive CLI")
        print("=" * 50)
        print("Welcome! Ask me anything about your SharePoint content.")
        print("Type '/help' for available commands or '/quit' to exit.\n")
        
        # Setup agent
        if not self._setup_agent():
            return
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n💬 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['/quit', '/q']:
                        print("\n👋 Goodbye! Thanks for using SharePoint Tool Foundry.")
                        break
                    
                    elif user_input.lower() in ['/help', '/h']:
                        self._show_help()
                        continue
                    
                    elif user_input.lower() in ['/history', '/hi']:
                        self._show_history()
                        continue
                    
                    elif user_input.lower() in ['/clear', '/c']:
                        self._clear_history()
                        continue
                    
                    # Process query
                    print("🔄 Processing your query...")
                    response = self.agent.query(user_input, self.thread_id)
                    
                    # Store thread ID for conversation continuity
                    if response.thread_id:
                        self.thread_id = response.thread_id
                    
                    self._print_response(response, user_input)
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupted. Type '/quit' to exit properly.")
                    continue
                
                except EOFError:
                    print("\n\n👋 Goodbye!")
                    break
        
        finally:
            # Cleanup
            if self.agent:
                print("\n🔄 Cleaning up...")
                self.agent.cleanup()


def main():
    """Main function for the interactive CLI."""
    try:
        cli = InteractiveCLI()
        cli.run()
    except Exception as e:
        print(f"❌ Application error: {e}")
        logging.error(f"CLI application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
