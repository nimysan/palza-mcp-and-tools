# MCP Servers Collection

一个包含多个 MCP (Model Context Protocol) 服务器的项目。

## 可用的 MCP 服务器

- **mcp-shopify-products**: Shopify 产品信息服务器
- **mcp-weather**: 天气信息服务器

## 项目结构

```
mcp-server/
├── README.md
├── pyproject.toml
└── src/
    └── mcp_servers/
        ├── __init__.py
        ├── shopify/          # Shopify MCP 服务器
        │   ├── __init__.py
        │   ├── main.py
        │   └── ...           # 原有的 shopify 代码
        └── weather/          # Weather MCP 服务器
            ├── __init__.py
            ├── main.py
            └── ...           # 原有的 weather 代码
```

## 快速开始

### 本地开发

```bash
# 克隆项目
cd /Users/yexw/PycharmProjects/mcp/mcp-server

# 运行 MCP 服务器
uv run mcp-shopify-products
uv run mcp-weather
```

### 全局安装

```bash
# 可编辑安装
uv tool install --editable .

# 使用
uv run mcp-shopify-products
uv run mcp-weather
```

## 添加新的 MCP 服务器

1. 在 `src/mcp_servers/` 中创建新目录，如 `new_service/`
2. 添加 `__init__.py` 和 `main.py`
3. 在 `pyproject.toml` 中添加对应的 `[project.scripts]` 条目：
   ```toml
   mcp-new-service = "mcp_servers.new_service.main:main"
   ```
4. 使用 `uv run mcp-new-service` 测试

## 技术特点

- 使用 `uv` 作为包管理器
- 现代 Python 项目结构（src layout）
- 单包多服务架构
- 支持 `uvx` 直接运行
- 快速开发迭代
