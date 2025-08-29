"""External API configuration."""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class APIConfig:
    """Base API configuration."""
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None


@dataclass
class InventoryAPIConfig(APIConfig):
    """Inventory API specific configuration."""
    warehouse_id: Optional[str] = None
    include_reserved: bool = True


@dataclass
class RecommendationAPIConfig(APIConfig):
    """Recommendation API specific configuration."""
    model_version: str = "v1"
    max_recommendations: int = 10
    include_metadata: bool = True


class ExternalAPISettings:
    """External API settings manager."""
    
    @staticmethod
    def get_inventory_config() -> InventoryAPIConfig:
        """Get inventory API configuration."""
        return InventoryAPIConfig(
            base_url=os.getenv("INVENTORY_API_URL", "https://api.inventory.com"),
            api_key=os.getenv("INVENTORY_API_KEY"),
            timeout=int(os.getenv("INVENTORY_API_TIMEOUT", "30")),
            warehouse_id=os.getenv("WAREHOUSE_ID"),
            include_reserved=os.getenv("INCLUDE_RESERVED", "true").lower() == "true"
        )
    
    @staticmethod
    def get_recommendation_config() -> RecommendationAPIConfig:
        """Get recommendation API configuration."""
        return RecommendationAPIConfig(
            base_url=os.getenv("RECOMMENDATION_API_URL", "https://api.recommendations.com"),
            api_key=os.getenv("RECOMMENDATION_API_KEY"),
            timeout=int(os.getenv("RECOMMENDATION_API_TIMEOUT", "30")),
            model_version=os.getenv("RECOMMENDATION_MODEL_VERSION", "v1"),
            max_recommendations=int(os.getenv("MAX_RECOMMENDATIONS", "10"))
        )
