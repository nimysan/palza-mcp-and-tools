# MCP Shopify Products

这是一个用于管理和搜索 Shopify 产品的 MCP 服务器。

## 可用工具

### 1. search_products

搜索产品，支持多种过滤条件。

```python
async def search_products(
    min_price: Optional[float] = None,    # 最低价格
    max_price: Optional[float] = None,    # 最高价格
    category: Optional[str] = None,       # 产品类别 (如 "Solar Generator", "Battery Pack" 等)
    scenario: Optional[str] = None,       # 使用场景 (如 "camping", "home backup" 等)
    description: Optional[str] = None     # 产品描述关键词 (可选)
) -> List[Dict[str, Any]]
```

示例调用：
```python
# 搜索露营用的太阳能发电机
results = await search_products(
    category="Solar Generator",
    scenario="camping",
    min_price=500,
    max_price=2000
)

# 搜索便携式产品
results = await search_products(description="portable")

# 搜索应急备用的大容量产品
results = await search_products(
    scenario="emergency",
    description="high capacity"
)
```

返回结果格式：
```python
[
    {
        'name': '产品名称',
        'url': '产品URL',
        'description': '产品描述'
    },
    ...
]
```

### 2. get_product_details

获取指定 URL 的产品详细信息。

```python
async def get_product_details(
    url: str    # 产品页面URL
) -> Dict[str, Any]
```

示例调用：
```python
details = await get_product_details("https://example.com/product/123")
```

返回结果格式：
```python
{
    'url': '产品URL',
    'html_content': '页面HTML内容',
    'timestamp': '获取时间'
}
```

### 3. crawl_all_products

重新爬取所有产品数据。

```python
async def crawl_all_products(
    website_url: str,           # Shopify 商店的URL (https://shopifystore.com)
    with_variants: bool = False # 是否爬取产品变体数据
) -> Dict[str, Any]
```

示例调用：
```python
result = await crawl_all_products(
    website_url="https://store.example.com",
    with_variants=True
)
```

返回结果格式：
```python
{
    "status": "success",
    "message": "产品数据已成功爬取并保存到 [文件路径]",
    "output_path": "保存文件的路径"
}
```

## 数据缓存

- 产品详情数据会被缓存 1 分钟
- 缓存文件保存在 `cache` 目录下
- 缓存文件名基于产品 URL 生成

## 错误处理

所有工具都包含适当的错误处理：
- 网络请求失败时会返回错误信息
- 数据解析失败时会提供相应的错误描述
- 文件操作失败时会返回具体的错误原因

## 使用建议

1. 搜索时尽量提供具体的过滤条件以获得更精确的结果
2. 对于频繁访问的产品，get_product_details 会使用缓存数据以提高响应速度
3. crawl_all_products 操作可能比较耗时，建议在非高峰期执行

## Release 到本地

```bash
uv pip install -e .
```
