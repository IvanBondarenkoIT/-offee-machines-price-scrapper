"""
WooCommerce API Client - Get stock data from WooCommerce REST API
Fetches products with stock_quantity > 0 and extracts prices (regular_price, sale_price)
"""

import time
from typing import Optional, Dict, List
from pathlib import Path
import sys
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.model_extractor import ModelExtractor

logger = setup_logger("woocommerce_client")

try:
    from woocommerce import API
except ImportError:
    logger.error("woocommerce package not installed. Run: pip install woocommerce")
    API = None


class WooCommerceClient:
    """
    Client for fetching stock data from WooCommerce REST API
    
    Converts API response to DataFrame format compatible with price comparison
    """
    
    def __init__(
        self,
        url: str,
        consumer_key: str,
        consumer_secret: str,
        api_version: str = "wc/v3",
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize WooCommerce API Client
        
        Args:
            url: WooCommerce store URL (e.g., https://dimkava.ge)
            consumer_key: WooCommerce API consumer key
            consumer_secret: WooCommerce API consumer secret
            api_version: API version (default: wc/v3)
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        if API is None:
            raise ImportError("woocommerce package not installed. Run: pip install woocommerce")
        
        self.url = url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_version = api_version
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Initialize WooCommerce API client
        self.wcapi = API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version=self.api_version,
            timeout=self.timeout,
            query_string_auth=True  # Use query string auth (more compatible)
        )
        
        # CRITICAL: Set User-Agent to bypass Imunify360 bot protection
        # This makes requests look like they come from a real browser
        import os
        from config import WOOCOMMERCE_CONFIG
        user_agent = WOOCOMMERCE_CONFIG.get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Set User-Agent using the API's user_agent attribute (preferred method)
        if hasattr(self.wcapi, 'user_agent'):
            self.wcapi.user_agent = user_agent
            logger.debug(f"Set User-Agent via wcapi.user_agent: {user_agent[:50]}...")
        # Fallback: Try to set through session if user_agent attribute doesn't work
        elif hasattr(self.wcapi, 'session'):
            self.wcapi.session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            logger.debug(f"Set User-Agent via wcapi.session: {user_agent[:50]}...")
        elif hasattr(self.wcapi, '_session'):
            self.wcapi._session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            logger.debug(f"Set User-Agent via wcapi._session: {user_agent[:50]}...")
        else:
            logger.warning("Could not set User-Agent. Imunify360 may block requests.")
        
        # Stats
        self.stats = {
            'total_products': 0,
            'in_stock_products': 0,
            'with_discount': 0,
            'no_model': 0,
        }
    
    def get_stock_data(self) -> pd.DataFrame:
        """
        Get stock data from WooCommerce API and convert to DataFrame
        
        Returns:
            DataFrame with columns:
            - name: product name
            - model: extracted model code
            - stock_quantity: stock quantity (only > 0)
            - sku: product SKU
            - price: current price (sale_price if available, else regular_price)
            - regular_price: regular price (without discount)
            - sale_price: sale price (if discount exists)
            - has_discount: boolean flag for discount
            - product_id: WooCommerce product ID
        
        Raises:
            Exception: If API request fails after all retries
        """
        logger.info("="*60)
        logger.info("FETCHING STOCK DATA FROM WOOCOMMERCE API")
        logger.info("="*60)
        logger.info(f"Store URL: {self.url}")
        
        # Fetch all products with pagination
        all_products = []
        page = 1
        per_page = 100  # WooCommerce default max per page
        
        while True:
            try:
                logger.info(f"Fetching page {page}...")
                products = self._fetch_products_page(page, per_page)
                
                if not products:
                    logger.info(f"No more products on page {page}, stopping pagination")
                    break
                
                all_products.extend(products)
                logger.info(f"[OK] Got {len(products)} products from page {page}")
                
                # If we got less than per_page, we're on the last page
                if len(products) < per_page:
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                # If it's the first page, fail completely
                if page == 1:
                    raise
                # Otherwise, stop pagination and use what we have
                logger.warning(f"Stopping pagination due to error, using {len(all_products)} products")
                break
        
        self.stats['total_products'] = len(all_products)
        logger.info(f"Total products fetched: {len(all_products)}")
        
        # Convert to DataFrame
        df = self._convert_to_dataframe(all_products)
        
        logger.info("="*60)
        logger.info("WOOCOMMERCE STOCK DATA LOADED SUCCESSFULLY")
        logger.info(f"Total products: {self.stats['total_products']}")
        logger.info(f"In stock (stock_quantity > 0): {self.stats['in_stock_products']}")
        logger.info(f"With discount: {self.stats['with_discount']}")
        logger.info(f"No model extracted: {self.stats['no_model']}")
        logger.info("="*60)
        
        return df
    
    def _fetch_products_page(self, page: int, per_page: int) -> List[Dict]:
        """
        Fetch a single page of products from WooCommerce API
        
        Args:
            page: Page number (1-based)
            per_page: Number of products per page
            
        Returns:
            List of product dictionaries from API
            
        Raises:
            Exception: If API request fails after all retries
        """
        # Retry loop
        last_exception = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.debug(f"API request attempt {attempt}/{self.retry_attempts} (page {page})...")
                
                # Make API request
                response = self.wcapi.get('products', params={
                    'per_page': per_page,
                    'page': page,
                    'stock_status': 'instock',  # Only products in stock
                    'status': 'publish',  # Only published products
                })
                
                # Check status code
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict) and 'message' in error_data:
                            error_msg = error_data['message']
                    except:
                        pass
                    raise Exception(f"API returned error: {error_msg}")
                
                # Parse JSON
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    # Direct list of products
                    products = data
                elif isinstance(data, dict):
                    # Check for error message
                    if 'message' in data:
                        error_msg = data.get('message', 'Unknown error')
                        error_code = data.get('code', 'unknown')
                        logger.error(f"API error: [{error_code}] {error_msg}")
                        
                        # Special handling for Imunify360 protection
                        if 'Imunify360' in error_msg or 'bot-protection' in error_msg.lower():
                            logger.error("="*60)
                            logger.error("IMUNIFY360 PROTECTION BLOCKED REQUEST")
                            logger.error("="*60)
                            logger.error("Solution: Add your IP address to Imunify360 whitelist on the server")
                            logger.error("Contact server administrator to whitelist your IP for API access")
                            logger.error("="*60)
                        
                        raise Exception(f"API returned error [{error_code}]: {error_msg}")
                    
                    # Check for error code
                    if 'code' in data and 'message' in data:
                        error_msg = data.get('message', 'Unknown error')
                        error_code = data.get('code', 'unknown')
                        logger.error(f"API error: [{error_code}] {error_msg}")
                        raise Exception(f"API returned error [{error_code}]: {error_msg}")
                    
                    # Check if products are in a nested structure
                    if 'products' in data:
                        products = data['products']
                    elif 'data' in data:
                        products = data['data']
                    else:
                        # Try to find list-like structure
                        for key, value in data.items():
                            if isinstance(value, list):
                                products = value
                                logger.warning(f"Found products in unexpected key '{key}'")
                                break
                        else:
                            logger.error(f"API response structure: {data}")
                            raise Exception(f"API response is dict but no products found. Keys: {list(data.keys())}")
                else:
                    raise Exception(f"API response is unexpected type: {type(data)}")
                
                if not isinstance(products, list):
                    raise Exception(f"Products is not a list: {type(products)}")
                
                logger.debug(f"[OK] Got {len(products)} products from page {page}")
                return products
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                
                # Wait before retry (unless last attempt)
                if attempt < self.retry_attempts:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
        
        # All attempts failed
        raise Exception(f"API request failed after {self.retry_attempts} attempts") from last_exception
    
    def _convert_to_dataframe(self, products: List[Dict]) -> pd.DataFrame:
        """
        Convert WooCommerce API products to DataFrame
        
        Filters: only products with stock_quantity > 0
        
        Args:
            products: List of product dictionaries from API
            
        Returns:
            DataFrame with filtered and processed products
        """
        logger.info("Converting WooCommerce products to DataFrame...")
        
        processed_products = []
        
        for product in products:
            try:
                # Extract basic fields
                product_id = product.get('id')
                name = product.get('name', '').strip()
                sku = product.get('sku', '').strip()
                
                if not name:
                    continue
                
                # Stock information
                stock_quantity = product.get('stock_quantity')
                stock_status = product.get('stock_status', '')
                
                # Filter: only products with stock_quantity > 0
                if stock_quantity is None:
                    stock_quantity = 0
                else:
                    try:
                        stock_quantity = int(stock_quantity)
                    except (ValueError, TypeError):
                        stock_quantity = 0
                
                if stock_quantity <= 0:
                    continue  # Skip products without stock
                
                # Price information
                regular_price_str = product.get('regular_price', '')
                sale_price_str = product.get('sale_price', '')
                
                # Convert prices to float
                regular_price = None
                sale_price = None
                
                if regular_price_str:
                    try:
                        regular_price = float(regular_price_str)
                    except (ValueError, TypeError):
                        regular_price = None
                
                if sale_price_str:
                    try:
                        sale_price = float(sale_price_str)
                    except (ValueError, TypeError):
                        sale_price = None
                
                # Determine current price and discount status
                if sale_price and sale_price > 0:
                    current_price = sale_price
                    has_discount = True
                elif regular_price and regular_price > 0:
                    current_price = regular_price
                    has_discount = False
                else:
                    # No valid price, skip
                    continue
                
                # Extract model from product name
                model = self._extract_model(name)
                
                # Build product dict
                product_data = {
                    'name': name,
                    'model': model,
                    'stock_quantity': stock_quantity,
                    'sku': sku,
                    'price': current_price,
                    'regular_price': regular_price,
                    'sale_price': sale_price if has_discount else None,
                    'has_discount': has_discount,
                    'product_id': product_id,
                    'stock_status': stock_status,
                }
                
                processed_products.append(product_data)
                
                # Update stats
                self.stats['in_stock_products'] += 1
                if has_discount:
                    self.stats['with_discount'] += 1
                if not model:
                    self.stats['no_model'] += 1
                    
            except Exception as e:
                logger.warning(f"Error processing product: {e}")
                continue
        
        df = pd.DataFrame(processed_products)
        
        logger.info(f"[OK] Converted {len(df)} products with stock > 0")
        
        return df
    
    def _extract_model(self, name: str) -> Optional[str]:
        """Extract model from product name using ModelExtractor"""
        try:
            model = ModelExtractor.extract_model(name)
            return model if model else None
        except Exception as e:
            logger.debug(f"Error extracting model from '{name}': {e}")
            return None


