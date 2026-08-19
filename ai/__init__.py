"""Compatibility package exposing the canonical IntelliHire AI layer."""
from backend.ai import AIOrchestrator, AIProviderError, AIUnavailableError, get_orchestrator

__all__ = ["AIOrchestrator", "AIProviderError", "AIUnavailableError", "get_orchestrator"]
