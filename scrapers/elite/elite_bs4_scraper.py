"""
ELITE BeautifulSoup Scraper with Pagination
Scrapes DeLonghi products from ee.ge across multiple pages
"""
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import ELITE_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("elite_bs4_scraper")


class EliteBS4Scraper:
    """Fast scraper for ELITE using BeautifulSoup with pagination"""
    
    def __init__(self):
        self.url_base = ELITE_CONFIG["url_base"]
        self.pages = ELITE_CONFIG["pages"]
        self.driver = None
        self.products = []
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if SELENIUM_CONFIG.get("headless", False):
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # Increase timeout for slow sites
        self.driver.set_page_load_timeout(60)  # 60 seconds instead of default
        self.driver.implicitly_wait(10)  # Wait for elements
        
        logger.info("WebDriver setup complete")
        
    def scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape products from a single page with retry logic"""
        # Build URL
        if page_num == 1:
            url = self.url_base
        else:
            url = f"{self.url_base}?page={page_num}"
        
        logger.info(f"Loading page {page_num}: {url}")
        
        # Retry logic for slow sites
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(6)  # Increased wait time for slow sites
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(5)  # Wait before retry
                else:
                    logger.error(f"All {max_retries} attempts failed for page {page_num}")
                    raise
        
        # Get HTML
        html = self.driver.page_source
        logger.info(f"Got HTML ({len(html)} chars)")
        
        # Parse with BS4
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all h3 tags (product names based on debug)
        h3_tags = soup.find_all('h3')
        logger.info(f"Found {len(h3_tags)} h3 tags on page {page_num}")
        
        # Filter DeLonghi products
        page_products = []
        
        for h3 in h3_tags:
            try:
                # Get product name
                name = h3.get_text(strip=True)
                
                # Check if DeLonghi
                if not name or 'delonghi' not in name.lower():
                    continue
                
                # Find parent container to get prices
                parent = h3.parent
                price_container = None
                
                # Go up to find span elements with prices
                for _ in range(10):
                    if parent:
                        spans = parent.find_all('span')
                        if len(spans) >= 1:
                            price_container = parent
                            break
                        parent = parent.parent
                    else:
                        break
                
                if not price_container:
                    logger.warning(f"No price container for: {name[:50]}")
                    continue
                
                # Extract prices from spans
                # Usually: span[1] = discount (if exists), span[2] = regular
                # Or just span = price (no discount)
                spans = price_container.find_all('span')
                
                price_texts = []
                for span in spans:
                    text = span.get_text(strip=True)
                    # Filter price-like text (contains digits and possibly ₾)
                    if re.search(r'\d{3,}', text):
                        price_texts.append(text)
                
                # Determine regular and discount prices
                regular_price_str = None
                discount_price_str = None
                
                if len(price_texts) >= 2:
                    # Has discount: [discount, regular]
                    discount_price_str = price_texts[0]
                    regular_price_str = price_texts[1]
                elif len(price_texts) == 1:
                    # No discount
                    regular_price_str = price_texts[0]
                
                # Clean prices
                regular_price = self.clean_price(regular_price_str)
                discount_price = self.clean_price(discount_price_str)
                
                if regular_price:
                    page_products.append({
                        'name': name,
                        'regular_price': regular_price,
                        'regular_price_str': regular_price_str,
                        'discount_price': discount_price,
                        'discount_price_str': discount_price_str,
                        'page': page_num,
                    })
                
            except Exception as e:
                logger.debug(f"Error parsing product on page {page_num}: {e}")
                continue
        
        logger.info(f"Page {page_num}: Found {len(page_products)} DeLonghi products")
        return page_products
    
    def scrape_all_pages(self):
        """Scrape all pages with pagination"""
        logger.info(f"Scraping {self.pages} pages...")
        
        all_products = []
        
        for page_num in range(1, self.pages + 1):
            products = self.scrape_page(page_num)
            all_products.extend(products)
            logger.info(f"Total so far: {len(all_products)} products")
        
        # Build final product list
        for idx, prod_data in enumerate(all_products, 1):
            product = {
                "index": idx,
                "name": prod_data['name'],
                "regular_price": prod_data['regular_price'],
                "regular_price_str": prod_data['regular_price_str'],
                "discount_price": prod_data['discount_price'],
                "discount_price_str": prod_data['discount_price_str'],
                "final_price": prod_data['discount_price'] if prod_data['discount_price'] else prod_data['regular_price'],
                "has_discount": prod_data['discount_price'] is not None,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"{self.url_base}?page={prod_data['page']}" if prod_data['page'] > 1 else self.url_base,
                "store": "ELITE",
                "page": prod_data['page'],
            }
            
            self.products.append(product)
        
        logger.info(f"Total products scraped: {len(self.products)}")
    
    def clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Clean and convert price string to float"""
        if not price_str:
            return None
        
        try:
            # Remove currency symbols, spaces, quotes, and text like "GEL"
            cleaned = re.sub(r'[₾₽$€\s",\']|GEL|gel', '', price_str, flags=re.IGNORECASE)
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def save_results(self):
        """Save scraped results"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        logger.info("Saving results...")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = save_to_excel(self.products, filename=f"elite_delonghi_prices_{timestamp}.xlsx")
            logger.info(f"[OK] Saved to Excel: {excel_path}")
            
            csv_path = save_to_csv(self.products, filename=f"elite_delonghi_prices_{timestamp}.csv")
            logger.info(f"[OK] Saved to CSV: {csv_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise
    
    def close(self):
        """Close the browser"""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Browser closed")
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("=" * 60)
            logger.info("ELITE DeLonghi BS4 Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            self.scrape_all_pages()
            self.save_results()
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS! Scraped {len(self.products)} products from {self.pages} pages")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            self.close()


def main():
    """Entry point"""
    scraper = EliteBS4Scraper()
    scraper.run()


if __name__ == "__main__":
    main()

