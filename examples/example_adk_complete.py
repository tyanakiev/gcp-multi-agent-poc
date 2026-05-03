"""
Complete ADK Implementation Example

This example demonstrates the complete Google Cloud ADK pattern with:
1. Agent creation with tools
2. Tool configuration and usage
3. Async execution patterns
4. Error handling and logging
5. Multi-agent coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from core.agent import Agent
from core.types import AgentRole, Task, OrchestrationResult
from core.adk_tools import (
    WebSearchTool,
    DataAnalysisTool,
    ContentGenerationTool,
    ToolDefinition
)
from orchestrators.sequential import SequentialOrchestrator


# ============================================================================
# PART 1: ADK AGENT DEFINITIONS
# ============================================================================

class ResearcherWithADK(Agent):
    """
    Researcher agent using Google Cloud ADK with web search capabilities.

    Pattern:
    --------
    agent = Agent(
        name="researcher",
        model="gemini-2.0-flash",
        instruction="Research topics thoroughly",
        tools=[web_search],
    )
    """

    def __init__(self, agent_id: str = "researcher_adk"):
        logger.info(f"Initializing {agent_id} with ADK pattern")
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            instruction="""You are an expert researcher using Google Cloud ADK.
Your role is to:
1. Use available tools to gather comprehensive information
2. Synthesize findings into clear summaries
3. Cite sources and provide references
4. Identify key patterns and themes

Available Tools:
- web_search: Search for information online
- analyze_data: Analyze data patterns

Approach research systematically and provide thorough, accurate information.""",
            model="gemini-2.0-flash",
            tools=[WebSearchTool.definition()]
        )

    def get_description(self) -> str:
        return "ADK Researcher: Uses web search and analysis tools for research"


class AnalystWithADK(Agent):
    """
    Analyst agent using ADK with data analysis tools.
    """

    def __init__(self, agent_id: str = "analyst_adk"):
        logger.info(f"Initializing {agent_id} with ADK pattern")
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYZER,
            instruction="""You are an expert analyst using Google Cloud ADK.
Your role is to:
1. Analyze structured and unstructured data
2. Identify patterns, trends, and anomalies
3. Generate insights and recommendations
4. Create visualizations and summaries

Available Tools:
- analyze_data: Perform statistical and trend analysis
- summarize_document: Summarize complex documents

Provide clear, data-driven analysis with actionable insights.""",
            model="gemini-2.0-flash",
            tools=[
                DataAnalysisTool.definition(),
            ]
        )

    def get_description(self) -> str:
        return "ADK Analyst: Uses data analysis and summarization tools"


class WriterWithADK(Agent):
    """
    Writer agent using ADK with content generation tools.
    """

    def __init__(self, agent_id: str = "writer_adk"):
        logger.info(f"Initializing {agent_id} with ADK pattern")
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.WRITER,
            instruction="""You are an expert writer using Google Cloud ADK.
Your role is to:
1. Create well-structured, engaging content
2. Synthesize information from multiple sources
3. Adapt tone and style for different audiences
4. Ensure clarity and readability

Available Tools:
- generate_content: Generate formatted content in various styles

Produce professional, polished written content that communicates clearly.""",
            model="gemini-2.0-flash",
            tools=[ContentGenerationTool.definition()]
        )

    def get_description(self) -> str:
        return "ADK Writer: Uses content generation tools for writing"


# ============================================================================
# PART 2: ASYNC EXECUTION EXAMPLES
# ============================================================================

async def execute_single_agent_example():
    """Example: Execute a single ADK agent with tools"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Single ADK Agent Execution")
    print("=" * 70)

    researcher = ResearcherWithADK()

    print(f"\nAgent Details:")
    print(f"  ID: {researcher.agent_id}")
    print(f"  Role: {researcher.role.value}")
    print(f"  Model: {researcher.model}")
    print(f"  Tools Available: {len(researcher.tools)}")
    print(f"  Description: {researcher.get_description()}")

    # Note: Requires GOOGLE_API_KEY to actually execute
    print("\nTo execute agent:")
    print("  1. Set GOOGLE_API_KEY environment variable")
    print("  2. Uncomment execution code below")

    # Uncomment to execute:
    # response = await researcher.execute(
    #     task="Research the latest developments in AI and machine learning",
    #     context={"focus_area": "LLMs", "time_period": "last 6 months"}
    # )
    # print(f"\nExecution Status: {response.status}")
    # print(f"Execution Time: {response.execution_time:.2f}s")
    # print(f"Output:\n{response.output}")


