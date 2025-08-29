"""Configuration utilities for shopify MCP server."""

import os
from typing import Optional


class Config:
    """Configuration manager."""
    
    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable."""
        return os.getenv(key, default)
    
    @staticmethod
    def get_inventory_api_url() -> str:
        """Get inventory API URL from environment."""
        return Config.get_env("INVENTORY_API_URL", "https://api.example.com/inventory")
    
    @staticmethod
    def get_recommendation_api_url() -> str:
        """Get recommendation API URL from environment."""
        return Config.get_env("RECOMMENDATION_API_URL", "https://api.example.com/recommendations")
