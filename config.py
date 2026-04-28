"""
config.py — Centralized configuration for VoteWise Election Education Assistant.

All constants, thresholds, and environment variables in one place.
"""

import os

__all__ = ["Config"]


class Config:
    """Application-wide configuration constants."""

    # Server
    PORT = int(os.environ.get("PORT", 8080))
    DEBUG = False

    # Rate Limiting
    RATE_LIMIT = "20 per minute"
    RATE_LIMIT_STORAGE = "memory://"

    # Caching
    CACHE_TTL_SECONDS = 600

    # Input Validation
    MAX_MESSAGE_LENGTH = 500
    MAX_TEXT_LENGTH = 2000
    MAX_FEEDBACK_CHIPS = 10

    # Election Data
    SUPPORTED_STATES = {
        "maharashtra", "delhi", "karnataka", "tamil_nadu", "uttar_pradesh",
        "west_bengal", "gujarat", "rajasthan", "madhya_pradesh", "bihar"
    }
    ELECTION_PHASES = {"registration", "announcement", "nomination", "campaign", "polling", "counting", "formation"}
    VOTING_AGE = 18

    # API Keys (from environment)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GOOGLE_TRANSLATE_API_KEY = os.environ.get("GOOGLE_TRANSLATE_API_KEY", "")
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")

    # Gemini
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_TIMEOUT = 15

    # Version
    VERSION = "1.0.0"
