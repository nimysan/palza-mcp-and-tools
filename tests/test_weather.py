import pytest
from unittest.mock import AsyncMock, patch
import httpx
from mcp_servers.weather.weather import make_nws_request, NWS_API_BASE, USER_AGENT


class TestWeatherAPI:
    """Test cases for weather API functions."""

    @pytest.mark.asyncio
    async def test_make_nws_request_success(self):
        """Test successful API request."""
        mock_response = {
            "properties": {
                "temperature": {"value": 20.0},
                "relativeHumidity": {"value": 65.0}
            }
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.return_value.json.return_value = mock_response
            mock_instance.get.return_value.raise_for_status.return_value = None
            
            result = await make_nws_request("https://api.weather.gov/test")
            
            assert result == mock_response
            mock_instance.get.assert_called_once_with(
                "https://api.weather.gov/test",
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/geo+json"
                },
                timeout=30.0
            )

    @pytest.mark.asyncio
    async def test_make_nws_request_http_error(self):
        """Test API request with HTTP error."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.HTTPStatusError(
                "404 Not Found", 
                request=AsyncMock(), 
                response=AsyncMock()
            )
            
            result = await make_nws_request("https://api.weather.gov/invalid")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_make_nws_request_timeout(self):
        """Test API request timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = httpx.TimeoutException("Timeout")
            
            result = await make_nws_request("https://api.weather.gov/timeout")
            
            assert result is None

    def test_constants(self):
        """Test API constants."""
        assert NWS_API_BASE == "https://api.weather.gov"
        assert USER_AGENT == "weather-app/1.0"
