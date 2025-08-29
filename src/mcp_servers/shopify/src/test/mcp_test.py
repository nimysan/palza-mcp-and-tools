import logging
import asyncio
import json
from products_repository.shopify_products import search_products, ProductFilter

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.INFO)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", 
    handlers=[logging.StreamHandler()]
)

async def main():
    results = await search_products(
        description="",
        min_price="0",
        max_price="400",
        category="",
        scenario="camping"
    )
    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
