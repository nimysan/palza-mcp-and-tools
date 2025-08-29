import pytest
from mcp_servers.weather.weather import NWS_API_BASE, USER_AGENT


class TestWeatherAPI:
    """Test cases for weather API functions."""

    def test_constants(self):
        """Test API constants."""
        assert NWS_API_BASE == "https://api.weather.gov"
        assert USER_AGENT == "weather-app/1.0"

    def test_weather_data_structure(self):
        """Test weather data structure."""
        weather_data = {
            "temperature": {"value": 20.0, "unit": "C"},
            "humidity": {"value": 65.0, "unit": "%"},
            "description": "Partly cloudy"
        }
        
        # Test required fields
        assert "temperature" in weather_data
        assert "humidity" in weather_data
        
        # Test data types
        assert isinstance(weather_data["temperature"]["value"], (int, float))
        assert isinstance(weather_data["humidity"]["value"], (int, float))

    def test_api_headers(self):
        """Test API headers format."""
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/geo+json"
        }
        
        assert headers["User-Agent"] == "weather-app/1.0"
        assert headers["Accept"] == "application/geo+json"
