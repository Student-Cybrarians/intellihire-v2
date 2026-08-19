"""Compatibility re-export for the canonical AI response schemas."""
from backend.ai.ai.schemas import (
    INTERVIEW_SCHEMA,
    MODULE1_SCHEMA,
    MODULE2_SCHEMA,
    MODULE5_SCHEMA,
    RESEARCH_SCHEMA,
)

__all__ = ["MODULE1_SCHEMA", "MODULE2_SCHEMA", "INTERVIEW_SCHEMA", "MODULE5_SCHEMA", "RESEARCH_SCHEMA"]
