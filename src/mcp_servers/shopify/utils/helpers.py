"""Common utility functions for shopify MCP server."""

from typing import Any, Dict, Optional
import json
import hashlib


def format_price(price: float, currency: str = "USD") -> str:
    """Format price with currency."""
    return f"{price:.2f} {currency}"


def generate_cache_key(url: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Generate cache key from URL and parameters."""
    key_data = url
    if params:
        key_data += json.dumps(params, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def sanitize_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize and validate product data."""
    # Implementation here
    return data
