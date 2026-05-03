"""
Sequential Processing Example

Demonstrates Use Case 1: Sequential Orchestration

This example shows how to use agents in a pipeline where:
1. Researcher gathers information about a topic
2. Analyzer interprets the research findings
3. Writer creates a final summary

Each agent receives the output from the previous agent as context.
"""

import asyncio
import logging
from core.types import Task, AgentRole, OrchestrationStrategy
from orchestrators.sequential import SequentialOrchestrator
from agents.researcher import ResearcherAgent
from agents.analyzer import AnalyzerAgent
from agents.writer import WriterAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run sequential orchestration example"""

    print("\n" + "=" * 70)
    print("SEQUENTIAL ORCHESTRATION EXAMPLE - Use Case 1")
    print("=" * 70)
    print("\nDemonstrating sequential processing with agents working in sequence:")
    print("Research → Analyze → Write\n")

    # Create agents
    researcher = ResearcherAgent(agent_id="researcher")
    analyzer = AnalyzerAgent(agent_id="analyzer")
    writer = WriterAgent(agent_id="writer")

    # Create orchestrator with agents
    agents = {
        "researcher": researcher,
        "analyzer": analyzer,
        "writer": writer
    }

    orchestrator = SequentialOrchestrator(
        orchestrator_id="seq_example_1",
        agents=agents
    )

    # Define sequential tasks
    tasks = [
        Task(
            task_id="research_1",
            description="Research the latest developments in artificial intelligence for 2026.",
            agent_role=AgentRole.RESEARCHER,
            parameters={"topic": "AI trends 2026", "focus": "latest developments"}
        ),
        Task(
            task_id="analyze_1",
            description="Based on the research, analyze the key trends and their implications for the industry.",
            agent_role=AgentRole.ANALYZER,
            parameters={"analyze_focus": "trends and implications"}
        ),
        Task(
            task_id="write_1",
            description="Create a comprehensive summary report of the research and analysis.",
            agent_role=AgentRole.WRITER,
            parameters={"format": "report", "length": "medium"}
        )
    ]

    # Execute orchestration
    print("Starting sequential execution...\n")
    result = await orchestrator.orchestrate(tasks)

    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nStrategy: {result.strategy.value}")
    print(f"Total Execution Time: {result.total_execution_time:.2f}s")
    print(f"Number of Agents: {len(result.agent_responses)}")

    print("\n" + "-" * 70)
    print("OUTPUT")
    print("-" * 70)
    print(result.final_output)

    print("\n" + "-" * 70)
    print("AGENT STATISTICS")
    print("-" * 70)
    for response in result.agent_responses:
        status_symbol = "✓" if response.status == "success" else "✗"
        print(f"{status_symbol} {response.agent_id}: {response.execution_time:.2f}s")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

