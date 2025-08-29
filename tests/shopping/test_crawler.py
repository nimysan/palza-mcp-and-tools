"""Tests for product crawler"""

import pytest
from unittest.mock import patch, MagicMock
from src.mcp_servers.shopping.crawler import ProductCrawler


@pytest.fixture
def crawler():
    """Product crawler instance"""
    return ProductCrawler()


@pytest.fixture
def mock_html():
    """Mock HTML response"""
    return """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "Product",
                "name": "Jackery Explorer 1000",
                "description": "Portable power station with 1000Wh capacity",
                "brand": {"name": "Jackery"},
                "offers": {
                    "price": "999.99",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock"
                },
                "image": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
                "aggregateRating": {
                    "ratingValue": "4.5",
                    "reviewCount": "123"
                }
            }
            </script>
        </head>
        <body>
            <h1>Jackery Explorer 1000</h1>
            <div class="product-description">Portable power station</div>
            <span class="price">$999.99</span>
        </body>
    </html>
    """


class TestProductCrawler:
    
    def test_extract_price(self, crawler):
        """Test price extraction"""
        assert crawler._extract_price("999.99") == 999.99
        assert crawler._extract_price("$1,299.99") == 1299.99
        assert crawler._extract_price("€500.50") == 500.50
        assert crawler._extract_price("invalid") is None
        assert crawler._extract_price("") is None
    
    def test_extract_images_string(self, crawler):
        """Test image extraction from string"""
        result = crawler._extract_images("https://example.com/image.jpg")
        assert result == ["https://example.com/image.jpg"]
    
    def test_extract_images_list(self, crawler):
        """Test image extraction from list"""
        images = [
            "https://example.com/image1.jpg",
            {"url": "https://example.com/image2.jpg"}
        ]
        result = crawler._extract_images(images)
        assert len(result) == 2
        assert result[0] == "https://example.com/image1.jpg"
        assert result[1] == "https://example.com/image2.jpg"
    
    def test_extract_rating(self, crawler):
        """Test rating extraction"""
        rating_data = {
            "ratingValue": "4.5",
            "reviewCount": "123",
            "bestRating": "5"
        }
        result = crawler._extract_rating(rating_data)
        assert result["rating"] == "4.5"
        assert result["review_count"] == "123"
        assert result["best_rating"] == "5"
    
    def test_extract_features(self, crawler):
        """Test feature extraction"""
        description = """
        Product features:
        • 1000Wh capacity
        • Multiple output ports
        - Fast charging
        Weight: 22 lbs
        """
        result = crawler._extract_features(description)
        assert len(result) >= 2
        assert any("1000Wh" in feature for feature in result)
    
    @patch('requests.Session.get')
    def test_get_product_detail_success(self, mock_get, crawler, mock_html):
        """Test successful product detail retrieval"""
        mock_response = MagicMock()
        mock_response.content = mock_html.encode()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = crawler.get_product_detail("https://example.com/product")
        
        assert result["name"] == "Jackery Explorer 1000"
        assert result["price"] == 999.99
        assert result["currency"] == "USD"
        assert result["brand"] == "Jackery"
        assert len(result["images"]) == 2
        assert result["source"] == "structured_data"
    
    @patch('requests.Session.get')
    def test_get_product_detail_request_error(self, mock_get, crawler):
        """Test request error handling"""
        mock_get.side_effect = Exception("Network error")
        
        result = crawler.get_product_detail("https://example.com/product")
        
        assert "error" in result
        assert "Network error" in result["error"]
    
    @patch('requests.Session.get')
    def test_get_product_detail_html_fallback(self, mock_get, crawler):
        """Test HTML parsing fallback"""
        html_without_json = """
        <html>
            <body>
                <h1>Test Product</h1>
                <div class="product-description">Test description</div>
                <span class="price">$199.99</span>
            </body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.content = html_without_json.encode()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = crawler.get_product_detail("https://example.com/product")
        
        assert result["name"] == "Test Product"
        assert result["source"] == "html_parsing"
        assert "url" in result
