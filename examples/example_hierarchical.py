"""
Hierarchical Processing Example

Demonstrates Use Case 3: Hierarchical Orchestration

This example shows how to use a coordinator agent that:
1. Analyzes the overall task
2. Delegates to specialized worker agents
3. Synthesizes the results

The coordinator supervises and manages worker agents,
making strategic decisions about task allocation.
"""

import asyncio
import logging
from core.types import Task, AgentRole
from orchestrators.hierarchical import HierarchicalOrchestrator
from agents.researcher import ResearcherAgent
from agents.analyzer import AnalyzerAgent
from agents.writer import WriterAgent
from agents.coordinator import CoordinatorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run hierarchical orchestration example"""

    print("\n" + "=" * 70)
    print("HIERARCHICAL ORCHESTRATION EXAMPLE - Use Case 3")
    print("=" * 70)
    print("\nDemonstrating hierarchical processing with coordinator managing workers:")
    print("Coordinator → (Research + Analyze + Write) → Synthesize\n")

    # Create agents
    coordinator = CoordinatorAgent(agent_id="coordinator")
    researcher = ResearcherAgent(agent_id="researcher")
    analyzer = AnalyzerAgent(agent_id="analyzer")
    writer = WriterAgent(agent_id="writer")

    # Create orchestrator with agents
    agents = {
        "coordinator": coordinator,
        "researcher": researcher,
        "analyzer": analyzer,
        "writer": writer
    }

    orchestrator = HierarchicalOrchestrator(
        orchestrator_id="hier_example_1",
        agents=agents,
        coordinator_id="coordinator"
    )

    # Define hierarchical tasks
    tasks = [
        Task(
            task_id="research_hier",
            description="Gather comprehensive information about enterprise AI adoption challenges.",
            agent_role=AgentRole.RESEARCHER,
            parameters={"topic": "enterprise AI adoption"}
        ),
        Task(
            task_id="analyze_hier",
            description="Analyze the key challenges and identify common patterns.",
            agent_role=AgentRole.ANALYZER,
            parameters={"focus": "adoption challenges"}
        ),
        Task(
            task_id="write_hier",
            description="Create a strategic roadmap for addressing these challenges.",
            agent_role=AgentRole.WRITER,
            parameters={"format": "strategic roadmap"}
        )
    ]

    # Execute orchestration
    print("Starting hierarchical execution...\n")
    result = await orchestrator.orchestrate(tasks)

    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nStrategy: {result.strategy.value}")
    print(f"Total Execution Time: {result.total_execution_time:.2f}s")
    print(f"Number of Agents: {len(result.agent_responses)}")
    print(f"Coordinator: coordinator")
    print(f"Workers: researcher, analyzer, writer")

    print("\n" + "-" * 70)
    print("OUTPUT")
    print("-" * 70)
    print(result.final_output)

    print("\n" + "-" * 70)
    print("EXECUTION PHASES")
    print("-" * 70)
    print(f"Coordination Phase: {result.agent_responses[0].execution_time:.2f}s")
    print(f"Worker Phase: {sum(r.execution_time for r in result.agent_responses[1:-1]):.2f}s")
    print(f"Synthesis Phase: {result.agent_responses[-1].execution_time:.2f}s")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

