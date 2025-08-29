from .shopify_products import mcp as my_mcp
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def joke():
    # 实现代码...
    # pass
    logger.info("hello")
    my_mcp.run(transport='stdio')


if __name__ == "__main__":
    joke()
