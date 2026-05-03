"""
Environment configuration for multi-agent orchestration using Google Cloud ADK
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Google Cloud Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_REGION = os.getenv("GOOGLE_REGION", "us-central1")

# Model Configuration
DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_TEMPERATURE = 0.7

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Timeout Configuration
DEFAULT_TIMEOUT = 30  # seconds
AGENT_TIMEOUT = 60    # seconds
ORCHESTRATOR_TIMEOUT = 120  # seconds

# Vertex AI Configuration
ENABLE_VERTEX_AI = os.getenv("ENABLE_VERTEX_AI", "true").lower() == "true"

# ADK Configuration
ADK_DEBUG = os.getenv("ADK_DEBUG", "false").lower() == "true"

# Validation - Optional for demos, required for actual execution
if not GOOGLE_API_KEY and not GOOGLE_PROJECT_ID:
    import warnings
    warnings.warn(
        "Neither GOOGLE_API_KEY nor GOOGLE_PROJECT_ID environment variables are set. "
        "Agent execution will require at least one of these to be configured.",
        UserWarning
    )

