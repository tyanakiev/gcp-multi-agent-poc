# Multi-Agent Orchestration with Google Cloud ADK

A modern, production-ready framework for building multi-agent AI systems using **Google Cloud Agent Development Kit (ADK)** and Generative AI. This project demonstrates how to orchestrate multiple specialized AI agents with tools support.

## 🎯 What is This?

This is a **POC (Proof of Concept) boilerplate** that has been **rewritten to use Google Cloud ADK**. It shows:

- ✅ **ADK Agent Pattern** - Native Google Cloud ADK implementation
- ✅ **Tool Integration** - Agents with web search, data analysis, and content generation
- ✅ **Multi-Agent Orchestration** - Sequential, parallel, and hierarchical coordination
- ✅ **Async/Await** - Full async support for concurrent operations
- ✅ **Production Ready** - Error handling, logging, and type safety

## 🚀 Quick Start

### Installation

```bash
# Clone or navigate to the project
cd multi-agent-orchestration

# Install dependencies
pip install -r requirements.txt

# Set your API key (optional, required for actual execution)
export GOOGLE_API_KEY="your-api-key-here"
```

### Run Examples

```bash
# Basic ADK agent demo
python -m examples.example_adk_quickstart

# Agents with tools
python -m examples.example_adk_agents_with_tools

# Complete implementation examples
python -m examples.example_adk_complete

# Multi-agent orchestration
python -m examples.example_sequential
python -m examples.example_parallel
python -m examples.example_hierarchical
```

## 📚 Core Concepts

### Google Cloud ADK Pattern

The project implements the official Google Cloud ADK pattern:

```python
from google.adk import Agent

agent = Agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="You help users research topics thoroughly.",
    tools=[google_search],
)
```

Our implementation:

```python
from core.agent import Agent
from core.types import AgentRole
from core.adk_tools import WebSearchTool

agent = Agent(
    agent_id="researcher",
    role=AgentRole.RESEARCHER,
    instruction="You help users research topics thoroughly.",
    tools=[WebSearchTool.definition()],
)
```

### Agent Types

| Agent | Purpose | Tools |
|-------|---------|-------|
| **ResearcherAgent** | Gather information | web_search, data_analysis |
| **AnalyzerAgent** | Analyze data | analyze_data, summarize_document |
| **WriterAgent** | Create content | generate_content |
| **CoordinatorAgent** | Coordinate tasks | (custom) |

### Available Tools

- **web_search** - Search information online
- **analyze_data** - Statistical and trend analysis
- **generate_content** - Format and generate content
- **generate_code** - Create code snippets
- **summarize_document** - Summarize long documents

## 💻 Usage Examples

### Single Agent Execution

```python
import asyncio
from agents.researcher import ResearcherAgent

async def main():
    agent = ResearcherAgent()
    response = await agent.execute(
        task="Research machine learning trends",
        context={"timeframe": "2024"}
    )
    print(f"Status: {response.status}")
    print(f"Output: {response.output}")
    print(f"Time: {response.execution_time:.2f}s")

asyncio.run(main())
```

### Agent with Tools

```python
from core.agent import Agent
from core.types import AgentRole
from core.adk_tools import WebSearchTool, DataAnalysisTool

class ResearcherWithTools(Agent):
    def __init__(self):
        super().__init__(
            agent_id="researcher",
            role=AgentRole.RESEARCHER,
            instruction="Research thoroughly using available tools",
            tools=[
                WebSearchTool.definition(),
                DataAnalysisTool.definition(),
            ]
        )

# Usage
agent = ResearcherWithTools()
response = await agent.execute("Research AI trends")
```

### Multi-Agent Pipeline

