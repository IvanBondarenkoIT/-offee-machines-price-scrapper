"""
Stock API Client - Get inventory data from remote API
Supports fallback to Excel file if API is unavailable
"""

import requests
import pandas as pd
import time
from typing import Optional, Dict, List
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.model_extractor import ModelExtractor

logger = setup_logger("stock_api_client")


class StockApiClient:
    """
    Client for fetching stock data from Proxy API
    
    Converts API response to DataFrame format compatible with InventoryParser
    """
    
    # SQL Query for stock data (from STOCK_API_INTEGRATION.md)
    STOCK_QUERY = """
    SELECT 
        GG.NAME as GROUP_NAME,
        G.OWNER as GROUP_ID,
        G.ID as GOOD_ID,
        G.NAME as GOOD_NAME,
        COALESCE(SUM(GDD.QUANT), 0) as QUANTITY,
        COALESCE(
            CASE 
                WHEN SUM(GDD.QUANT) > 0 
                THEN SUM(GDD.QUANT * GDD.PRICE) / SUM(GDD.QUANT)
                ELSE 0
            END,
            0
        ) as PRICE,
        COALESCE(SUM(GDD.QUANT), 0) * 
        COALESCE(
            CASE 
                WHEN SUM(GDD.QUANT) > 0 
                THEN SUM(GDD.QUANT * GDD.PRICE) / SUM(GDD.QUANT)
                ELSE 0
            END,
            0
        ) as TOTAL_SUM
    FROM GOODS G
    LEFT JOIN GOODSGROUPS GG ON G.OWNER = GG.ID
    LEFT JOIN GDDKT GDD ON G.ID = GDD.GDSKEY
        AND GDD.PRICE IS NOT NULL 
        AND GDD.PRICE > 0
        AND GDD.QUANT IS NOT NULL
    GROUP BY 
        G.ID,
        G.NAME,
        G.OWNER,
        GG.NAME
    HAVING SUM(GDD.QUANT) > 0
    ORDER BY 
        GG.NAME,
        G.NAME
    """
    
    # Valid brands (from InventoryParser)
    VALID_BRANDS = [
        'DELONGHI', 'DE LONGHI', "DE'LONGHI",
        'MELITTA', 'MELITA',
        'NIVONA',
        'JURA',
        'SAECO',
        'GAGGIA',
    ]
    
    # Accessories and spare parts keywords (from InventoryParser)
    SPARE_PARTS_KEYWORDS = [
        'ASSY', 'PCB', 'TUBE', 'FUNNEL', 'SUPPORT', 'DRAINING',
        'CARAF', 'TANK', 'PIPE', 'CONNECTOR', 'VALVE', 'GASKET',
        'SEAL', 'SPRING', 'SCREW', 'NUT', 'BOLT', 'WASHER',
        'O-RING', 'BEARING', 'MOTOR', 'PUMP', 'SENSOR', 'SWITCH',
        'CABLE', 'WIRE', 'BOARD', 'DISPLAY', 'BUTTON', 'KNOB',
    ]
    
    ACCESSORIES_KEYWORDS = [
        'PITCHER', 'TAMPER', 'SPOON', 'MAT', 'BRUSH', 'CLOTH',
        'DESCAL', 'CLEAN', 'TABLET', 'LIQUID', 'POWDER',
        'FILTER', 'CARTRIDGE', 'SOFTBAL',
    ]
    
    def __init__(
        self, 
        api_url: str, 
        api_token: Optional[str] = None,
        fallback_token: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize Stock API Client
        
        Args:
            api_url: API endpoint URL (e.g., http://85.114.224.45:8000)
            api_token: Primary API token
            fallback_token: Fallback API token if primary fails
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.fallback_token = fallback_token
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Stats
        self.stats = {
            'total_products': 0,
            'valid_products': 0,
            'spare_parts': 0,
            'accessories': 0,
            'no_brand': 0,
            'no_model': 0,
        }
    
    def get_stock_data(self) -> pd.DataFrame:
        """
        Get stock data from API and convert to DataFrame
        
        Returns:
            DataFrame with columns compatible with InventoryParser:
            - name, model, brand, quantity, price, category, is_valid, source
        
        Raises:
            Exception: If API request fails after all retries
        """
        logger.info("="*60)
        logger.info("FETCHING STOCK DATA FROM API")
        logger.info("="*60)
        logger.info(f"API URL: {self.api_url}")
        
        # Try primary token first
        api_response = None
        token_used = None
        
        if self.api_token:
            try:
                logger.info("Attempting with primary token...")
                api_response = self._make_request(self.api_token)
                token_used = "primary"
                logger.info("[OK] Primary token succeeded")
            except Exception as e:
                logger.warning(f"Primary token failed: {e}")
                
                # Try fallback token
                if self.fallback_token:
                    try:
                        logger.info("Attempting with fallback token...")
                        api_response = self._make_request(self.fallback_token)
                        token_used = "fallback"
                        logger.info("[OK] Fallback token succeeded")
                    except Exception as e2:
                        logger.error(f"Fallback token also failed: {e2}")
                        raise Exception("Both primary and fallback tokens failed") from e2
                else:
                    raise
        else:
            # No token (public API)
            logger.info("No token provided, trying without authentication...")
            api_response = self._make_request(None)
            token_used = "none"
        
        if not api_response:
            raise Exception("Failed to get response from API")
        
        # Convert to DataFrame
        df = self._convert_to_dataframe(api_response)
        
        logger.info("="*60)
        logger.info(f"STOCK DATA LOADED SUCCESSFULLY (token: {token_used})")
        logger.info(f"Total products from API: {len(df)}")
        logger.info(f"Valid products: {self.stats['valid_products']}")
        logger.info("="*60)
        
        return df
    
    def _make_request(self, token: Optional[str]) -> Dict:
        """
        Make API request with retry logic
        
        Args:
            token: API token (or None)
            
        Returns:
            API response as dict
            
        Raises:
            Exception: If all retry attempts fail
        """
        # Prepare request
        url = f"{self.api_url}/api/query"
        headers = {
            "Content-Type": "application/json"
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        payload = {
            "query": self.STOCK_QUERY
        }
        
        # Retry loop
        last_exception = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.info(f"API request attempt {attempt}/{self.retry_attempts}...")
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                # Check status
                response.raise_for_status()
                
                # Parse JSON
                data = response.json()
                
                # Check success
                if not data.get('success'):
                    error_msg = data.get('error', 'Unknown error')
                    raise Exception(f"API returned error: {error_msg}")
                
                # Check data
                if 'data' not in data:
                    raise Exception("API response missing 'data' field")
                
                logger.info(f"[OK] Got {len(data['data'])} products from API")
                return data
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} timeout after {self.timeout}s")
                
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} connection error: {e}")
                
            except requests.exceptions.HTTPError as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} HTTP error: {e}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
            
            # Wait before retry (unless last attempt)
            if attempt < self.retry_attempts:
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        # All attempts failed
        raise Exception(f"API request failed after {self.retry_attempts} attempts") from last_exception
    
    def _convert_to_dataframe(self, api_response: Dict) -> pd.DataFrame:
        """
        Convert API response to DataFrame format compatible with InventoryParser
        
        API fields → DataFrame fields:
        - GOOD_NAME → name
        - GOOD_ID → good_id (new)
        - QUANTITY → quantity
        - PRICE → price
        - GROUP_NAME → group_name (new)
        
        Extracted fields:
        - model → extracted using ModelExtractor
        - brand → extracted from name
        - category → product/spare_part/accessory
        - is_valid → calculated
        - source → 'INVENTORY' (for compatibility)
        
        Args:
            api_response: API response dict with 'data' field
            
        Returns:
            DataFrame with InventoryParser-compatible structure
        """
        logger.info("Converting API response to DataFrame...")
        
        products = []
        raw_data = api_response['data']
        
        self.stats['total_products'] = len(raw_data)
        
        for item in raw_data:
            try:
                # Extract basic fields
                name = item.get('GOOD_NAME', '').strip()
                if not name or len(name) < 3:
                    continue
                
                good_id = item.get('GOOD_ID')
                quantity = float(item.get('QUANTITY', 0))
                price = float(item.get('PRICE', 0))
                group_name = item.get('GROUP_NAME', '').strip()
                
                # Skip if no price (likely not a product)
                if price <= 0:
                    continue
                
                # Extract brand
                brand = self._extract_brand(name)
                
                # Extract model
                model = self._extract_model(name)
                
                # Categorize
                category = self._categorize_product(name)
                
                # Validate
                is_valid = self._is_valid_product(name, brand, model, category, price)
                
                # Build product dict
                product = {
                    'name': name,
                    'model': model,
                    'brand': brand,
                    'quantity': quantity,
                    'price': price,
                    'category': category,
                    'is_valid': is_valid,
                    'source': 'INVENTORY',
                    # Extra fields from API (for reference)
                    'good_id': good_id,
                    'group_name': group_name,
                }
                
                products.append(product)
                
                # Update stats
                if category == 'spare_part':
                    self.stats['spare_parts'] += 1
                elif category == 'accessory':
                    self.stats['accessories'] += 1
                
                if is_valid:
                    self.stats['valid_products'] += 1
                
                if not brand:
                    self.stats['no_brand'] += 1
                if not model:
                    self.stats['no_model'] += 1
                    
            except Exception as e:
                logger.warning(f"Error processing item: {e}")
                continue
        
        df = pd.DataFrame(products)
        
        logger.info(f"[OK] Converted {len(df)} products")
        logger.info(f"     Valid: {self.stats['valid_products']}")
        logger.info(f"     Spare parts: {self.stats['spare_parts']}")
        logger.info(f"     Accessories: {self.stats['accessories']}")
        
        # Filter to valid products only (like InventoryParser.get_valid_products())
        df_valid = df[df['is_valid'] == True].copy()
        logger.info(f"[OK] Filtered to {len(df_valid)} valid products")
        
        return df_valid
    
    def _extract_brand(self, name: str) -> Optional[str]:
        """Extract brand from product name (same logic as InventoryParser)"""
        name_upper = name.upper()
        
        for brand in self.VALID_BRANDS:
            if brand in name_upper:
                if 'DELONGHI' in brand or 'DE LONGHI' in brand:
                    return 'DeLonghi'
                elif 'MELITTA' in brand or 'MELITA' in brand:
                    return 'Melitta'
                elif 'NIVONA' in brand:
                    return 'Nivona'
                elif 'JURA' in brand:
                    return 'Jura'
                elif 'SAECO' in brand:
                    return 'Saeco'
                elif 'GAGGIA' in brand:
                    return 'Gaggia'
        
        return None
    
    def _extract_model(self, name: str) -> Optional[str]:
        """Extract model from product name using ModelExtractor"""
        try:
            model = ModelExtractor.extract_model(name)
            return model if model else None
        except Exception as e:
            logger.debug(f"Error extracting model from '{name}': {e}")
            return None
    
    def _categorize_product(self, name: str) -> str:
        """Categorize as product/spare_part/accessory (same logic as InventoryParser)"""
        name_upper = name.upper()
        
        # Check spare parts
        for keyword in self.SPARE_PARTS_KEYWORDS:
            if keyword in name_upper:
                return 'spare_part'
        
        # Check accessories
        for keyword in self.ACCESSORIES_KEYWORDS:
            if keyword in name_upper:
                return 'accessory'
        
        return 'product'
    
    def _is_valid_product(
        self, 
        name: str, 
        brand: Optional[str], 
        model: Optional[str], 
        category: str,
        price: float
    ) -> bool:
        """Validate product (same logic as InventoryParser)"""
        # Must be a product
        if category != 'product':
            return False
        
        # Must have brand
        if not brand:
            return False
        
        # Must have reasonable price
        if price < 50:
            return False
        
        # Check for spare part indicators
        name_upper = name.upper()
        spare_indicators = ['SPARE', 'PART', 'REPLACEMENT', 'REPAIR']
        if any(ind in name_upper for ind in spare_indicators):
            return False
        
        # Exclude very short names
        if len(name) < 10:
            return False
        
        return True


def main():
    """Test the API client"""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get config from env
    api_url = os.getenv('STOCK_API_URL')
    api_token = os.getenv('STOCK_API_TOKEN')
    fallback_token = os.getenv('STOCK_API_FALLBACK_TOKEN')
    timeout = int(os.getenv('STOCK_API_TIMEOUT', '30'))
    
    if not api_url:
        print("[ERROR] STOCK_API_URL not set in .env file")
        return
    
    # Create client
    client = StockApiClient(
        api_url=api_url,
        api_token=api_token,
        fallback_token=fallback_token,
        timeout=timeout
    )
    
    # Get data
    try:
        df = client.get_stock_data()
        print(f"\n[SUCCESS] Loaded {len(df)} valid products")
        print(f"\nBrand distribution:")
        print(df['brand'].value_counts())
        print(f"\nFirst 5 products:")
        print(df[['name', 'brand', 'model', 'quantity', 'price']].head())
        
    except Exception as e:
        print(f"\n[ERROR] Failed to load data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

