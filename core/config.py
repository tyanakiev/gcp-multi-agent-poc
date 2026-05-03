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
USE_ADK_NATIVE = os.getenv("USE_ADK_NATIVE", "true").lower() == "true"

# Pub/Sub Configuration
PUBSUB_TOPIC_PREFIX = os.getenv("PUBSUB_TOPIC_PREFIX", "agent")
PUBSUB_SUBSCRIPTION_PREFIX = os.getenv("PUBSUB_SUBSCRIPTION_PREFIX", "agent-sub")
PUBSUB_DLQ_TOPIC = os.getenv("PUBSUB_DLQ_TOPIC", "dead-letter-queue")
PUBSUB_EMULATOR_HOST = os.getenv("PUBSUB_EMULATOR_HOST")

# Observability Configuration
ENABLE_STRUCTURED_LOGGING = os.getenv("ENABLE_STRUCTURED_LOGGING", "true").lower() == "true"
TRACE_ID_HEADER = "X-Trace-ID"
SERVICE_NAME = os.getenv("SERVICE_NAME", "multi-agent-service")

# Health Check Configuration
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))  # seconds
READINESS_PROBE_PORT = int(os.getenv("READINESS_PROBE_PORT", "8080"))

# Retry Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_MULTIPLIER = float(os.getenv("RETRY_BACKOFF_MULTIPLIER", "2.0"))
INITIAL_RETRY_DELAY = float(os.getenv("INITIAL_RETRY_DELAY", "1.0"))  # seconds

# Validation - Optional for demos, required for actual execution
if not GOOGLE_API_KEY and not GOOGLE_PROJECT_ID:
    import warnings
    warnings.warn(
        "Neither GOOGLE_API_KEY nor GOOGLE_PROJECT_ID environment variables are set. "
        "Agent execution will require at least one of these to be configured.",
        UserWarning
    )

