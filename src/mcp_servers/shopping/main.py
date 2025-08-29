#!/usr/bin/env python3
"""Shopping MCP Server - 基于Shopify产品数据的导购系统"""

import asyncio
import json
from typing import Optional
import mcp
from mcp.server import Server
import mcp.server.stdio
from .service import ShoppingService

# 创建服务器实例和服务
server = Server("shopping-assistant")
shopping_service = ShoppingService()

@mcp.tool()
async def search_products(
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
    result = shopping_service.search_products(query, price_min, price_max, sort_by, limit)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_product_detail(product_id: str) -> str:
    """获取单个商品的详细信息
    
    Args:
        product_id: 商品ID
    """
    result = shopping_service.get_product_detail(product_id)
    return json.dumps(result, indent=2)

@mcp.tool()
async def check_inventory(
    product_id: str,
    variant_id: Optional[str] = None
) -> str:
    """查询商品库存信息
    
    Args:
        product_id: 商品ID
        variant_id: 商品变体ID（可选）
    """
    result = shopping_service.check_inventory(product_id, variant_id)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_recommendations(
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
    result = shopping_service.get_recommendations(recommendation_type, product_id, limit)
    return json.dumps(result, indent=2)

async def main():
    """启动 MCP 服务器"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

async def main():
    """启动 MCP 服务器"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

async def main():
    """启动 MCP 服务器"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
