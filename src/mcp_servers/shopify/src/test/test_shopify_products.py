import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from products_repository.shopify_products import search_products, ProductFilter

@pytest.fixture
def sample_products_df():
    """创建测试用的产品数据DataFrame"""
    return pd.DataFrame({
        'Name': ['Solar Generator 1000', 'Battery Pack 500', 'Power Station 2000'],
        'URL': ['http://example.com/1', 'http://example.com/2', 'http://example.com/3'],
        'Product Description': [
            'Powerful solar generator $999.99 perfect for camping and outdoor activities',
            'Portable battery pack $499.99 ideal for travel',
            'High capacity power station $1999.99 for home backup and emergency'
        ]
    })

@pytest.mark.asyncio
async def test_search_products_with_description():
    """测试search_products函数的description参数功能"""
    # 创建测试数据
    test_df = pd.DataFrame({
        'Name': ['Solar Generator 1000'],
        'URL': ['http://example.com/1'],
        'Product Description': ['Powerful solar generator $999.99 perfect for camping']
    })
    
    # Mock load_products函数
    with patch('products_repository.shopify_products.load_products', return_value=test_df):
        # 测试使用description参数搜索
        results = await search_products(description="camping")
        print(results)
        assert len(results) == 1
        assert results[0]['name'] == 'Solar Generator 1000'
        assert "camping" in results[0]['description']
        
        # 测试使用不匹配的description
        results = await search_products(description="office")
        assert len(results) == 0
        
        # 测试不提供description参数
        results = await search_products()
        assert len(results) == 1  # 应该返回所有产品
        
        # 测试组合使用description和其他参数
        results = await search_products(
            min_price=900,
            max_price=1000,
            category="Solar",
            description="camping"
        )
        assert len(results) == 1
        assert results[0]['name'] == 'Solar Generator 1000'

@pytest.mark.asyncio
async def test_search_products_with_multiple_filters(sample_products_df):
    """测试search_products函数的多个过滤条件组合"""
    with patch('products_repository.shopify_products.load_products', return_value=sample_products_df):
        # 测试价格范围和描述关键词组合
        results = await search_products(
            min_price=400,
            max_price=1000,
            description="portable"
        )
        print(results)
        assert len(results) == 1
        assert "Battery Pack" in results[0]['name']
        
        # 测试类别和描述关键词组合
        results = await search_products(
            category="Solar",
            description="outdoor"
        )
        assert len(results) == 1
        assert "Solar Generator" in results[0]['name']
        
        # 测试场景和描述关键词组合
        results = await search_products(
            scenario="emergency",
            description="power station"
        )
        assert len(results) == 1
        assert "Power Station" in results[0]['name']

@pytest.mark.asyncio
async def test_get_all_products(sample_products_df):
    """测试get_all_products函数的功能"""
    with patch('products_repository.shopify_products.load_products', return_value=sample_products_df):
        # 导入get_all_products函数
        from products_repository.shopify_products import get_all_products
        
        # 获取所有产品
        results = await get_all_products()
        
        # 验证返回的产品数量
        assert len(results) == 3
        
        # 验证每个产品的数据结构和内容
        for product in results:
            # 检查必要字段是否存在
            assert 'name' in product
            assert 'url' in product
            assert 'description' in product
            assert 'price' in product
            assert 'category' in product
            
            # 验证价格提取
            assert isinstance(product['price'], (float, type(None)))
            if product['price'] is not None:
                assert product['price'] > 0
            
            # 验证类别识别
            assert product['category'] in ['Solar Generator', 'Battery Pack', None]
            
            # 验证具体产品数据
            if 'Solar Generator' in product['name']:
                assert product['price'] == 999.99
                assert product['category'] == 'Solar Generator'
            elif 'Battery Pack' in product['name']:
                assert product['price'] == 499.99
                assert product['category'] == 'Battery Pack'
            elif 'Power Station' in product['name']:
                assert product['price'] == 1999.99
                assert product['category'] == 'Battery Pack'

@pytest.mark.asyncio
async def test_search_products_with_camping_scenario(sample_products_df):
    """测试search_products函数的camping场景搜索功能"""
    with patch('products_repository.shopify_products.load_products', return_value=sample_products_df):
        # 测试空描述和价格范围及场景组合
        results = await search_products(
            description="",
            min_price="0",
            max_price="1000",
            category="",
            scenario="camping"
        )
        print(results)
        assert len(results) == 1
        assert "Solar Generator" in results[0]['name']
        assert "camping" in results[0]['description'].lower()

@pytest.mark.asyncio
async def test_get_single_product_detail():
    """测试get_single_product_detail函数的功能"""
    # 创建测试数据
    test_product = {
        'name': 'Jackery 2 Year Extended Warranty Fee Smart Transfer Switch',
        'url': 'https://www.jackery.com/products/jackery-2-year-extended-warranty-fee-smart-transfer-switch',
        'description': 'Extended warranty for smart transfer switch',
        'price': 99.99,
        'category': 'Accessories'
    }
    
    # Mock get_product_detail函数
    with patch('products_repository.shopify_products.get_product_detail', return_value=test_product):
        # 导入get_single_product_detail函数
        from products_repository.shopify_products import get_single_product_detail
        
        # 测试获取单个产品详情
        result = await get_single_product_detail(
            url="https://www.jackery.com/products/jackery-2-year-extended-warranty-fee-smart-transfer-switch"
        )
        
        # 验证返回的产品数据结构和内容
        assert result['name'] == test_product['name']
        assert result['url'] == test_product['url']
        assert result['description'] == test_product['description']
        assert result['price'] == test_product['price']
        assert result['category'] == test_product['category']
