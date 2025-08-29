# MCP Servers 使用指南

## 安装

### 全局安装（推荐）
```bash
# 可编辑安装，方便开发和其他项目调用
uv tool install --editable . --force

# 验证安装
uv tool list
```

### 本地开发
```bash
# 直接运行
uv run mcp-shopping
uv run mcp-shopify-products  
uv run mcp-weather
```

## 可用的MCP服务器

### 1. mcp-shopping - 导购系统
**功能**: 基于Shopify产品数据的智能导购系统

**工具列表**:
- `search_products`: 商品搜索（关键词、价格筛选、排序）
- `get_product_detail`: 商品详情（包含实时网页数据）
- `check_inventory`: 库存查询
- `get_recommendations`: 智能推荐

**启动**:
```bash
mcp-shopping
```

**特性**:
- 3224+真实Shopify产品数据
- 实时网页爬虫获取详细信息
- 智能推荐算法
- 完整的测试覆盖

### 2. mcp-shopify-products - Shopify产品服务
**功能**: Shopify产品管理和查询

**启动**:
```bash
mcp-shopify-products
```

### 3. mcp-weather - 天气服务
**功能**: 天气信息查询

**启动**:
```bash
mcp-weather
```

## 在其他项目中使用

### 作为MCP客户端
```python
import mcp

# 连接到shopping服务器
async with mcp.ClientSession("mcp-shopping") as session:
    result = await session.call_tool("search_products", {
        "query": "Explorer",
        "price_max": 1000,
        "limit": 5
    })
    print(result)
```

### 直接使用服务类
```python
from mcp_servers.shopping.service import ShoppingService

service = ShoppingService()

# 搜索商品
results = service.search_products("battery", price_min=100, limit=10)

# 获取详情（包含实时数据）
detail = service.get_product_detail("1001", fetch_live_data=True)

# 检查库存
inventory = service.check_inventory("1001")
```

## 测试

```bash
# 运行所有测试
pytest tests/

# 运行shopping测试
pytest tests/shopping/ -v

# 使用测试脚本
python run_tests.py
```

## 开发

### 添加新的MCP服务器
1. 在 `src/mcp_servers/` 创建新目录
2. 实现 `main.py` 和相关模块
3. 在 `pyproject.toml` 添加脚本入口
4. 重新安装: `uv tool install --editable . --force`

### 项目结构
```
mcp-server/
├── src/mcp_servers/
│   ├── shopping/          # 导购系统
│   │   ├── main.py       # MCP工具声明
│   │   ├── service.py    # 业务逻辑
│   │   └── crawler.py    # 网页爬虫
│   ├── shopify/          # Shopify服务
│   └── weather/          # 天气服务
├── tests/                # 测试用例
└── pyproject.toml        # 项目配置
```
