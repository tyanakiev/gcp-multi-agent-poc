"""
ADK-compatible tools: plain callables (ADK wraps them as FunctionTool).

See: https://google.github.io/adk-docs/get-started/python/
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class ToolDefinition:
    """Registry entry describing a tool callable (used by get_tool / list_available_tools)."""

    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]


# --- Named callables (ADK uses function __name__ in declarations) -----------------


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for information on a given topic.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default: 5).
    """
    return f"Search results for '{query}' (simulated, max_results={max_results})"


def analyze_data(data: str, analysis_type: str = "statistical") -> str:
    """Analyze structured data and provide insights.

    Args:
        data: The data to analyze.
        analysis_type: Type of analysis (statistical, trend, pattern).
    """
    return f"Analysis complete for data with {analysis_type} analysis type (simulated)"


def generate_content(topic: str, output_format: str = "markdown", length: str = "medium") -> str:
    """Generate formatted content based on specifications.

    Args:
        topic: The topic to write about.
        output_format: Output format (markdown, html, plain text).
        length: Content length (short, medium, long).
    """
    return f"Generated {length} {output_format} content about {topic} (simulated)"


def generate_code(language: str, task: str, style: str = "clean") -> str:
    """Generate code snippets for specified tasks.

    Args:
        language: Programming language (python, javascript, java, etc.).
        task: Description of what the code should do.
        style: Code style preference.
    """
    return f"Generated {language} code for task: {task} (simulated, style={style})"


def summarize_document(document: str, summary_length: str = "medium") -> str:
    """Summarize long documents into concise summaries.

    Args:
        document: The document text to summarize.
        summary_length: Length of summary (brief, medium, detailed).
    """
    return f"Generated {summary_length} summary (simulated, chars={len(document)})"


class WebSearchTool:
    """Web search tool for research agents"""

    @staticmethod
    def definition() -> ToolDefinition:
        return ToolDefinition(
            name="web_search",
            description="Search the web for information on a given topic",
            parameters={
                "query": "The search query string",
                "max_results": "Maximum number of results to return (default: 5)",
            },
            func=web_search,
        )


class DataAnalysisTool:
    """Data analysis tool for analyzer agents"""

    @staticmethod
    def definition() -> ToolDefinition:
        return ToolDefinition(
            name="analyze_data",
            description="Analyze structured data and provide insights",
            parameters={
                "data": "The data to analyze",
                "analysis_type": "Type of analysis (statistical, trend, pattern)",
            },
            func=analyze_data,
        )


class ContentGenerationTool:
    """Content generation tool for writer agents"""

    @staticmethod
    def definition() -> ToolDefinition:
        return ToolDefinition(
            name="generate_content",
            description="Generate formatted content based on specifications",
            parameters={
                "topic": "The topic to write about",
                "output_format": "Output format (markdown, html, plain text)",
                "length": "Content length (short, medium, long)",
            },
            func=generate_content,
        )


class CodeGenerationTool:
    """Code generation tool for technical agents"""

    @staticmethod
    def definition() -> ToolDefinition:
        return ToolDefinition(
            name="generate_code",
            description="Generate code snippets for specified tasks",
            parameters={
                "language": "Programming language (python, javascript, java, etc.)",
                "task": "Description of what the code should do",
                "style": "Code style preference",
            },
            func=generate_code,
        )


class DocumentSummarizationTool:
    """Document summarization tool for analysis agents"""

    @staticmethod
    def definition() -> ToolDefinition:
        return ToolDefinition(
            name="summarize_document",
            description="Summarize long documents into concise summaries",
            parameters={
                "document": "The document text to summarize",
                "summary_length": "Length of summary (brief, medium, detailed)",
            },
            func=summarize_document,
        )


class APICacheTool:
    """Tool for caching API responses to avoid redundant calls"""

    def __init__(self):
        self.cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Cache a value"""
        self.cache[key] = value

    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()


# Registry of available tools
AVAILABLE_TOOLS = {
    "web_search": WebSearchTool,
    "analyze_data": DataAnalysisTool,
    "generate_content": ContentGenerationTool,
    "generate_code": CodeGenerationTool,
    "summarize_document": DocumentSummarizationTool,
}


def get_tool(tool_name: str) -> Optional[ToolDefinition]:
    """Get a tool definition by name"""
    tool_class = AVAILABLE_TOOLS.get(tool_name)
    if tool_class:
        return tool_class.definition()
    return None


def list_available_tools() -> Dict[str, str]:
    """List all available tools with descriptions"""
    tools: Dict[str, str] = {}
    for name, tool_class in AVAILABLE_TOOLS.items():
        definition = tool_class.definition()
        tools[name] = definition.description
    return tools
