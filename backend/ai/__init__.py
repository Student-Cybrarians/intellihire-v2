"""Canonical compatibility entrypoint for IntelliHire's AI package."""
from .ai import AIOrchestrator, AIProviderError, AIUnavailableError, get_orchestrator

__all__ = ["AIOrchestrator", "AIProviderError", "AIUnavailableError", "get_orchestrator"]