```python
import asyncio
from orchestrators.sequential import SequentialOrchestrator
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent
from core.types import Task, AgentRole

async def main():
    # Create agents
    researcher = ResearcherAgent()
    writer = WriterAgent()
    
    # Create orchestrator
    orchestrator = SequentialOrchestrator(
        orchestrator_id="research_pipeline",
        agents={"researcher": researcher, "writer": writer}
    )
    
    # Create tasks
    tasks = [
        Task(
            task_id="research",
            description="Research AI developments",
            agent_role=AgentRole.RESEARCHER
        ),
        Task(
            task_id="write",
            description="Write a report",
            agent_role=AgentRole.WRITER
        ),
    ]
    
    # Execute
    result = await orchestrator.orchestrate(tasks)
    print(result.final_output)

asyncio.run(main())
```

### Parallel Agent Execution

```python
import asyncio
from agents.researcher import ResearcherAgent

async def main():
    # Create multiple agents
    researchers = [ResearcherAgent(f"researcher_{i}") for i in range(3)]
    
    # Execute in parallel
    tasks = [
        agent.execute(f"Research topic {i}")
        for i, agent in enumerate(researchers)
    ]
    
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"Agent: {result.agent_id}")
        print(f"Status: {result.status}")
        print(f"Output: {result.output}\n")

asyncio.run(main())
```

## 📁 Project Structure

```
multi-agent-orchestration/
├── core/
│   ├── __init__.py
│   ├── agent.py              # Base Agent class (ADK implementation)
│   ├── adk_tools.py          # Tool definitions
│   ├── orchestrator.py       # Base Orchestrator class
│   ├── config.py             # Configuration
│   └── types.py              # Type definitions
├── orchestrators/
│   ├── __init__.py
│   ├── sequential.py         # Sequential orchestration
│   ├── parallel.py           # Parallel orchestration
│   └── hierarchical.py       # Hierarchical orchestration
├── agents/
│   ├── __init__.py
│   ├── researcher.py         # Researcher agent
│   ├── analyzer.py           # Analyzer agent
│   ├── writer.py             # Writer agent
│   └── coordinator.py        # Coordinator agent
├── examples/
│   ├── __init__.py
│   ├── example_adk_quickstart.py
│   ├── example_adk_agents_with_tools.py
│   ├── example_adk_complete.py
│   ├── example_sequential.py
│   ├── example_parallel.py
│   └── example_hierarchical.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── requirements.txt
├── README.md
├── ADK_README.md (this file)
├── ADK_MIGRATION_GUIDE.md
└── .env.example
```

## 🔧 Configuration

Create a `.env` file:

```env
# API Configuration
GOOGLE_API_KEY=your-api-key-here
GOOGLE_PROJECT_ID=your-project-id

# Model Configuration
DEFAULT_MODEL=gemini-2.0-flash
DEFAULT_TEMPERATURE=0.7

# ADK Configuration
ADK_DEBUG=false
ENABLE_VERTEX_AI=true

# Logging
LOG_LEVEL=INFO
```

## 🎓 Orchestration Strategies

### Sequential Orchestration
Tasks execute one after another, with outputs feeding into the next task.

```python
SequentialOrchestrator(
    orchestrator_id="seq_orch",
    agents={"r": researcher, "w": writer}
)
```

**Use case:** Research → Analysis → Writing pipeline

### Parallel Orchestration
Multiple agents execute tasks simultaneously.

```python
ParallelOrchestrator(
    orchestrator_id="par_orch",
    agents={"r1": res1, "r2": res2, "r3": res3}
)
```

**Use case:** Concurrent research from multiple sources

### Hierarchical Orchestration
A supervisor agent coordinates subordinate agents.

```python
HierarchicalOrchestrator(
    orchestrator_id="hier_orch",
    supervisor_agent=coordinator,
    agents={"r": researcher, "a": analyzer}
)
```

**Use case:** Complex workflows with central coordination

## 🛠️ Creating Custom Agents

```python
from core.agent import Agent
from core.types import AgentRole
from core.adk_tools import WebSearchTool

class MyCustomAgent(Agent):
    def __init__(self, agent_id: str = "custom_agent"):
        instruction = """You are a specialized agent for specific tasks.
Your role is to:
1. Understand complex requirements
2. Execute tasks efficiently
3. Provide clear results

Use your tools effectively."""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CUSTOM,
            instruction=instruction,
            model="gemini-2.0-flash",
            tools=[WebSearchTool.definition()]
        )
```

