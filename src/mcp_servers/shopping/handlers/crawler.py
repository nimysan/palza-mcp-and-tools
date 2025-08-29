"""Product detail crawler for Shopify products"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import json
import re


class ProductCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_product_detail(self, url: str) -> Dict[str, Any]:
        """从Shopify产品页面获取详细信息"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取结构化数据
            product_data = self._extract_json_ld(soup)
            if product_data:
                return self._parse_structured_data(product_data)
            
            # 回退到HTML解析
            return self._parse_html(soup, url)
            
        except Exception as e:
            return {"error": f"Failed to fetch product details: {str(e)}"}
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[Dict]:
        """提取JSON-LD结构化数据"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    return data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            return item
            except:
                continue
        return None
    
    def _parse_structured_data(self, data: Dict) -> Dict[str, Any]:
        """解析结构化数据"""
        offers = data.get('offers', {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        return {
            "name": data.get('name', ''),
            "description": data.get('description', ''),
            "brand": data.get('brand', {}).get('name', ''),
            "price": self._extract_price(offers.get('price')),
            "currency": offers.get('priceCurrency', 'USD'),
            "availability": offers.get('availability', '').split('/')[-1],
            "images": self._extract_images(data.get('image', [])),
            "rating": self._extract_rating(data.get('aggregateRating', {})),
            "features": self._extract_features(data.get('description', '')),
            "source": "structured_data"
        }
    
    def _parse_html(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """HTML解析回退方案"""
        return {
            "name": self._get_text(soup.find('h1')),
            "description": self._get_text(soup.find('div', class_=re.compile(r'product.*description|description.*product', re.I))),
            "price": self._extract_price_from_html(soup),
            "images": self._extract_images_from_html(soup),
            "features": [],
            "source": "html_parsing",
            "url": url
        }
    
    def _extract_price(self, price_str: str) -> Optional[float]:
        """提取价格数值"""
        if not price_str:
            return None
        try:
            # 移除货币符号和空格，提取数字
            price_clean = re.sub(r'[^\d.]', '', str(price_str))
            return float(price_clean) if price_clean else None
        except:
            return None
    
    def _extract_price_from_html(self, soup: BeautifulSoup) -> Optional[float]:
        """从HTML提取价格"""
        price_selectors = [
            '[data-price]',
            '.price',
            '.product-price',
            '[class*="price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get('data-price') or element.get_text()
                price = self._extract_price(price_text)
                if price:
                    return price
        return None
    
    def _extract_images(self, images_data) -> List[str]:
        """提取图片URL列表"""
        if isinstance(images_data, str):
            return [images_data]
        elif isinstance(images_data, list):
            return [img if isinstance(img, str) else img.get('url', '') for img in images_data]
        return []
    
    def _extract_images_from_html(self, soup: BeautifulSoup) -> List[str]:
        """从HTML提取图片"""
        images = []
        img_elements = soup.find_all('img', src=True)
        for img in img_elements:
            src = img.get('src', '')
            if 'product' in src.lower() or 'cdn.shopify' in src:
                images.append(src)
        return images[:5]  # 限制数量
    
    def _extract_rating(self, rating_data: Dict) -> Dict[str, Any]:
        """提取评分信息"""
        if not rating_data:
            return {}
        
        return {
            "rating": rating_data.get('ratingValue'),
            "review_count": rating_data.get('reviewCount'),
            "best_rating": rating_data.get('bestRating', 5)
        }
    
    def _extract_features(self, description: str) -> List[str]:
        """从描述中提取特性列表"""
        if not description:
            return []
        
        # 简单的特性提取逻辑
        features = []
        lines = description.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or ':' in line):
                features.append(line)
        
        return features[:10]  # 限制数量
    
    def _get_text(self, element) -> str:
        """安全获取元素文本"""
        return element.get_text(strip=True) if element else ""
