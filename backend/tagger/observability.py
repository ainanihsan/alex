"""
Observability module for LangFuse integration.
Provides a simple context manager for setting up and flushing traces.
"""

import os
import logging
from contextlib import contextmanager

# Use root logger for Lambda compatibility
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@contextmanager
def observe():
    """
    Context manager for observability with LangFuse.

    Sets up LangFuse observability if environment variables are configured,
    and ensures traces are flushed on exit.

    Usage:
        from observability import observe

        with observe():
            # Your code that uses OpenAI Agents SDK
            result = await agent.run(...)
    """
    logger.info("[CHECK] Observability: Checking configuration...")

    # Check if required environment variables exist
    has_langfuse = bool(os.getenv("LANGFUSE_SECRET_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    logger.info(f"[CHECK] Observability: LANGFUSE_SECRET_KEY exists: {has_langfuse}")
    logger.info(f"[CHECK] Observability: OPENAI_API_KEY exists: {has_openai}")

    if not has_langfuse:
        logger.info("[CHECK] Observability: LangFuse not configured, skipping setup")
        yield
        return

    if not has_openai:
        logger.warning("[WARNING]  Observability: OPENAI_API_KEY not set, traces may not export")

    # Local variable for the client (no global needed)
    langfuse_client = None

    # Try to set up LangFuse
    try:
        logger.info("[CHECK] Observability: Setting up LangFuse...")

        import logfire
        from langfuse import get_client

        # Configure logfire to instrument OpenAI Agents SDK
        logfire.configure(
            service_name="alex_tagger_agent",
            send_to_logfire=False,  # Don't send to Logfire cloud
        )
        logger.info("[OK] Observability: Logfire configured")

        # Instrument OpenAI Agents SDK
        logfire.instrument_openai_agents()
        logger.info("[OK] Observability: OpenAI Agents SDK instrumented")

        # Initialize LangFuse client
        langfuse_client = get_client()
        logger.info("[OK] Observability: LangFuse client initialized")

        # Optional: Check authentication (blocking call, use sparingly)
        try:
            auth_result = langfuse_client.auth_check()
            logger.info(
                f"[OK] Observability: LangFuse authentication check passed (result: {auth_result})"
            )
        except Exception as auth_error:
            logger.warning(f"[WARNING]  Observability: Auth check failed but continuing: {auth_error}")

        logger.info("[TARGET] Observability: Setup complete - traces will be sent to LangFuse")

    except ImportError as e:
        logger.error(f"[ERROR] Observability: Missing required package: {e}")
        langfuse_client = None
    except Exception as e:
        logger.error(f"[ERROR] Observability: Setup failed: {e}")
        langfuse_client = None

    try:
        # Yield control back to the calling code
        yield
    finally:
        # Flush traces on exit
        if langfuse_client:
            try:
                logger.info("[CHECK] Observability: Flushing traces to LangFuse...")
                langfuse_client.flush()
                langfuse_client.shutdown()

                # Add a 10 second delay to ensure network requests complete
                # This is a workaround for Lambda's immediate termination
                import time

                logger.info("[CHECK] Observability: Waiting 10 seconds for flush to complete...")
                time.sleep(10)

                logger.info("[OK] Observability: Traces flushed successfully")
            except Exception as e:
                logger.error(f"[ERROR] Observability: Failed to flush traces: {e}")
        else:
            logger.debug("[CHECK] Observability: No client to flush")
