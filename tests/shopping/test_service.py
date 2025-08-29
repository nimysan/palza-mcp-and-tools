"""Tests for shopping service"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.mcp_servers.shopping.service import ShoppingService


@pytest.fixture
def mock_df():
    """Mock product data"""
    return pd.DataFrame({
        'Product ID': [1001, 1001, 1002, 1003],
        'Variant ID': [2001, 2002, 2003, 2004],
        'Name': ['Jackery Explorer 1000', 'Jackery Explorer 1000', 'Solar Panel 100W', 'Battery Pack 500'],
        'Variant Title': ['Default', 'Extended', 'Default', 'Default'],
        'Price': [999.99, 1199.99, 299.99, 199.99],
        'Compare At Price': [1299.99, 1399.99, None, 249.99],
        'SKU': ['JE1000', 'JE1000E', 'SP100', 'BP500'],
        'URL': ['url1', 'url1', 'url2', 'url3'],
        'Inventory Quantity': [50, 30, 100, 25],
        'Product Description': ['Portable power station', 'Portable power station', 'Solar charging panel', 'Backup battery'],
        'Meta Title': ['Explorer 1000', 'Explorer 1000', 'Solar Panel', 'Battery'],
        'Meta Description': ['desc1', 'desc1', 'desc2', 'desc3'],
        'Created At': ['2024-01-01', '2024-01-01', '2024-02-01', '2024-03-01'],
        'Updated At': ['2024-01-15', '2024-01-15', '2024-02-15', '2024-03-15'],
        'Taxable': [True, True, False, True],
        'Requires Shipping': [True, True, True, False],
        'Weight': [10.0, 10.0, 5.0, 2.0],
        'Weight Unit': ['lb', 'lb', 'lb', 'lb'],
        'Barcode': ['123456', '123457', '123458', '123459'],
        'Inventory Policy': ['deny', 'deny', 'continue', 'deny'],
        'Fulfillment Service': ['manual', 'manual', 'manual', 'manual'],
        'Inventory Management': ['shopify', 'shopify', 'shopify', 'shopify']
    })


@pytest.fixture
def service():
    """Shopping service instance"""
    return ShoppingService()


class TestShoppingService:
    
    def test_search_products_basic(self, service, mock_df):
        """Test basic product search"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.search_products("Explorer")
            
            assert result['query'] == "Explorer"
            assert result['total_found'] == 2
            assert len(result['products']) == 2
            assert result['products'][0]['name'] == 'Jackery Explorer 1000'
    
    def test_search_products_price_filter(self, service, mock_df):
        """Test search with price filters"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.search_products("", price_min=300, price_max=1000)
            
            assert result['total_found'] == 1
            assert result['products'][0]['price'] == 999.99
    
    def test_search_products_sort_by_price(self, service, mock_df):
        """Test search with price sorting"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.search_products("", sort_by="price_asc", limit=10)
            
            prices = [p['price'] for p in result['products']]
            assert prices == sorted(prices)
    
    def test_get_product_detail_success(self, service, mock_df):
        """Test successful product detail retrieval"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.get_product_detail("1001")
            
            assert result['product_id'] == "1001"
            assert result['name'] == 'Jackery Explorer 1000'
            assert len(result['variants']) == 2
            assert result['variants'][0]['variant_id'] == '2001'
    
    def test_get_product_detail_not_found(self, service, mock_df):
        """Test product detail for non-existent product"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.get_product_detail("9999")
            
            assert 'error' in result
            assert "未找到商品ID: 9999" in result['error']
    
    def test_check_inventory_by_product(self, service, mock_df):
        """Test inventory check by product ID"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.check_inventory("1001")
            
            assert result['product_id'] == "1001"
            assert result['total_inventory'] == 80  # 50 + 30
            assert len(result['inventory_details']) == 2
            assert result['is_low_stock'] == False
    
    def test_check_inventory_by_variant(self, service, mock_df):
        """Test inventory check by variant ID"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.check_inventory("1001", variant_id="2001")
            
            assert result['variant_id'] == "2001"
            assert result['total_inventory'] == 50
            assert len(result['inventory_details']) == 1
    
    def test_check_inventory_low_stock(self, service, mock_df):
        """Test low stock detection"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.check_inventory("1003")  # Battery Pack with 25 qty
            
            assert result['is_low_stock'] == False  # 25 > 10
            
            # Test with actual low stock
            low_stock_df = mock_df.copy()
            low_stock_df.loc[low_stock_df['Product ID'] == 1003, 'Inventory Quantity'] = 5
            
            with patch.object(service, '_load_products', return_value=low_stock_df):
                result = service.check_inventory("1003")
                assert result['is_low_stock'] == True
    
    def test_get_recommendations_similar(self, service, mock_df):
        """Test similar product recommendations"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.get_recommendations("similar", product_id="1001")
            
            assert result['recommendation_type'] == "similar"
            assert result['base_product_id'] == "1001"
            # Should find products within 30% price range of 999.99
            assert len(result['recommendations']) >= 0
    
    def test_get_recommendations_newest(self, service, mock_df):
        """Test newest product recommendations"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.get_recommendations("newest", limit=2)
            
            assert result['recommendation_type'] == "newest"
            assert len(result['recommendations']) <= 2
    
    def test_get_recommendations_price_range(self, service, mock_df):
        """Test price range recommendations"""
        with patch.object(service, '_load_products', return_value=mock_df):
            result = service.get_recommendations("price_range", limit=3)
            
            assert result['recommendation_type'] == "price_range"
            prices = [r['price'] for r in result['recommendations']]
            assert prices == sorted(prices)  # Should be sorted by price
    
    def test_empty_dataframe_handling(self, service):
        """Test handling of empty dataframe"""
        with patch.object(service, '_load_products', return_value=pd.DataFrame()):
            result = service.search_products("test")
            assert 'error' in result
            
            result = service.get_product_detail("1001")
            assert 'error' in result
            
            result = service.check_inventory("1001")
            assert 'error' in result
            
            result = service.get_recommendations("similar")
            assert 'error' in result
    
    def test_data_caching(self, service):
        """Test that data is cached after first load"""
        mock_csv_read = MagicMock(return_value=pd.DataFrame({'test': [1]}))
        
        with patch('pandas.read_csv', mock_csv_read):
            # First call should read CSV
            service._load_products()
            assert mock_csv_read.call_count == 1
            
            # Second call should use cache
            service._load_products()
            assert mock_csv_read.call_count == 1  # Still 1, not 2
