#!/usr/bin/env python3
"""Shopify MCP Server main entry point"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
def main():
    """Main entry point for Shopify MCP Server"""
    try:
        # 添加 src 目录到 Python 路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(current_dir, 'src')
        sys.path.insert(0, src_dir)
        
        # 导入原始的 joke 函数
        from .shopping_products import mcp as my_mcp
        logger.info("shopping hello")
        my_mcp.run(transport='stdio')
    except ImportError as e:
        print(f"Error importing shopify modules: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
