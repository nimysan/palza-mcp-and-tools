import pytest
import pandas as pd


class TestShopifyProducts:
    """Test cases for Shopify products functionality."""

    def test_product_data_structure(self):
        """Test product data structure."""
        product_data = {
            'id': 1,
            'title': 'Test Product',
            'price': 99.99,
            'description': 'A test product'
        }
        
        # Test required fields
        required_fields = ['id', 'title', 'price']
        for field in required_fields:
            assert field in product_data
        
        # Test data types
        assert isinstance(product_data['id'], int)
        assert isinstance(product_data['title'], str)
        assert isinstance(product_data['price'], (int, float))

    def test_pandas_dataframe_operations(self):
        """Test pandas operations for product data."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'title': ['Product A', 'Product B', 'Product C'],
            'price': [10.99, 25.50, 99.99]
        })
        
        assert len(df) == 3
        assert df['price'].max() == 99.99
        assert df['price'].min() == 10.99