## 🛠️ Creating Custom Tools

```python
from core.adk_tools import ToolDefinition

class MyTool:
    @staticmethod
    def definition() -> ToolDefinition:
        return ToolDefinition(
            name="my_tool",
            description="What this tool does",
            parameters={
                "param1": "Description of param1",
                "param2": "Description of param2"
            },
            func=MyTool.execute
        )
    
    @staticmethod
    async def execute(param1: str, param2: str) -> str:
        # Your implementation
        return f"Result: {param1} and {param2}"

# Use in agent
custom_tool = MyTool.definition()
agent = Agent(..., tools=[custom_tool])
```

## 📊 Response Types

### AgentResponse

```python
@dataclass
class AgentResponse:
    agent_id: str              # Agent identifier
    output: str                # Agent output
    status: str                # "success", "error", "timeout"
    execution_time: float      # Time in seconds
    metadata: Dict[str, Any]   # Additional data
    error: Optional[str]       # Error message if status is "error"
```

### OrchestrationResult

```python
@dataclass
class OrchestrationResult:
    strategy: OrchestrationStrategy  # Which orchestration pattern
    total_execution_time: float      # Total time
    agent_responses: List[AgentResponse]  # Individual agent results
    final_output: str                # Aggregated result
    metadata: Dict[str, Any]         # Additional metadata
```

## 🔐 Error Handling

Agents implement automatic fallback:

1. **Primary**: Google Cloud ADK (if available)
2. **Fallback**: Google Generative AI
3. **Error Capture**: All errors logged and returned in response

```python
response = await agent.execute("task")
if response.status == "error":
    print(f"Error: {response.error}")
```

## 📈 Performance Tips

- **Use ParallelOrchestrator** for concurrent tasks
- **Set appropriate temperature** (0.0-1.0) for output variability
- **Cache tool results** to avoid redundant API calls
- **Monitor execution_time** to identify bottlenecks
- **Use gemini-2.0-flash-lite** for simple tasks to save costs

## 🧪 Testing

Run the examples to test:

```bash
# Test basic functionality
python -m examples.example_adk_quickstart

# Test agents with tools
python -m examples.example_adk_agents_with_tools

# Test complete implementation
python -m examples.example_adk_complete

# Test orchestration
python -m examples.example_sequential
python -m examples.example_parallel
python -m examples.example_hierarchical
```

## 📚 Documentation

- **ADK_MIGRATION_GUIDE.md** - Migration from old to new ADK pattern
- **ARCHITECTURE.md** - Detailed architecture documentation
- **IMPLEMENTATION_CHECKLIST.md** - Implementation guide
- **PROJECT_STRUCTURE.md** - Project layout details
- **TESTING.md** - Testing strategies

## 🔗 Resources

- [Google Cloud ADK Documentation](https://cloud.google.com/docs/adk)
- [Generative AI API](https://ai.google.dev/)
- [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)

## 🤝 Contributing

To extend this project:

1. **Add new agents** in `agents/` directory
2. **Create custom tools** in `core/adk_tools.py`
3. **Implement new orchestrators** in `orchestrators/` directory
4. **Add examples** in `examples/` directory

## 📄 License

This project is provided as-is for demonstration and educational purposes.

## ⚡ Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export GOOGLE_API_KEY="your-key"

# Run quickstart
python -m examples.example_adk_quickstart

# Run with tools
python -m examples.example_adk_agents_with_tools

# Run orchestration
python -m examples.example_sequential

# Debug with ADK_DEBUG
export ADK_DEBUG=true
python -m examples.example_adk_complete
```

## 🎯 Next Steps

1. **Install** the project and dependencies
2. **Review** `ADK_MIGRATION_GUIDE.md` for ADK pattern details
3. **Run examples** to understand the flow
4. **Create** your first custom agent
5. **Build** your multi-agent orchestration system

---

**Built with Google Cloud ADK** | May 2026

