"""Application boundary for the current Flask runtime.

The application implementation remains in ``app.py`` during the staged
migration. New deployment code should import this module rather than the root
entrypoint directly.
"""
from app import app

__all__ = ["app"]
