"""External recommendation API client."""

import httpx
from typing import Dict, Any, List, Optional
from .config import ExternalAPISettings, RecommendationAPIConfig


class RecommendationAPI:
    """Client for external recommendation API."""
    
    def __init__(self, config: Optional[RecommendationAPIConfig] = None):
        self.config = config or ExternalAPISettings.get_recommendation_config()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if self.config.headers:
            headers.update(self.config.headers)
        return headers
    
    async def get_recommendations(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get product recommendations for a user."""
        params = {
            "user_id": user_id,
            "model_version": self.config.model_version,
            "limit": limit or self.config.max_recommendations
        }
        if self.config.include_metadata:
            params["include_metadata"] = "true"
            
        response = await self.client.get("/recommendations", params=params)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
