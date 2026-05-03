"""
Parallel Processing Example

Demonstrates Use Case 2: Parallel Orchestration

This example shows how to use agents in parallel where:
1. Researcher gathers information
2. Analyzer examines trends
3. Writer creates insights

All agents work simultaneously on independent tasks,
and results are aggregated at the end.
"""

import asyncio
import logging
from core.types import Task, AgentRole
from orchestrators.parallel import ParallelOrchestrator
from agents.researcher import ResearcherAgent
from agents.analyzer import AnalyzerAgent
from agents.writer import WriterAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run parallel orchestration example"""

    print("\n" + "=" * 70)
    print("PARALLEL ORCHESTRATION EXAMPLE - Use Case 2")
    print("=" * 70)
    print("\nDemonstrating parallel processing with agents working simultaneously:")
    print("(Research + Analyze + Write) → Aggregate Results\n")

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

    orchestrator = ParallelOrchestrator(
        orchestrator_id="par_example_1",
        agents=agents
    )

    # Define parallel tasks (all independent)
    tasks = [
        Task(
            task_id="research_parallel",
            description="Research the impact of generative AI on software development in 2026.",
            agent_role=AgentRole.RESEARCHER,
            parameters={"topic": "generative AI and software development"}
        ),
        Task(
            task_id="analyze_parallel",
            description="Analyze the emerging patterns in multi-agent AI systems and their applications.",
            agent_role=AgentRole.ANALYZER,
            parameters={"focus": "multi-agent AI patterns"}
        ),
        Task(
            task_id="write_parallel",
            description="Write an executive summary about the future of AI orchestration.",
            agent_role=AgentRole.WRITER,
            parameters={"format": "executive summary"}
        )
    ]

    # Execute orchestration
    print("Starting parallel execution...\n")
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
    print("EFFICIENCY ANALYSIS")
    print("-" * 70)
    total_individual_time = sum(r.execution_time for r in result.agent_responses)
    parallel_speedup = total_individual_time / result.total_execution_time
    print(f"Total individual execution time: {total_individual_time:.2f}s")
    print(f"Parallel execution time: {result.total_execution_time:.2f}s")
    print(f"Speedup from parallelization: {parallel_speedup:.2f}x")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

