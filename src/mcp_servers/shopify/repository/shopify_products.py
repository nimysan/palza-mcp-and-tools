from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
from decimal import Decimal
import re
import requests
import os
import json
import logging
from datetime import datetime, timedelta
from .shopify_crawler import ShopifyCrawler


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 FastMCP 服务器
mcp = FastMCP("jackery-products")

# 常量
PRODUCTS_CSV_PATH = "/Users/yexw/PycharmProjects/mcp/mcp-server/mcp-shopify-products/src/data/products.csv"
CACHE_TTL_MINUTES = 5

# 内存缓存
_products_cache = None
_cache_timestamp = None

class ProductFilter:
    """产品过滤器类"""
    def __init__(self, 
                 min_price: Optional[float] = None,
                 max_price: Optional[float] = None,
                 category: Optional[str] = None,
                 scenario: Optional[str] = None,
                 description: Optional[str] = None):
        self.min_price = min_price
        self.max_price = max_price
        self.category = category
        self.scenario = scenario
        self.description = description

    def match_price(self, description: str) -> bool:
        """检查价格是否在范围内"""
        if not (self.min_price or self.max_price):
            return True
            
        # 从描述中提取价格
        price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', str(description))
        if not price_match:
            return True
            
        try:
            price = Decimal(price_match.group(1).replace(',', ''))
            if self.min_price and price < self.min_price:
                return False
            if self.max_price and price > self.max_price:
                return False
            return True
        except:
            return True

    def match_category(self, name: str, description: str) -> bool:
        """检查产品类别是否匹配"""
        if not self.category:
            return True
            
        category_lower = self.category.lower()
        return (category_lower in str(name).lower() or 
                category_lower in str(description).lower())

    def match_scenario(self, description: str) -> bool:
        """检查使用场景是否匹配"""
        if not self.scenario:
            return True
            
        scenario_lower = self.scenario.lower()
        return scenario_lower in str(description).lower()

    def match_description(self, description: str) -> bool:
        """检查产品描述是否匹配搜索关键词"""
        if not self.description:
            return True
            
        description_lower = self.description.lower()
        return description_lower in str(description).lower()

    def match_product(self, product: Dict[str, Any]) -> bool:
        """检查产品是否满足所有过滤条件"""
        product_description = product.get('Product Description', '')
        return (self.match_price(product_description) and
                self.match_category(product.get('Name', ''), product_description) and
                self.match_scenario(product_description) and
                self.match_description(product_description))

def load_products() -> pd.DataFrame:
    """加载产品数据，使用内存缓存（缓存时间5分钟）"""
    global _products_cache, _cache_timestamp
    
    current_time = datetime.now()
    
    # 检查缓存是否有效
    if (_products_cache is not None and _cache_timestamp is not None and
        current_time - _cache_timestamp < timedelta(minutes=CACHE_TTL_MINUTES)):
        logger.info("使用内存缓存的产品数据")
        return _products_cache
    
    # 缓存无效或不存在，重新加载数据
    logger.info("从文件加载产品数据")
    _products_cache = pd.read_csv(PRODUCTS_CSV_PATH, dtype={
        'Name': str,
        'URL': str,
        'Meta Title': str,
        'Meta Description': str,
        'Product Description': str
    })
    _cache_timestamp = current_time
    
    return _products_cache

@mcp.tool()
async def search_products(category: str,
                        scenario: str,
                        min_price: Optional[float] = None,
                        max_price: Optional[float] = None,
                        description: Optional[str] = None) -> List[Dict[str, Any]]:
    """搜索产品
    
    Args:
        category: 产品类别 (如 "Solar Generator", "Battery Pack" 等)，必需参数
        scenario: 使用场景 (如 "camping", "home backup" 等)，必需参数
        min_price: 最低价格 (可选)
        max_price: 最高价格 (可选)
        description: 产品描述关键词 (可选)
    
    Returns:
        满足条件的产品列表
    """
    # 创建过滤器
    product_filter = ProductFilter(
        min_price=min_price,
        max_price=max_price,
        category=category,
        scenario=scenario,
        description=description
    )
    
    # 加载产品数据
    logger.info(f"搜索产品 - 价格范围: {min_price}-{max_price}, 类别: {category}, 场景: {scenario}, 描述关键词: {description}")
    df = load_products()
    
    # 应用过滤器
    filtered_products = []
    for _, row in df.iterrows():
        product = row.to_dict()
        if product_filter.match_product(product):
            filtered_products.append({
                'name': str(product['Name']),
                'url': str(product['URL']),
                'description': str(product['Product Description'])
            })
    
    # 限制返回最多3个产品
    limited_products = filtered_products[:3]
    logger.info(f"找到 {len(filtered_products)} 个匹配的产品，返回前 {len(limited_products)} 个")
    return limited_products

