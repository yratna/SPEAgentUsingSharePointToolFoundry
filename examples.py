"""
Example usage scenarios for SharePoint Tool Foundry

This module demonstrates various ways to use the SharePoint agent
for different business scenarios and use cases.
"""

import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from sharepoint_agent import SharePointAgent, AgentResponse
from config import Config


@dataclass
class UseCase:
    """Represents a use case with description and sample queries."""
    name: str
    description: str
    queries: List[str]


class SharePointUseCases:
    """Demonstrates various SharePoint agent use cases."""
    
    def __init__(self):
        """Initialize the use cases demo."""
        self.config = Config()
        
        # Define use cases
        self.use_cases = [
            UseCase(
                name="Document Summarization",
                description="Summarize key content from SharePoint documents",
                queries=[
                    "Summarize the main points from the latest quarterly report",
                    "What are the key takeaways from project documentation?",
                    "Provide an executive summary of policy documents"
                ]
            ),
            UseCase(
                name="Content Discovery",
                description="Find and discover relevant content in SharePoint",
                queries=[
                    "What documents are available about budget planning?",
                    "Find all training materials related to new employees",
                    "Show me documents from the last quarter"
                ]
            ),
            UseCase(
                name="Knowledge Extraction",
                description="Extract specific knowledge and insights",
                queries=[
                    "What are the current project deadlines mentioned in documents?",
                    "Extract contact information from team directories",
                    "What are the compliance requirements mentioned in policies?"
                ]
            ),
            UseCase(
                name="Comparative Analysis",
                description="Compare information across multiple documents",
                queries=[
                    "Compare this quarter's performance with last quarter",
                    "How do the new policies differ from previous versions?",
                    "What changes were made in the latest project updates?"
                ]
            ),
            UseCase(
                name="Research Assistance",
                description="Help with research and information gathering",
                queries=[
                    "Research best practices mentioned in our knowledge base",
                    "What expertise areas are covered in our team profiles?",
                    "Find examples of successful project implementations"
                ]
            )
        ]
    
    def demonstrate_use_case(self, use_case: UseCase, agent: SharePointAgent) -> Dict[str, Any]:
        """
        Demonstrate a specific use case with the SharePoint agent.
        
        Args:
            use_case: The use case to demonstrate
            agent: The SharePoint agent instance
            
        Returns:
            Dictionary with use case results
        """
        print(f"\n{'='*60}")
        print(f"🎯 Use Case: {use_case.name}")
        print(f"📝 Description: {use_case.description}")
        print(f"{'='*60}")
        
        results = {
            "use_case": use_case.name,
            "queries": [],
            "total_time": 0.0,
            "success_count": 0
        }
        
        for i, query in enumerate(use_case.queries, 1):
            print(f"\n🔍 Query {i}: {query}")
            print("-" * 40)
            
            response = agent.query(query)
            
            query_result = {
                "query": query,
                "success": response.success,
                "execution_time": response.execution_time or 0.0,
                "content_length": len(response.content) if response.success else 0
            }
            
            if response.success:
                print(f"✅ Response: {response.content[:200]}{'...' if len(response.content) > 200 else ''}")
                print(f"⏱️  Time: {response.execution_time:.2f}s")
                results["success_count"] += 1
            else:
                print(f"❌ Error: {response.error_message}")
            
            results["queries"].append(query_result)
            results["total_time"] += query_result["execution_time"]
        
        # Summary
        success_rate = (results["success_count"] / len(use_case.queries)) * 100
        print(f"\n📊 Use Case Summary:")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Total Time: {results['total_time']:.2f}s")
        print(f"   Average Time: {results['total_time']/len(use_case.queries):.2f}s")
        
        return results
    
    def run_all_use_cases(self) -> Dict[str, Any]:
        """
        Run all use cases and provide comprehensive analysis.
        
        Returns:
            Dictionary with complete results and analysis
        """
        print("🚀 SharePoint Tool Foundry - Use Case Demonstrations")
        print("=" * 60)
        print("This demo showcases various ways to leverage the SharePoint agent")
        print("for different business scenarios and use cases.\n")
        
        all_results = {
            "use_cases": [],
            "overall_stats": {
                "total_queries": 0,
                "total_time": 0.0,
                "total_successes": 0
            }
        }
        
        try:
            with SharePointAgent(self.config) as agent:
                
                for use_case in self.use_cases:
                    result = self.demonstrate_use_case(use_case, agent)
                    all_results["use_cases"].append(result)
                    
                    # Update overall stats
                    all_results["overall_stats"]["total_queries"] += len(result["queries"])
                    all_results["overall_stats"]["total_time"] += result["total_time"]
                    all_results["overall_stats"]["total_successes"] += result["success_count"]
                
                # Final summary
                self._print_final_summary(all_results)
                
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            logging.error(f"Use case demo failed: {e}")
        
        return all_results
    
    def _print_final_summary(self, results: Dict[str, Any]) -> None:
        """Print final summary of all use cases."""
        stats = results["overall_stats"]
        
        print(f"\n{'='*60}")
        print("📈 FINAL SUMMARY")
        print(f"{'='*60}")
        
        print(f"🎯 Use Cases Demonstrated: {len(results['use_cases'])}")
        print(f"❓ Total Queries Processed: {stats['total_queries']}")
        print(f"✅ Successful Responses: {stats['total_successes']}")
        print(f"📊 Overall Success Rate: {(stats['total_successes']/stats['total_queries']*100):.1f}%")
        print(f"⏱️  Total Execution Time: {stats['total_time']:.2f}s")
        print(f"⚡ Average Response Time: {stats['total_time']/stats['total_queries']:.2f}s")
        
        print(f"\n🎉 Demo completed successfully!")
        print("The SharePoint Tool Foundry agent is ready for production use.")
    
    def run_specific_use_case(self, use_case_name: str) -> bool:
        """
        Run a specific use case by name.
        
        Args:
            use_case_name: Name of the use case to run
            
        Returns:
            True if use case was found and executed, False otherwise
        """
        for use_case in self.use_cases:
            if use_case.name.lower() == use_case_name.lower():
                try:
                    with SharePointAgent(self.config) as agent:
                        self.demonstrate_use_case(use_case, agent)
                    return True
                except Exception as e:
                    print(f"❌ Failed to run use case: {e}")
                    return False
        
        print(f"❌ Use case '{use_case_name}' not found.")
        print("Available use cases:")
        for use_case in self.use_cases:
            print(f"  - {use_case.name}")
        return False


def main():
    """Main function for running use case demonstrations."""
    import sys
    
    demo = SharePointUseCases()
    
    if len(sys.argv) > 1:
        # Run specific use case
        use_case_name = " ".join(sys.argv[1:])
        demo.run_specific_use_case(use_case_name)
    else:
        # Run all use cases
        demo.run_all_use_cases()


if __name__ == "__main__":
    main()
