import csv
import json
import urllib.request
import requests
import pandas as pd
import ssl
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

# 创建未验证的HTTPS上下文
ssl._create_default_https_context = ssl._create_unverified_context

class ShopifyCrawler:
    def __init__(self, website_url: str, output_path: str, with_variants: bool = False):
        """
        初始化爬虫
        
        Args:
            website_url: Shopify 商店的URL (https://shopifystore.com)
            output_path: 输出CSV文件的路径
            with_variants: 是否爬取产品变体数据
        """
        self.base_url = website_url
        self.url = website_url + '/products.json'
        self.output_path = output_path
        self.with_variants = with_variants
        
    def get_page(self, page: int) -> List[Dict]:
        """获取指定页面的产品数据"""
        logger.info(f"获取第 {page} 页产品数据")
        data = urllib.request.urlopen(self.url + f'?page={page}').read()
        products = json.loads(data)['products']
        return products

    def get_tags_from_product(self, product_url: str) -> Tuple[str, str]:
        """获取产品的标题和描述"""
        logger.info(f"获取产品标签信息: {product_url}")
        r = urllib.request.urlopen(product_url).read()
        soup = BeautifulSoup(r, "html.parser")

        title = soup.title.string
        description = ''

        meta = soup.find_all('meta')
        for tag in meta:
            if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() == 'description':
                description = tag.attrs['content']

        return title, description

    def get_variant_attribute(self, variant: Dict, key: str, default: str = '') -> str:
        """安全地获取variant的属性值"""
        return variant.get(key, default)

    def get_inventory_from_product(self, product_url: str) -> pd.DataFrame:
        """获取产品库存信息"""
        logger.info(f"获取产品库存信息: {product_url}")
        get_product = requests.get(product_url)
        product_json = get_product.json()
        product_variants = pd.DataFrame(product_json['product']['variants'])
        return product_variants

    def crawl(self) -> None:
        """开始爬取产品数据"""
        logger.info("开始爬取产品数据")
        
        # 确保输出目录存在
        output_dir = Path(self.output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            page = 1
            writer = csv.writer(f)
            
            # 写入表头
            if self.with_variants:
                writer.writerow([
                    'Name', 'Variant ID', 'Product ID', 'Variant Title', 'Price', 'SKU', 
                    'Position', 'Inventory Policy', 'Compare At Price', 'Fulfillment Service',
                    'Inventory Management', 'Option1', 'Option2', 'Option3', 'Created At',
                    'Updated At', 'Taxable', 'Barcode', 'Grams', 'Image ID', 'Weight',
                    'Weight Unit', 'Inventory Quantity', 'Old Inventory Quantity',
                    'Tax Code', 'Requires Shipping', 'Quantity Rule', 'Price Currency',
                    'Compare At Price Currency', 'Quantity Price Breaks',
                    'URL', 'Meta Title', 'Meta Description', 'Product Description'
                ])
            else:
                writer.writerow(['Name', 'URL', 'Meta Title', 'Meta Description', 'Product Description'])

            logger.info("开始检查产品页面")
            products = self.get_page(page)
            
            while products:
                for product in products:
                    name = product['title']
                    product_url = self.base_url + '/products/' + product['handle']

                    body_description = BeautifulSoup(product['body_html'], "html.parser")
                    body_description = body_description.get_text()

                    logger.info(f"爬取产品: {product_url}")
                    title, description = self.get_tags_from_product(product_url)

                    if self.with_variants:
                        variants_df = self.get_inventory_from_product(product_url + '.json')
                        for _, variant in variants_df.iterrows():
                            row = [
                                name, 
                                self.get_variant_attribute(variant, 'id'),
                                self.get_variant_attribute(variant, 'product_id'),
                                self.get_variant_attribute(variant, 'title'),
                                self.get_variant_attribute(variant, 'price'),
                                self.get_variant_attribute(variant, 'sku'),
                                self.get_variant_attribute(variant, 'position'),
                                self.get_variant_attribute(variant, 'inventory_policy'),
                                self.get_variant_attribute(variant, 'compare_at_price'),
                                self.get_variant_attribute(variant, 'fulfillment_service'),
                                self.get_variant_attribute(variant, 'inventory_management'),
                                self.get_variant_attribute(variant, 'option1'),
                                self.get_variant_attribute(variant, 'option2'),
                                self.get_variant_attribute(variant, 'option3'),
                                self.get_variant_attribute(variant, 'created_at'),
                                self.get_variant_attribute(variant, 'updated_at'),
                                self.get_variant_attribute(variant, 'taxable'),
                                self.get_variant_attribute(variant, 'barcode'),
                                self.get_variant_attribute(variant, 'grams'),
                                self.get_variant_attribute(variant, 'image_id'),
                                self.get_variant_attribute(variant, 'weight'),
                                self.get_variant_attribute(variant, 'weight_unit'),
                                self.get_variant_attribute(variant, 'inventory_quantity'),
                                self.get_variant_attribute(variant, 'old_inventory_quantity'),
                                self.get_variant_attribute(variant, 'tax_code'),
                                self.get_variant_attribute(variant, 'requires_shipping'),
                                self.get_variant_attribute(variant, 'quantity_rule'),
                                self.get_variant_attribute(variant, 'price_currency'),
                                self.get_variant_attribute(variant, 'compare_at_price_currency'),
                                self.get_variant_attribute(variant, 'quantity_price_breaks'),
                                product_url, title, description, body_description
                            ]
                            writer.writerow(row)
                    else:
                        row = [name, product_url, title, description, body_description]
                        writer.writerow(row)
                
                page += 1
                products = self.get_page(page)
        
        logger.info(f"爬取完成，数据已保存到: {self.output_path}")
