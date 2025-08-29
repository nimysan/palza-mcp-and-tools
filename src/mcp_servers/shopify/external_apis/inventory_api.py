"""External inventory API client."""

import httpx
from typing import Dict, Any, Optional
from .config import ExternalAPISettings, InventoryAPIConfig


class InventoryAPI:
    """Client for external inventory API."""
    
    def __init__(self, config: Optional[InventoryAPIConfig] = None):
        self.config = config or ExternalAPISettings.get_inventory_config()
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
    
    async def get_inventory(self, product_id: str) -> Dict[str, Any]:
        """Get inventory for a product."""
        params = {"product_id": product_id}
        if self.config.warehouse_id:
            params["warehouse_id"] = self.config.warehouse_id
        if self.config.include_reserved:
            params["include_reserved"] = "true"
            
        response = await self.client.get("/inventory", params=params)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
