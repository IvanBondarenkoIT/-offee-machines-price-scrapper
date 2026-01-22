"""
WooCommerce API Client
Fetches product data from WooCommerce store via REST API
"""

import requests
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import os

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.model_extractor import ModelExtractor


class WooCommerceClient:
    """Client for WooCommerce REST API"""
    
    def __init__(self, url: str, consumer_key: str, consumer_secret: str, api_version: str = "wc/v3"):
        """
        Initialize WooCommerce client
        
        Args:
            url: Store URL (e.g., "https://dimkava.ge")
            consumer_key: WooCommerce API consumer key
            consumer_secret: WooCommerce API consumer secret
            api_version: API version (default: "wc/v3")
        """
        self.base_url = url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_version = api_version
        self.api_url = f"{self.base_url}/wp-json/{api_version}"
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.auth = (consumer_key, consumer_secret)
        self.session.headers.update({
            'User-Agent': 'PriceComparisonBot/1.0',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request with error handling
        
        Args:
            endpoint: API endpoint (e.g., "products")
            params: Query parameters
            
        Returns:
            JSON response or None on error
        """
        url = f"{self.api_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] WooCommerce API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Status: {e.response.status_code}")
                print(f"  Response: {e.response.text[:200]}")
            return None
    
    def fetch_all_products(self, stock_status: str = "instock", per_page: int = 100) -> List[Dict]:
        """
        Fetch all products with pagination
        
        Args:
            stock_status: Filter by stock status ("instock", "outofstock", "onbackorder")
            per_page: Products per page (max 100)
            
        Returns:
            List of product dictionaries
        """
        all_products = []
        page = 1
        
        print(f"[WooCommerce] Fetching products (stock_status={stock_status})...")
        
        while True:
            params = {
                'stock_status': stock_status,
                'per_page': per_page,
                'page': page,
                'status': 'publish'  # Only published products
            }
            
            products = self._make_request('products', params)
            
            if not products:
                break
            
            if not isinstance(products, list):
                break
            
            if len(products) == 0:
                break
            
            all_products.extend(products)
            print(f"  Page {page}: {len(products)} products")
            
            # If we got less than per_page, we're done
            if len(products) < per_page:
                break
            
            page += 1
        
        print(f"[OK] Total products fetched: {len(all_products)}")
        return all_products
    
    def get_stock_data(self) -> pd.DataFrame:
        """
        Get stock data as DataFrame
        
        Returns:
            DataFrame with columns: model, name, price, stock_quantity, url
        """
        products = self.fetch_all_products(stock_status='instock')
        
        if not products:
            print("[WARNING] No products found")
            return pd.DataFrame()
        
        data = []
        
        for product in products:
            # Extract model from name
            name = product.get('name', '')
            model = ModelExtractor.extract_model(name)
            
            # Skip if no model found
            if not model:
                continue
            
            # Get price (use sale_price if available, else regular_price)
            regular_price = product.get('regular_price', '')
            sale_price = product.get('sale_price', '')
            price = sale_price if sale_price else regular_price
            
            # Convert price to float
            try:
                price = float(price) if price else None
            except (ValueError, TypeError):
                price = None
            
            # Get stock quantity
            stock_quantity = product.get('stock_quantity', 0)
            try:
                stock_quantity = int(stock_quantity) if stock_quantity else 0
            except (ValueError, TypeError):
                stock_quantity = 0
            
            # Get URL
            url = product.get('permalink', '')
            if not url:
                url = product.get('link', '')
            
            data.append({
                'model': model,
                'name': name,
                'price': price,
                'regular_price': regular_price if regular_price else None,
                'sale_price': sale_price if sale_price else None,
                'stock_quantity': stock_quantity,
                'url': url,
                'sku': product.get('sku', ''),
                'source': 'WOOCOMMERCE'
            })
        
        df = pd.DataFrame(data)
        
        if len(df) > 0:
            print(f"[OK] Processed {len(df)} products with models")
        else:
            print("[WARNING] No products with extractable models")
        
        return df


def get_woocommerce_config() -> Optional[Dict]:
    """
    Get WooCommerce configuration from environment variables
    
    Returns:
        Dict with config or None if not configured
    """
    url = os.getenv('WC_URL')
    consumer_key = os.getenv('WC_CONSUMER_KEY')
    consumer_secret = os.getenv('WC_CONSUMER_SECRET')
    
    if not all([url, consumer_key, consumer_secret]):
        return None
    
    return {
        'url': url,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'api_version': os.getenv('WC_API_VERSION', 'wc/v3')
    }


if __name__ == "__main__":
    # Test client
    config = get_woocommerce_config()
    
    if not config:
        print("[ERROR] WooCommerce configuration not found in environment variables")
        print("  Required: WC_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET")
        exit(1)
    
    client = WooCommerceClient(**config)
    df = client.get_stock_data()
    
    if len(df) > 0:
        print(f"\n[OK] Retrieved {len(df)} products")
        print("\nFirst 5 products:")
        print(df.head().to_string())
    else:
        print("\n[WARNING] No products retrieved")
