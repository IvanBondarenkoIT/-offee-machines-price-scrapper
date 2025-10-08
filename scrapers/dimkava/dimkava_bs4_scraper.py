"""
DIM KAVA BeautifulSoup Scraper
Scrapes DeLonghi products from dimkava.ge (our own store)
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

from config import DIMKAVA_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("dimkava_bs4_scraper")


class DimKavaBS4Scraper:
    """Scraper for Dim Kava (our own store)"""
    
    def __init__(self):
        self.url = DIMKAVA_CONFIG["url"]
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
        self.driver.set_page_load_timeout(SELENIUM_CONFIG["page_load_timeout"])
        
        logger.info("WebDriver setup complete")
        
    def load_page_and_wait(self):
        """Load page and wait for all products to load"""
        logger.info(f"Loading page: {self.url}")
        self.driver.get(self.url)
        
        # Initial wait
        time.sleep(3)
        
        # Scroll down multiple times to trigger lazy loading
        logger.info("Scrolling to load all products...")
        for i in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            logger.info(f"Scroll {i+1}/3 complete")
        
        # Final wait for dynamic content to load
        wait_time = DIMKAVA_CONFIG["wait_for_load"]
        logger.info(f"Waiting {wait_time} more seconds for all products to finish loading...")
        time.sleep(wait_time)
        
        logger.info("Page loaded and content ready")
        
    def parse_with_bs4(self, html: str):
        """Parse products using BeautifulSoup"""
        logger.info("Parsing with BeautifulSoup...")
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all products by class 'un-product-title'
        product_titles = soup.find_all(class_='un-product-title')
        logger.info(f"Found {len(product_titles)} products with un-product-title class")
        
        # Filter DeLonghi products
        delonghi_items = []
        for title_elem in product_titles:
            text = title_elem.get_text(strip=True)
            if text and 'delonghi' in text.lower():
                # Get parent li element
                parent = title_elem.parent
                for _ in range(10):  # Go up to find li
                    if parent and parent.name == 'li':
                        delonghi_items.append((title_elem, parent))
                        break
                    parent = parent.parent if parent else None
        
        logger.info(f"Found {len(delonghi_items)} DeLonghi product items")
        
        # Parse each product
        for idx, (title_elem, li_elem) in enumerate(delonghi_items, 1):
            try:
                # Extract name from un-product-title class
                name = title_elem.get_text(strip=True)
                
                if not name or len(name) < 5:
                    logger.warning(f"Invalid name for product {idx}")
                    continue
                
                # Extract price from class 'price'
                # XPath mentioned: span[2]/span/bdi, but we'll use class selector
                price_str = None
                
                # Find price element by class
                price_elem = li_elem.find(class_='price')
                if price_elem:
                    # Try to find bdi
                    bdi = price_elem.find('bdi')
                    if bdi:
                        price_str = bdi.get_text(strip=True)
                    else:
                        # Try direct text
                        price_str = price_elem.get_text(strip=True)
                
                # Fallback: try to find any bdi or span with price
                if not price_str:
                    bdi_tags = li_elem.find_all('bdi')
                    for bdi in bdi_tags:
                        text = bdi.get_text(strip=True)
                        if re.search(r'\d{3,}', text):
                            price_str = text
                            break
                
                # Clean price
                final_price = self.clean_price(price_str)
                
                if not final_price:
                    logger.warning(f"No price found for: {name[:50]}")
                    continue
                
                # For Dim Kava, we only have final prices (our store)
                product = {
                    "index": idx,
                    "name": name,
                    "regular_price": final_price,
                    "regular_price_str": price_str,
                    "discount_price": None,
                    "discount_price_str": None,
                    "final_price": final_price,
                    "has_discount": False,  # Our store prices (no competitor discount)
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": self.url,
                    "store": "DIM_KAVA",
                }
                
                self.products.append(product)
                
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(delonghi_items)} products...")
                
            except Exception as e:
                logger.error(f"Error parsing product {idx}: {e}")
                continue
        
        logger.info(f"Parsing complete! Total products: {len(self.products)}")
    
    def clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Clean and convert price string to float"""
        if not price_str:
            return None
        
        try:
            # Remove currency symbols, spaces, quotes, and text
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
            excel_path = save_to_excel(self.products, filename=f"dimkava_delonghi_prices_{timestamp}.xlsx")
            logger.info(f"[OK] Saved to Excel: {excel_path}")
            
            csv_path = save_to_csv(self.products, filename=f"dimkava_delonghi_prices_{timestamp}.csv")
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
            logger.info("DIM KAVA DeLonghi Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            self.load_page_and_wait()
            
            html = self.driver.page_source
            logger.info(f"Got HTML page source ({len(html)} chars)")
            
            self.parse_with_bs4(html)
            self.save_results()
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS! Scraped {len(self.products)} products")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            raise
        finally:
            self.close()


def main():
    """Entry point"""
    scraper = DimKavaBS4Scraper()
    scraper.run()


if __name__ == "__main__":
    main()