def main():
    """Test the WooCommerce API client"""
    import os
    from dotenv import load_dotenv
    from config import WOOCOMMERCE_CONFIG
    
    # Load environment variables
    load_dotenv()
    
    # Check if enabled
    if not WOOCOMMERCE_CONFIG.get("enabled", False):
        print("[INFO] WooCommerce integration is disabled (USE_WOOCOMMERCE_STOCK=false)")
        return
    
    # Validate config
    if not WOOCOMMERCE_CONFIG.get("url"):
        print("[ERROR] WC_URL not set in .env file")
        return
    
    if not WOOCOMMERCE_CONFIG.get("consumer_key"):
        print("[ERROR] WC_CONSUMER_KEY not set in .env file")
        return
    
    if not WOOCOMMERCE_CONFIG.get("consumer_secret"):
        print("[ERROR] WC_CONSUMER_SECRET not set in .env file")
        return
    
    # Create client
    client = WooCommerceClient(
        url=WOOCOMMERCE_CONFIG["url"],
        consumer_key=WOOCOMMERCE_CONFIG["consumer_key"],
        consumer_secret=WOOCOMMERCE_CONFIG["consumer_secret"],
        api_version=WOOCOMMERCE_CONFIG.get("api_version", "wc/v3"),
        timeout=WOOCOMMERCE_CONFIG.get("timeout", 30),
        retry_attempts=WOOCOMMERCE_CONFIG.get("retry_attempts", 3),
        retry_delay=WOOCOMMERCE_CONFIG.get("retry_delay", 2)
    )
    
    # Get data
    try:
        df = client.get_stock_data()
        print(f"\n[SUCCESS] Loaded {len(df)} products with stock > 0")
        print(f"\nPrice statistics:")
        print(f"  With discount: {client.stats['with_discount']}")
        print(f"  Without discount: {len(df) - client.stats['with_discount']}")
        print(f"\nFirst 5 products:")
        print(df[['name', 'model', 'stock_quantity', 'price', 'regular_price', 'sale_price', 'has_discount']].head())
        
    except Exception as e:
        print(f"\n[ERROR] Failed to load data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