async def execute_agent_pipeline_example():
    """Example: Execute agents in a pipeline (Sequential Orchestration)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Multi-Agent Pipeline with ADK")
    print("=" * 70)

    # Create agents
    researcher = ResearcherWithADK("researcher_1")
    analyst = AnalystWithADK("analyst_1")
    writer = WriterWithADK("writer_1")

    # Create orchestrator
    agents = {
        "researcher": researcher,
        "analyst": analyst,
        "writer": writer
    }

    orchestrator = SequentialOrchestrator(
        orchestrator_id="adk_pipeline_example",
        agents=agents
    )

    print("\nPipeline Configuration:")
    print(f"  Orchestrator: {orchestrator.orchestrator_id}")
    print(f"  Strategy: {orchestrator.strategy.value}")
    print(f"  Agents: {len(orchestrator.agents)}")

    for agent_id, agent in agents.items():
        print(f"\n  Agent: {agent_id}")
        print(f"    Role: {agent.role.value}")
        print(f"    Tools: {len(agent.tools)}")
        print(f"    Description: {agent.get_description()}")

    print("\nPipeline Flow: Research → Analyze → Write")
    print("\nTo execute pipeline:")
    print("  1. Set GOOGLE_API_KEY environment variable")
    print("  2. Define tasks and call orchestrator.orchestrate(tasks)")


async def execute_parallel_agents_example():
    """Example: Execute multiple agents in parallel"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Parallel Agent Execution with ADK")
    print("=" * 70)

    # Create multiple agent instances
    researchers = [
        ResearcherWithADK(f"researcher_{i}")
        for i in range(3)
    ]

    print(f"\nCreated {len(researchers)} parallel researchers")
    print("Each with:")
    print("  - Web search tool")
    print("  - Data analysis capability")
    print("  - Async execution support")

    print("\nTo execute in parallel:")
    print("  tasks = [agent.execute(task) for agent in researchers]")
    print("  results = await asyncio.gather(*tasks)")


async def demonstrate_tool_usage():
    """Example: Demonstrate available tools"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: ADK Tools Overview")
    print("=" * 70)

    agents_with_tools = [
        ("Researcher", ResearcherWithADK()),
        ("Analyst", AnalystWithADK()),
        ("Writer", WriterWithADK()),
    ]

    for name, agent in agents_with_tools:
        print(f"\n{name} Agent ({agent.agent_id}):")
        print(f"  Role: {agent.role.value}")
        print(f"  Available Tools: {len(agent.tools)}")

        for i, tool in enumerate(agent.tools, 1):
            print(f"    {i}. {tool.name}")
            print(f"       Description: {tool.description}")
            print(f"       Parameters: {list(tool.parameters.keys())}")


async def demonstrate_error_handling():
    """Example: Error handling and fallback mechanisms"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: ADK Error Handling & Fallback")
    print("=" * 70)

    agent = ResearcherWithADK()

    print("\nAgent Error Handling Features:")
    print("  1. ADK Backend: Primary implementation using google.adk")
    print("  2. Fallback Backend: Automatic fallback to google.generativeai")
    print("  3. Error Capture: All errors captured in AgentResponse.error")
    print("  4. Graceful Degradation: Agent continues with fallback")

    print("\nError Response Example:")
    print("  response = AgentResponse(")
    print("    agent_id='researcher_1',")
    print("    output='',")
    print("    status='error',")
    print("    execution_time=0.5,")
    print("    error='API key not configured',")
    print("    metadata={'role': 'researcher'}")
    print("  )")


async def demonstrate_adk_pattern():
    """Example: Demonstrate the ADK pattern"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Google Cloud ADK Pattern")
    print("=" * 70)

    print("\nADK Pattern Basics:")
    print("-" * 70)
    print("""
from google.adk import Agent

# Create an ADK agent with tools
agent = Agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="You help users research topics thoroughly.",
    tools=[web_search, data_analysis],
)

# Execute agent
response = await agent.run("Research AI trends")
""")

    print("Our Implementation:")
    print("-" * 70)
    print("""
from core.agent import Agent
from core.adk_tools import WebSearchTool

# Create agent with ADK pattern
agent = Agent(
    agent_id="researcher",
    role=AgentRole.RESEARCHER,
    instruction="You help users research topics thoroughly.",
    tools=[WebSearchTool.definition()],
)

# Execute agent
response = await agent.execute("Research AI trends")
""")

    print("\nKey Features:")
    print("  ✓ ADK-compatible interface")
    print("  ✓ Tool support and integration")
    print("  ✓ Async execution")
    print("  ✓ Automatic fallback")
    print("  ✓ Full type safety")


# ============================================================================
# PART 3: MAIN EXECUTION
# ============================================================================

async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("GOOGLE CLOUD ADK COMPLETE IMPLEMENTATION")
    print("=" * 70)

    # Run examples
    await execute_single_agent_example()
    await execute_agent_pipeline_example()
    await execute_parallel_agents_example()
    await demonstrate_tool_usage()
    await demonstrate_error_handling()
    await demonstrate_adk_pattern()

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. Set GOOGLE_API_KEY environment variable
2. Run example_adk_quickstart.py for basic usage
3. Run example_adk_agents_with_tools.py for tool examples
4. Check examples/example_sequential.py for orchestration
5. Review ADK_MIGRATION_GUIDE.md for migration details
6. Visit docs for full API documentation
""")


if __name__ == "__main__":
    asyncio.run(main())

