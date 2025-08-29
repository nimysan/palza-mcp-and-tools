"""Tests for external APIs configuration."""

import os
import pytest
from unittest.mock import patch

from mcp_servers.shopify.external_apis.config import (
    APIConfig,
    InventoryAPIConfig,
    RecommendationAPIConfig,
    ExternalAPISettings
)


class TestAPIConfig:
    """Test APIConfig dataclass."""
    
    def test_api_config_defaults(self):
        """Test APIConfig with default values."""
        config = APIConfig(base_url="https://api.example.com")
        
        assert config.base_url == "https://api.example.com"
        assert config.api_key is None
        assert config.timeout == 30
        assert config.headers is None
    
    def test_api_config_with_values(self):
        """Test APIConfig with custom values."""
        headers = {"Custom-Header": "value"}
        config = APIConfig(
            base_url="https://api.example.com",
            api_key="test-key",
            timeout=60,
            headers=headers
        )
        
        assert config.base_url == "https://api.example.com"
        assert config.api_key == "test-key"
        assert config.timeout == 60
        assert config.headers == headers


class TestInventoryAPIConfig:
    """Test InventoryAPIConfig dataclass."""
    
    def test_inventory_config_defaults(self):
        """Test InventoryAPIConfig with default values."""
        config = InventoryAPIConfig(base_url="https://inventory.api.com")
        
        assert config.base_url == "https://inventory.api.com"
        assert config.warehouse_id is None
        assert config.include_reserved is True
    
    def test_inventory_config_with_values(self):
        """Test InventoryAPIConfig with custom values."""
        config = InventoryAPIConfig(
            base_url="https://inventory.api.com",
            api_key="inv-key",
            warehouse_id="wh-001",
            include_reserved=False
        )
        
        assert config.warehouse_id == "wh-001"
        assert config.include_reserved is False


class TestRecommendationAPIConfig:
    """Test RecommendationAPIConfig dataclass."""
    
    def test_recommendation_config_defaults(self):
        """Test RecommendationAPIConfig with default values."""
        config = RecommendationAPIConfig(base_url="https://rec.api.com")
        
        assert config.base_url == "https://rec.api.com"
        assert config.model_version == "v1"
        assert config.max_recommendations == 10
        assert config.include_metadata is True
    
    def test_recommendation_config_with_values(self):
        """Test RecommendationAPIConfig with custom values."""
        config = RecommendationAPIConfig(
            base_url="https://rec.api.com",
            api_key="rec-key",
            model_version="v2",
            max_recommendations=20,
            include_metadata=False
        )
        
        assert config.model_version == "v2"
        assert config.max_recommendations == 20
        assert config.include_metadata is False


class TestExternalAPISettings:
    """Test ExternalAPISettings class."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_inventory_config_defaults(self):
        """Test inventory config with default environment values."""
        config = ExternalAPISettings.get_inventory_config()
        
        assert config.base_url == "https://api.inventory.com"
        assert config.api_key is None
        assert config.timeout == 30
        assert config.warehouse_id is None
        assert config.include_reserved is True
    
    @patch.dict(os.environ, {
        "INVENTORY_API_URL": "https://custom-inventory.com",
        "INVENTORY_API_KEY": "test-inv-key",
        "INVENTORY_API_TIMEOUT": "45",
        "WAREHOUSE_ID": "wh-test",
        "INCLUDE_RESERVED": "false"
    })
    def test_inventory_config_from_env(self):
        """Test inventory config from environment variables."""
        config = ExternalAPISettings.get_inventory_config()
        
        assert config.base_url == "https://custom-inventory.com"
        assert config.api_key == "test-inv-key"
        assert config.timeout == 45
        assert config.warehouse_id == "wh-test"
        assert config.include_reserved is False
    
    @patch.dict(os.environ, {}, clear=True)
    def test_recommendation_config_defaults(self):
        """Test recommendation config with default environment values."""
        config = ExternalAPISettings.get_recommendation_config()
        
        assert config.base_url == "https://api.recommendations.com"
        assert config.api_key is None
        assert config.timeout == 30
        assert config.model_version == "v1"
        assert config.max_recommendations == 10
    
    @patch.dict(os.environ, {
        "RECOMMENDATION_API_URL": "https://custom-rec.com",
        "RECOMMENDATION_API_KEY": "test-rec-key",
        "RECOMMENDATION_API_TIMEOUT": "60",
        "RECOMMENDATION_MODEL_VERSION": "v3",
        "MAX_RECOMMENDATIONS": "25"
    })
    def test_recommendation_config_from_env(self):
        """Test recommendation config from environment variables."""
        config = ExternalAPISettings.get_recommendation_config()
        
        assert config.base_url == "https://custom-rec.com"
        assert config.api_key == "test-rec-key"
        assert config.timeout == 60
        assert config.model_version == "v3"
        assert config.max_recommendations == 25
    
    @patch.dict(os.environ, {"INCLUDE_RESERVED": "TRUE"})
    def test_boolean_env_parsing_true_uppercase(self):
        """Test boolean environment variable parsing - TRUE."""
        config = ExternalAPISettings.get_inventory_config()
        assert config.include_reserved is True
    
    @patch.dict(os.environ, {"INCLUDE_RESERVED": "False"})
    def test_boolean_env_parsing_false_mixed_case(self):
        """Test boolean environment variable parsing - False."""
        config = ExternalAPISettings.get_inventory_config()
        assert config.include_reserved is False
