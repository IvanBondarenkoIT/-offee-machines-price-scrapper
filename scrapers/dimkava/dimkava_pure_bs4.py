"""
DIM KAVA Pure BeautifulSoup Scraper (NO Selenium)
Uses only requests + BeautifulSoup for Railway compatibility
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv

logger = setup_logger("dimkava_pure_bs4")


class DimKavaPureBS4Scraper:
    """Pure BeautifulSoup scraper for DIM KAVA (no Selenium)"""
    
    def __init__(self):
        self.url = "https://dimkava.ge/brand/delonghi/"
        self.products = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_page(self):
        """Fetch page HTML"""
        logger.info(f"Fetching: {self.url}")
        
        try:
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            logger.info(f"[OK] Page loaded ({len(response.content)} bytes)")
            return response.text
        except Exception as e:
            logger.error(f"[ERROR] Failed to fetch page: {e}")
            raise
    
    def clean_price(self, price_str):
        """Extract numeric price from string"""
        if not price_str:
            return None
        
        # Remove all non-digits except decimal point
        cleaned = re.sub(r'[^\d.]', '', price_str)
        
        try:
            return float(cleaned) if cleaned else None
        except:
            return None
    
    def parse_products(self, html):
        """Parse products from HTML"""
        logger.info("Parsing products...")
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Find product list
        product_items = soup.find_all('li', class_='product')
        
        if not product_items:
            # Try alternative selector
            product_items = soup.select('ul li')
            logger.info(f"Found {len(product_items)} li elements")
        
        logger.info(f"Found {len(product_items)} product items")
        
        idx = 0
        for li_elem in product_items:
            try:
                # Get product name
                name_elem = li_elem.select_one('h2 a') or li_elem.select_one('.woocommerce-loop-product__title')
                
                if not name_elem:
                    continue
                
                name = name_elem.get_text(strip=True)
                
                # Skip if not DeLonghi or if it's a category/header
                if not name or len(name) < 5:
                    continue
                
                idx += 1
                
                # Get product URL
                product_url = name_elem.get('href', self.url)
                
                # Check for discount
                has_discount = bool(li_elem.select_one('.onsale'))
                
                # Get prices
                regular_price_str = None
                discount_price_str = None
                
                # Try to find price in bdi tag
                price_elems = li_elem.select('bdi')
                
                if len(price_elems) >= 2:
                    # Has discount
                    discount_price_str = price_elems[-1].get_text(strip=True)
                    regular_price_str = price_elems[0].get_text(strip=True)
                elif len(price_elems) == 1:
                    # Regular price only
                    regular_price_str = price_elems[0].get_text(strip=True)
                
                # Clean prices
                regular_price = self.clean_price(regular_price_str) if regular_price_str else None
                discount_price = self.clean_price(discount_price_str) if discount_price_str else None
                
                # Determine final price
                final_price = discount_price if has_discount and discount_price else regular_price
                
                if not final_price:
                    logger.warning(f"No price for: {name[:50]}")
                    continue
                
                # Build product
                product = {
                    "index": idx,
                    "name": name,
                    "regular_price": regular_price,
                    "regular_price_str": regular_price_str or "",
                    "discount_price": discount_price,
                    "discount_price_str": discount_price_str or "",
                    "final_price": final_price,
                    "has_discount": has_discount,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": product_url,
                    "store": "DIM_KAVA",
                }
                
                self.products.append(product)
                
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx} products...")
                
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                continue
        
        logger.info(f"[OK] Parsed {len(self.products)} products")
    
    def save_results(self):
        """Save results to Excel and CSV"""
        if not self.products:
            logger.warning("No products to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent.parent / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to Excel
        excel_file = output_dir / f"dimkava_delonghi_prices_{timestamp}.xlsx"
        save_to_excel(self.products, excel_file, "DIM_KAVA")
        logger.info(f"[OK] Saved to Excel: {excel_file.name}")
        
        # Save to CSV
        csv_file = output_dir / f"dimkava_delonghi_prices_{timestamp}.csv"
        save_to_csv(self.products, csv_file)
        logger.info(f"[OK] Saved to CSV: {csv_file.name}")
    
    def run(self):
        """Main execution"""
        try:
            logger.info("=" * 60)
            logger.info("DIM KAVA Pure BS4 Scraper Started")
            logger.info("=" * 60)
            
            html = self.fetch_page()
            self.parse_products(html)
            self.save_results()
            
            logger.info("=" * 60)
            logger.info(f"[SUCCESS] Scraped {len(self.products)} products")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"[ERROR] Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


def main():
    """Entry point"""
    scraper = DimKavaPureBS4Scraper()
    scraper.run()


if __name__ == "__main__":
    main()

