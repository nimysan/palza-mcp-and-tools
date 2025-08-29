"""Tests for external API clients."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from mcp_servers.shopify.external_apis.inventory_api import InventoryAPI
from mcp_servers.shopify.external_apis.recommendation_api import RecommendationAPI
from mcp_servers.shopify.external_apis.config import InventoryAPIConfig, RecommendationAPIConfig


class TestInventoryAPI:
    """Test InventoryAPI class."""
    
    def test_init_with_default_config(self):
        """Test InventoryAPI initialization with default config."""
        with patch('mcp_servers.shopify.external_apis.inventory_api.ExternalAPISettings.get_inventory_config') as mock_config:
            mock_config.return_value = InventoryAPIConfig(
                base_url="https://test-inventory.com",
                api_key="test-key"
            )
            
            api = InventoryAPI()
            assert api.config.base_url == "https://test-inventory.com"
            assert api.config.api_key == "test-key"
    
    def test_init_with_custom_config(self):
        """Test InventoryAPI initialization with custom config."""
        config = InventoryAPIConfig(
            base_url="https://custom-inventory.com",
            api_key="custom-key",
            warehouse_id="wh-001"
        )
        
        api = InventoryAPI(config)
        assert api.config.base_url == "https://custom-inventory.com"
        assert api.config.api_key == "custom-key"
        assert api.config.warehouse_id == "wh-001"
    
    def test_get_headers_with_api_key(self):
        """Test headers generation with API key."""
        config = InventoryAPIConfig(
            base_url="https://test.com",
            api_key="test-key"
        )
        
        api = InventoryAPI(config)
        headers = api._get_headers()
        
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-key"
    
    def test_get_headers_without_api_key(self):
        """Test headers generation without API key."""
        config = InventoryAPIConfig(base_url="https://test.com")
        
        api = InventoryAPI(config)
        headers = api._get_headers()
        
        assert headers["Content-Type"] == "application/json"
        assert "Authorization" not in headers
    
    @pytest.mark.asyncio
    async def test_get_inventory_basic(self):
        """Test basic inventory retrieval."""
        config = InventoryAPIConfig(base_url="https://test.com")
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = {"product_id": "123", "quantity": 50}
            mock_client.get.return_value = mock_response
            
            api = InventoryAPI(config)
            result = await api.get_inventory("123")
            
            assert result == {"product_id": "123", "quantity": 50}
            expected_params = {
                "product_id": "123",
                "include_reserved": "true"
            }
            mock_client.get.assert_called_once_with("/inventory", params=expected_params)
    
    @pytest.mark.asyncio
    async def test_get_inventory_with_warehouse(self):
        """Test inventory retrieval with warehouse ID."""
        config = InventoryAPIConfig(
            base_url="https://test.com",
            warehouse_id="wh-001",
            include_reserved=False
        )
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = {"product_id": "123", "quantity": 30}
            mock_client.get.return_value = mock_response
            
            api = InventoryAPI(config)
            await api.get_inventory("123")
            
            expected_params = {
                "product_id": "123",
                "warehouse_id": "wh-001"
            }
            mock_client.get.assert_called_once_with("/inventory", params=expected_params)


class TestRecommendationAPI:
    """Test RecommendationAPI class."""
    
    def test_init_with_custom_config(self):
        """Test RecommendationAPI initialization with custom config."""
        config = RecommendationAPIConfig(
            base_url="https://custom-rec.com",
            api_key="rec-key",
            model_version="v2"
        )
        
        api = RecommendationAPI(config)
        assert api.config.base_url == "https://custom-rec.com"
        assert api.config.api_key == "rec-key"
        assert api.config.model_version == "v2"
    
    @pytest.mark.asyncio
    async def test_get_recommendations_basic(self):
        """Test basic recommendations retrieval."""
        config = RecommendationAPIConfig(
            base_url="https://test.com",
            model_version="v1",
            max_recommendations=5
        )
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = [{"product_id": "123"}, {"product_id": "456"}]
            mock_client.get.return_value = mock_response
            
            api = RecommendationAPI(config)
            result = await api.get_recommendations("user123")
            
            assert result == [{"product_id": "123"}, {"product_id": "456"}]
            expected_params = {
                "user_id": "user123",
                "model_version": "v1",
                "limit": 5,
                "include_metadata": "true"
            }
            mock_client.get.assert_called_once_with("/recommendations", params=expected_params)
    
    @pytest.mark.asyncio
    async def test_get_recommendations_with_custom_limit(self):
        """Test recommendations retrieval with custom limit."""
        config = RecommendationAPIConfig(base_url="https://test.com")
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_client.get.return_value = mock_response
            
            api = RecommendationAPI(config)
            await api.get_recommendations("user123", limit=15)
            
            expected_params = {
                "user_id": "user123",
                "model_version": "v1",
                "limit": 15,
                "include_metadata": "true"
            }
            mock_client.get.assert_called_once_with("/recommendations", params=expected_params)