def get_cache_path(url: str) -> str:
    """获取缓存文件路径"""
    # 将URL转换为文件名安全的格式
    cache_filename = re.sub(r'[^\w]', '_', url) + '.json'
    cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, cache_filename)

def is_cache_valid(cache_path: str) -> bool:
    """检查缓存是否在TTL期限内"""
    if not os.path.exists(cache_path):
        return False
    
    # 检查文件修改时间是否在1分钟内
    mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
    return datetime.now() - mtime < timedelta(minutes=1)

@mcp.tool()
async def get_single_product_detail(url: str) -> Dict[str, Any]:
    """获取指定URL的产品详情
    1. 获取具体的产品的价格，规格，优惠卷，SKU等信息。
    2. 当需要对比不同的商品的时候， 分别获取不同的商品详情来对比。
    
    Args:
        url: 产品页面URL
    
    Returns:
        包含产品详细信息的字典
    """
    logger.info(f"获取产品详情: {url}")
    cache_path = get_cache_path(url)
    
    # 检查缓存是否有效
    if is_cache_valid(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                logger.info(f"使用缓存数据: {cache_path}")
                return json.load(f)
        except:
            pass
    
    try:
        # 发送HTTP请求获取页面内容
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        # 提取产品信息
        # 这里使用简单的数据结构存储,实际使用时可能需要更复杂的解析逻辑
        product_data = {
            'url': url,
            'html_content': html_content,
            'timestamp': datetime.now().isoformat(),
        }
        
        # 保存到缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            logger.info(f"保存数据到缓存: {cache_path}")
            json.dump(product_data, f, ensure_ascii=False, indent=2)
        
        return product_data
        
    except Exception as e:
        error_msg = f"获取产品详情失败: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
async def get_all_products() -> List[Dict[str, Any]]:
    """获取所有产品数据
    
    Returns:
        所有产品的列表，每个产品包含名称、URL、描述、价格和类别信息
    """
    logger.info("获取所有产品数据")
    df = load_products()
    
    products = []
    for _, row in df.iterrows():
        description = str(row['Product Description'])
        
        # 提取价格
        price = None
        price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', description)
        if price_match:
            try:
                price = float(price_match.group(1).replace(',', ''))
            except:
                pass
        
        # 从名称中提取类别
        name = str(row['Name'])
        category = None
        if "Solar Generator" in name:
            category = "Solar Generator"
        elif "Battery Pack" in name or "Power Station" in name:
            category = "Battery Pack"
        elif "Solar Panel" in name:
            category = "Solar Panel"
        
        products.append({
            'name': name,
            'url': str(row['URL']),
            'description': description,
            'price': price,
            'category': category
        })
    
    logger.info(f"总共返回 {len(products)} 个产品")
    return products

# @mcp.tool()
async def crawl_all_products(website_url: str, with_variants: bool = False) -> Dict[str, Any]:
    """重新爬取所有产品数据
    
    Args:
        website_url: Shopify 商店的URL (https://shopifystore.com)
        with_variants: 是否爬取产品变体数据
    
    Returns:
        包含爬取结果信息的字典
    """
    try:
        logger.info(f"开始爬取商店 {website_url} 的产品数据")
        
        # 创建爬虫实例
        crawler = ShopifyCrawler(
            website_url=website_url,
            output_path=PRODUCTS_CSV_PATH,
            with_variants=with_variants
        )
        
        # 开始爬取
        crawler.crawl()
        
        return {
            "status": "success",
            "message": f"产品数据已成功爬取并保存到 {PRODUCTS_CSV_PATH}",
            "output_path": PRODUCTS_CSV_PATH
        }
        
    except Exception as e:
        error_msg = f"爬取产品数据失败: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')
