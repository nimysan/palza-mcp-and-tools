"""Shopping service implementation"""

import pandas as pd
import json
from typing import Optional, Dict, Any
from pathlib import Path

class ShoppingService:
    def __init__(self):
        self.csv_path = Path(__file__).parent.parent / "shopify" / "data" / "products.csv"
        self._df = None
    
    def _load_products(self) -> pd.DataFrame:
        """加载产品数据"""
        if self._df is None:
            try:
                self._df = pd.read_csv(self.csv_path)
            except Exception as e:
                print(f"Error loading products: {e}")
                self._df = pd.DataFrame()
        return self._df
    
    def search_products(
        self,
        query: str,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        sort_by: str = "relevance",
        limit: int = 20
    ) -> Dict[str, Any]:
        """搜索商品"""
        df = self._load_products()
        if df.empty:
            return {"error": "产品数据加载失败"}
        
        # 搜索过滤
        mask = df['Name'].str.contains(query, case=False, na=False) | \
               df['Product Description'].str.contains(query, case=False, na=False)
        
        if price_min is not None:
            mask &= df['Price'] >= price_min
        if price_max is not None:
            mask &= df['Price'] <= price_max
        
        results = df[mask].copy()
        
        # 排序
        if sort_by == "price_asc":
            results = results.sort_values('Price')
        elif sort_by == "price_desc":
            results = results.sort_values('Price', ascending=False)
        elif sort_by == "name":
            results = results.sort_values('Name')
        elif sort_by == "newest":
            results = results.sort_values('Created At', ascending=False)
        
        results = results.head(limit)
        
        products = []
        for _, row in results.iterrows():
            products.append({
                "product_id": str(row['Product ID']),
                "variant_id": str(row['Variant ID']),
                "name": row['Name'],
                "price": float(row['Price']),
                "compare_at_price": float(row['Compare At Price']) if pd.notna(row['Compare At Price']) else None,
                "sku": row['SKU'],
                "url": row['URL'],
                "inventory_quantity": int(row['Inventory Quantity']) if pd.notna(row['Inventory Quantity']) else 0
            })
        
        return {
            "query": query,
            "total_found": len(results),
            "products": products,
            "filters_applied": {
                "price_min": price_min,
                "price_max": price_max,
                "sort_by": sort_by
            }
        }
    
    def get_product_detail(self, product_id: str) -> Dict[str, Any]:
        """获取商品详情"""
        df = self._load_products()
        if df.empty:
            return {"error": "产品数据加载失败"}
        
        product = df[df['Product ID'] == int(product_id)]
        if product.empty:
            return {"error": f"未找到商品ID: {product_id}"}
        
        variants = []
        for _, row in product.iterrows():
            variants.append({
                "variant_id": str(row['Variant ID']),
                "title": row['Variant Title'],
                "price": float(row['Price']),
                "compare_at_price": float(row['Compare At Price']) if pd.notna(row['Compare At Price']) else None,
                "sku": row['SKU'],
                "inventory_quantity": int(row['Inventory Quantity']) if pd.notna(row['Inventory Quantity']) else 0,
                "weight": f"{row['Weight']} {row['Weight Unit']}" if pd.notna(row['Weight']) else None,
                "barcode": row['Barcode'] if pd.notna(row['Barcode']) else None
            })
        
        first_row = product.iloc[0]
        return {
            "product_id": product_id,
            "name": first_row['Name'],
            "description": first_row['Product Description'],
            "meta_title": first_row['Meta Title'],
            "meta_description": first_row['Meta Description'],
            "url": first_row['URL'],
            "created_at": first_row['Created At'],
            "updated_at": first_row['Updated At'],
            "taxable": bool(first_row['Taxable']),
            "requires_shipping": bool(first_row['Requires Shipping']),
            "variants": variants,
            "total_variants": len(variants)
        }
    
    def check_inventory(
        self,
        product_id: str,
        variant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """检查库存"""
        df = self._load_products()
        if df.empty:
            return {"error": "产品数据加载失败"}
        
        if variant_id:
            inventory = df[df['Variant ID'] == int(variant_id)]
            if inventory.empty:
                return {"error": f"未找到变体ID: {variant_id}"}
        else:
            inventory = df[df['Product ID'] == int(product_id)]
            if inventory.empty:
                return {"error": f"未找到商品ID: {product_id}"}
        
        inventory_info = []
        total_quantity = 0
        
        for _, row in inventory.iterrows():
            qty = int(row['Inventory Quantity']) if pd.notna(row['Inventory Quantity']) else 0
            total_quantity += qty
            
            inventory_info.append({
                "variant_id": str(row['Variant ID']),
                "variant_title": row['Variant Title'],
                "sku": row['SKU'],
                "inventory_quantity": qty,
                "inventory_policy": row['Inventory Policy'],
                "fulfillment_service": row['Fulfillment Service'],
                "inventory_management": row['Inventory Management']
            })
        
        return {
            "product_id": product_id,
            "variant_id": variant_id,
            "total_inventory": total_quantity,
            "inventory_details": inventory_info,
            "low_stock_threshold": 10,
            "is_low_stock": total_quantity < 10
        }
    
    def get_recommendations(
        self,
        recommendation_type: str,
        product_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """获取推荐"""
        df = self._load_products()
        if df.empty:
            return {"error": "产品数据加载失败"}
        
        unique_products = df.drop_duplicates(subset=['Product ID'])
        
        if recommendation_type == "similar" and product_id:
            base_product = df[df['Product ID'] == int(product_id)]
            if not base_product.empty:
                base_price = base_product.iloc[0]['Price']
                price_range = base_price * 0.3
                similar = unique_products[
                    (unique_products['Price'] >= base_price - price_range) &
                    (unique_products['Price'] <= base_price + price_range) &
                    (unique_products['Product ID'] != int(product_id))
                ]
                recommendations = similar.head(limit)
            else:
                recommendations = unique_products.head(limit)
        elif recommendation_type == "price_range":
            recommendations = unique_products.sort_values('Price').head(limit)
        elif recommendation_type == "newest":
            recommendations = unique_products.sort_values('Created At', ascending=False).head(limit)
        else:  # random
            recommendations = unique_products.sample(n=min(limit, len(unique_products)))
        
        products = []
        for _, row in recommendations.iterrows():
            products.append({
                "product_id": str(row['Product ID']),
                "name": row['Name'],
                "price": float(row['Price']),
                "compare_at_price": float(row['Compare At Price']) if pd.notna(row['Compare At Price']) else None,
                "url": row['URL'],
                "reason": f"基于{recommendation_type}推荐"
            })
        
        return {
            "recommendation_type": recommendation_type,
            "base_product_id": product_id,
            "total_recommendations": len(products),
            "recommendations": products
        }
