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
        
        # Initial wait for page to start loading
        time.sleep(4)
        
        # Scroll down multiple times to trigger lazy loading
        scroll_pause = DIMKAVA_CONFIG.get("scroll_pause", 3)
        logger.info("Scrolling to load all products...")
        
        for i in range(5):  # Increased scrolls
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Check how many products loaded
            from selenium.webdriver.common.by import By
            try:
                titles = self.driver.find_elements(By.CLASS_NAME, "un-product-title")
                logger.info(f"Scroll {i+1}/5: {len(titles)} products visible")
            except:
                pass
        
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
        
        # Get all items (this is DeLonghi brand page, all should be DeLonghi)
        # Don't filter by text - the page is already filtered
        product_items = []
        for title_elem in product_titles:
            # Get parent li element
            parent = title_elem.parent
            for _ in range(10):  # Go up to find li
                if parent and parent.name == 'li':
                    product_items.append((title_elem, parent))
                    break
                parent = parent.parent if parent else None
        
        logger.info(f"Processing {len(product_items)} product items from brand page")
        
        # Parse each product
        for idx, (title_elem, li_elem) in enumerate(product_items, 1):
            try:
                # Extract name from un-product-title class
                name = title_elem.get_text(strip=True)
                
                if not name or len(name) < 5:
                    logger.warning(f"Invalid name for product {idx}")
                    continue
                
                # Extract price - check for discount structure
                # Regular price: <del><span><bdi>
                # Discount price: <ins><span><bdi>
                regular_price_str = None
                discount_price_str = None
                has_discount = False
                
                # Find price element by class
                price_elem = li_elem.find(class_='price')
                if price_elem:
                    # Check for discount structure (del + ins)
                    del_elem = price_elem.find('del')
                    ins_elem = price_elem.find('ins')
                    
                    if del_elem and ins_elem:
                        # Has discount
                        has_discount = True
                        
                        # Regular price in <del>
                        del_bdi = del_elem.find('bdi')
                        if del_bdi:
                            regular_price_str = del_bdi.get_text(strip=True)
                        
                        # Discount price in <ins>
                        ins_bdi = ins_elem.find('bdi')
                        if ins_bdi:
                            discount_price_str = ins_bdi.get_text(strip=True)
                    else:
                        # No discount, just regular price
                        bdi = price_elem.find('bdi')
                        if bdi:
                            regular_price_str = bdi.get_text(strip=True)
                
                # Fallback: try to find any bdi with price
                if not regular_price_str and not discount_price_str:
                    bdi_tags = li_elem.find_all('bdi')
                    for bdi in bdi_tags:
                        text = bdi.get_text(strip=True)
                        if re.search(r'\d{3,}', text):
                            regular_price_str = text
                            break
                
                # Clean prices
                regular_price = self.clean_price(regular_price_str) if regular_price_str else None
                discount_price = self.clean_price(discount_price_str) if discount_price_str else None
                
                # Determine final price
                final_price = discount_price if has_discount and discount_price else regular_price
                
                if not final_price:
                    logger.warning(f"No price found for: {name[:50]}")
                    continue
                
                # Build product dict
                product = {
                    "index": idx,
                    "name": name,
                    "regular_price": regular_price,
                    "regular_price_str": regular_price_str,
                    "discount_price": discount_price,
                    "discount_price_str": discount_price_str,
                    "final_price": final_price,
                    "has_discount": has_discount,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": self.url,
                    "store": "DIM_KAVA",
                }
                
                self.products.append(product)
                
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(product_items)} products...")
                
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

