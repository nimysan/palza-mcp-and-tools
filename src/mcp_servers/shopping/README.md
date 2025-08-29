# Shopping MCP Server - 导购系统接口

## 工具列表

### 1. search_products - 搜索商品
**功能**: 根据关键词、分类、价格等条件搜索商品

**参数**:
- `query` (必需): 搜索关键词
- `category`: 商品分类 (electronics/clothing/books/home/sports/beauty)
- `price_min`: 最低价格
- `price_max`: 最高价格  
- `sort_by`: 排序方式 (price_asc/price_desc/rating/popularity/newest)
- `limit`: 返回数量 (默认20)

### 2. get_product_detail - 商品详情
**功能**: 获取单个商品的完整信息

**参数**:
- `product_id` (必需): 商品ID

**返回**: 商品名称、价格、描述、图片、变体、规格、配送信息等

### 3. check_inventory - 库存查询
**功能**: 查询商品库存状态

**参数**:
- `product_id` (必需): 商品ID
- `variant_id`: 商品变体ID
- `location`: 查询地区/仓库

**返回**: 可用库存、预留库存、补货信息等

### 4. get_recommendations - 推荐商品
**功能**: 获取个性化推荐列表

**参数**:
- `recommendation_type` (必需): 推荐类型
  - `similar`: 相似商品
  - `complementary`: 互补商品
  - `trending`: 热门商品
  - `personalized`: 个性化推荐
  - `frequently_bought_together`: 经常一起购买
- `user_id`: 用户ID
- `product_id`: 基础商品ID
- `category`: 推荐分类
- `limit`: 推荐数量 (默认10)

## 使用方法

```bash
# 启动服务器
uv run mcp-shopping

# 测试工具
mcp-client call search_products '{"query": "手机", "category": "electronics", "limit": 5}'
```
