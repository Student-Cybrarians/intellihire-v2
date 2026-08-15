"""Compatibility facade for the centralized AI orchestrator.

The implementation currently lives in the legacy ``ai`` package. This facade
establishes the new backend import boundary without changing runtime behavior.
"""
from ai.orchestrator import *  # noqa: F401,F403
