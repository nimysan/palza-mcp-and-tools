#!/usr/bin/env python3
"""Example usage of shopping service with web crawling"""

import asyncio
from service import ShoppingService

async def main():
    """演示shopping service功能"""
    service = ShoppingService()
    
    print("=== 搜索商品 ===")
    search_result = service.search_products("Explorer", limit=3)
    print(f"找到 {search_result['total_found']} 个商品")
    
    if search_result['products']:
        product_id = search_result['products'][0]['product_id']
        print(f"\n=== 获取商品详情 (ID: {product_id}) ===")
        
        # 获取详情（包含实时数据）
        detail = service.get_product_detail(product_id, fetch_live_data=True)
        print(f"商品名称: {detail['name']}")
        print(f"描述: {detail['description'][:100]}...")
        
        if 'live_data' in detail:
            print(f"实时价格: {detail['live_data'].get('price')}")
            print(f"品牌: {detail['live_data'].get('brand')}")
            if detail['live_data'].get('images'):
                print(f"图片数量: {len(detail['live_data']['images'])}")
        
        print(f"\n=== 检查库存 ===")
        inventory = service.check_inventory(product_id)
        print(f"总库存: {inventory['total_inventory']}")
        print(f"低库存警告: {inventory['is_low_stock']}")

if __name__ == "__main__":
    asyncio.run(main())
