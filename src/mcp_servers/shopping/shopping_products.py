from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
import logging
from pathlib import Path
from .service import ShoppingService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 FastMCP 服务器
mcp = FastMCP("shopping-assistant")

# 初始化服务
shopping_service = ShoppingService()

@mcp.tool()
def search_products(
    query: str,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort_by: str = "relevance",
    limit: int = 20
) -> str:
    """搜索商品，支持关键词、价格范围等条件
    
    Args:
        query: 搜索关键词（在商品名称和描述中搜索）
        price_min: 最低价格
        price_max: 最高价格
        sort_by: 排序方式 (price_asc/price_desc/name/newest)
        limit: 返回结果数量限制
    """
    logger.info(f"搜索商品: query={query}, price_min={price_min}, price_max={price_max}")
    result = shopping_service.search_products(query, price_min, price_max, sort_by, limit)
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def get_product_detail(product_id: str, fetch_live_data: bool = True) -> str:
    """获取单个商品的详细信息
    
    Args:
        product_id: 商品ID
        fetch_live_data: 是否获取实时网页数据（默认True）
    """
    logger.info(f"获取商品详情: product_id={product_id}, fetch_live_data={fetch_live_data}")
    result = shopping_service.get_product_detail(product_id, fetch_live_data)
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def check_inventory(
    product_id: str,
    variant_id: Optional[str] = None
) -> str:
    """查询商品库存信息
    
    Args:
        product_id: 商品ID
        variant_id: 商品变体ID（可选）
    """
    logger.info(f"检查库存: product_id={product_id}, variant_id={variant_id}")
    result = shopping_service.check_inventory(product_id, variant_id)
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
def get_recommendations(
    recommendation_type: str,
    product_id: Optional[str] = None,
    limit: int = 10
) -> str:
    """获取商品推荐列表
    
    Args:
        recommendation_type: 推荐类型 (similar/price_range/newest/random)
        product_id: 基于此商品的相关推荐（可选）
        limit: 推荐商品数量
    """
    logger.info(f"获取推荐: type={recommendation_type}, product_id={product_id}, limit={limit}")
    result = shopping_service.get_recommendations(recommendation_type, product_id, limit)
    return json.dumps(result, indent=2, ensure_ascii=False)
