from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import pandas as pd
import json
import logging
from pathlib import Path
from .handlers.product_handler import ShoppingService

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
    scenario: str,
    query: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort_by: str = "relevance",
    limit: int = 20
) -> str:
    """搜索商品，基于使用场景进行筛选
    
    Args:
        scenario: 使用场景 (户外/家用/应急/旅行/大容量/便携/太阳能/配件)
        query: 搜索关键词（可选，在商品名称和描述中搜索）
        price_min: 最低价格
        price_max: 最高价格
        sort_by: 排序方式 (price_asc/price_desc/name/newest)
        limit: 返回结果数量限制
    """
    logger.info(f"开始搜索商品: scenario='{scenario}', query='{query}', price_min={price_min}, price_max={price_max}, sort_by='{sort_by}', limit={limit}")
    
    try:
        result = shopping_service.search_products(scenario, query, price_min, price_max, sort_by, limit)
        
        # 记录搜索结果统计信息
        if isinstance(result, dict):
            total_count = len(result.get('products', []))
            logger.info(f"搜索完成: 场景'{scenario}' 找到 {total_count} 个商品")
            
            # 记录返回的商品基本信息
            if total_count > 0:
                products = result.get('products', [])
                logger.debug(f"返回商品列表: {[p.get('name', 'Unknown') for p in products[:5]]}")  # 只记录前5个商品名称
                if total_count > 5:
                    logger.debug(f"... 还有 {total_count - 5} 个商品")
        else:
            logger.warning(f"搜索结果格式异常: {type(result)}")
        
        # 记录返回数据的大小
        json_result = json.dumps(result, indent=2, ensure_ascii=False)
        logger.info(f"返回数据大小: {len(json_result)} 字符")
        logger.info(f"{json_result}")
        
        return json_result
        
    except Exception as e:
        logger.error(f"搜索商品时发生错误: {str(e)}", exc_info=True)
        return json.dumps({"error": f"搜索失败: {str(e)}"}, ensure_ascii=False)

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
