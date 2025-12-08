# FILE: backend/core/__init__.py
# ================================================
"""
Core Module
===========
Configuration, database, and models
"""

from .config import Settings, APIConfig, settings
from .database import Database, db

__all__ = ['Settings', 'APIConfig', 'settings', 'Database', 'db']