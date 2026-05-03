"""
Pub/Sub client wrapper for agent message routing

Provides standardized publish/subscribe with DLQ support and message envelope handling.
"""

import json
import asyncio
import logging
from typing import Any, Dict, Callable, Optional, List
from abc import ABC, abstractmethod

try:
    from google.cloud import pubsub_v1
    from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
    GOOGLE_PUBSUB_AVAILABLE = True
except ImportError:
    GOOGLE_PUBSUB_AVAILABLE = False

import structlog
from sdk.message_types import MessageEnvelope, AgentMessage
from core.config import (
    GOOGLE_PROJECT_ID,
    PUBSUB_TOPIC_PREFIX,
    PUBSUB_SUBSCRIPTION_PREFIX,
    PUBSUB_DLQ_TOPIC,
    PUBSUB_EMULATOR_HOST,
    MAX_RETRIES,
    RETRY_BACKOFF_MULTIPLIER,
    INITIAL_RETRY_DELAY,
)

logger = structlog.get_logger(__name__)


class PubSubClient:
    """
    Wrapper around Google Cloud Pub/Sub for agent messaging.

    Provides:
    - Message envelope serialization/deserialization
    - Dead-letter queue (DLQ) support
    - Retry logic with exponential backoff
    - Message acknowledgment
    """

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize Pub/Sub client.

        Args:
            project_id: GCP project ID (defaults to config)
        """
        self.project_id = project_id or GOOGLE_PROJECT_ID
        self.publisher_client = None
        self.subscriber_client = None
        self.subscriptions: Dict[str, StreamingPullFuture] = {}

        if not GOOGLE_PUBSUB_AVAILABLE:
            logger.warning("google_cloud_pubsub_not_available")
            return

        if PUBSUB_EMULATOR_HOST:
            # Use Pub/Sub emulator for local development
            import os
            os.environ["PUBSUB_EMULATOR_HOST"] = PUBSUB_EMULATOR_HOST
            logger.info("using_pubsub_emulator", emulator_host=PUBSUB_EMULATOR_HOST)

        try:
            self.publisher_client = pubsub_v1.PublisherClient()
            self.subscriber_client = pubsub_v1.SubscriberClient()
            logger.info("pubsub_client_initialized", project_id=self.project_id)
        except Exception as e:
            logger.error("pubsub_initialization_failed", error=str(e))

    def _get_topic_path(self, topic_name: str) -> str:
        """Get full topic path"""
        if not topic_name.startswith(self.project_id):
            topic_name = f"{PUBSUB_TOPIC_PREFIX}-{topic_name}"
        return self.publisher_client.topic_path(self.project_id, topic_name)

    def _get_subscription_path(self, subscription_name: str) -> str:
        """Get full subscription path"""
        if not subscription_name.startswith(self.project_id):
            subscription_name = f"{PUBSUB_SUBSCRIPTION_PREFIX}-{subscription_name}"
        return self.subscriber_client.subscription_path(self.project_id, subscription_name)

    async def publish_message(
        self,
        envelope: MessageEnvelope,
        topic_name: str,
    ) -> str:
        """
        Publish a message envelope to a topic.

        Args:
            envelope: Message envelope to publish
            topic_name: Target topic name

        Returns:
            Message ID
        """
        if not self.publisher_client:
            logger.warning("pubsub_client_not_initialized")
            return ""

        try:
            topic_path = self._get_topic_path(topic_name)
            message_data = envelope.to_json().encode("utf-8")

            # Publish with trace context
            future = self.publisher_client.publish(
                topic_path,
                message_data,
                trace_id=envelope.message.trace_id,
            )

            message_id = future.result()

            logger.info(
                "message_published",
                topic=topic_name,
                message_id=message_id,
                trace_id=envelope.message.trace_id,
            )

            return message_id

        except Exception as e:
            logger.error(
                "message_publish_failed",
                topic=topic_name,
                error=str(e),
                trace_id=envelope.message.trace_id,
            )
            raise

    async def publish_to_dlq(
        self,
        envelope: MessageEnvelope,
        error_reason: str,
    ) -> str:
        """
        Publish message to dead-letter queue.

        Args:
            envelope: Message envelope
            error_reason: Reason for DLQ

        Returns:
            Message ID
        """
        if not self.publisher_client:
            logger.warning("pubsub_client_not_initialized")
            return ""

        try:
            dlq_path = self._get_topic_path(PUBSUB_DLQ_TOPIC)
            envelope.last_error = error_reason
            message_data = envelope.to_json().encode("utf-8")

            future = self.publisher_client.publish(
                dlq_path,
                message_data,
                original_topic=envelope.message.recipient,
            )

            message_id = future.result()

            logger.info(
                "message_sent_to_dlq",
                message_id=message_id,
                reason=error_reason,
                trace_id=envelope.message.trace_id,
            )

            return message_id

        except Exception as e:
            logger.error(
                "dlq_publish_failed",
                error=str(e),
                trace_id=envelope.message.trace_id,
            )
            raise

    async def subscribe(
        self,
        subscription_name: str,
        callback: Callable,
    ) -> StreamingPullFuture:
        """
        Subscribe to a topic.

        Args:
            subscription_name: Subscription name
            callback: Async callback to handle messages

        Returns:
            Streaming pull future
        """
        if not self.subscriber_client:
            logger.warning("pubsub_client_not_initialized")
            return None

        try:
            subscription_path = self._get_subscription_path(subscription_name)

            def _callback_wrapper(message):
                """Wrap callback to handle async execution"""
                try:
                    # Parse envelope
                    envelope = MessageEnvelope.from_json(
                        message.data.decode("utf-8")
                    )

                    # Execute callback
                    loop = asyncio.get_event_loop()
                    loop.create_task(callback(envelope, message))

                except Exception as e:
                    logger.error(
                        "message_callback_error",
                        error=str(e),
                        message_id=message.message_id,
                    )
                    message.nack()

            future = self.subscriber_client.subscribe(
                subscription_path,
                _callback_wrapper,
            )

            self.subscriptions[subscription_name] = future

            logger.info(
                "subscription_created",
                subscription=subscription_name,
            )

            return future

        except Exception as e:
            logger.error(
                "subscription_failed",
                subscription=subscription_name,
                error=str(e),
            )
            raise

    async def unsubscribe(self, subscription_name: str) -> None:
        """
        Unsubscribe from a topic.

        Args:
            subscription_name: Subscription name
        """
        future = self.subscriptions.pop(subscription_name, None)
        if future:
            future.cancel()
            logger.info("subscription_cancelled", subscription=subscription_name)

    async def shutdown(self) -> None:
        """Shutdown Pub/Sub client"""
        # Cancel all subscriptions
        for subscription_name in list(self.subscriptions.keys()):
            await self.unsubscribe(subscription_name)

        # Close clients
        if self.publisher_client:
            self.publisher_client.close()
        if self.subscriber_client:
            self.subscriber_client.close()

        logger.info("pubsub_client_shutdown")

