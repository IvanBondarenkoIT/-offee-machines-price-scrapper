"""
ALTA BeautifulSoup Scraper - Fast alternative to Selenium
Uses Selenium only to load the page, then BeautifulSoup to parse
"""
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import ALTA_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("alta_bs4_scraper")


class AltaBS4Scraper:
    """Fast scraper using BeautifulSoup after initial Selenium page load"""
    
    def __init__(self):
        self.url = ALTA_CONFIG["url"]
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
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        
        chrome_options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(SELENIUM_CONFIG["page_load_timeout"])
        
        logger.info("WebDriver setup complete")
        
    def load_all_products_selenium(self):
        """Use Selenium to load page and click 'Load More' until all products loaded"""
        logger.info(f"Loading page: {self.url}")
        self.driver.get(self.url)
        time.sleep(3)
        logger.info("Page loaded")
        
        logger.info("Loading all products...")
        max_attempts = SELENIUM_CONFIG["max_load_more_attempts"]
        attempts = 0
        
        while attempts < max_attempts:
            # Count current products
            try:
                product_elements = self.driver.find_elements(
                    By.XPATH, 
                    "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div"
                )
                product_count = len(product_elements)
                logger.info(f"Current product count: {product_count}")
                
                if product_count >= ALTA_CONFIG["expected_products"]:
                    logger.info(f"All {product_count} products loaded!")
                    break
            except:
                product_count = 0
            
            # Try to click 'Load More'
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                
                button_xpath = "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button"
                button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, button_xpath))
                )
                
                if button.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("Clicked 'Load More' button")
                    time.sleep(2)
                else:
                    break
            except TimeoutException:
                logger.info("'Load More' button not found")
                break
            except Exception as e:
                logger.debug(f"Error clicking: {e}")
                break
            
            attempts += 1
        
        final_count = len(self.driver.find_elements(
            By.XPATH, 
            "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div"
        ))
        logger.info(f"Finished loading. Total products: {final_count}")
        
        return final_count
    
    def get_page_html(self) -> str:
        """Get current page HTML"""
        return self.driver.page_source
    
    def parse_with_bs4(self, html: str):
        """Parse products using BeautifulSoup - MUCH faster than Selenium"""
        logger.info("Parsing with BeautifulSoup...")
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Simple approach: Find all h2 tags (product names)
        # Each product has an h2 with the name
        h2_tags = soup.find_all('h2')
        
        logger.info(f"Found {len(h2_tags)} products (h2 tags)")
        
        # For each h2, find its parent container to get prices
        likely_products = []
        for h2 in h2_tags:
            # Go up to find the product container (usually 2-3 levels up)
            parent = h2.parent
            for _ in range(5):  # Try up to 5 levels up
                if parent and parent.find_all('span'):
                    likely_products.append(parent)
                    break
                parent = parent.parent if parent else None
            else:
                # If no parent with spans found, use h2's immediate parent
                likely_products.append(h2.parent)
        
        logger.info(f"Extracted {len(likely_products)} product containers")
        
        # Parse each product
        for idx, product_elem in enumerate(likely_products, 1):
            try:
                # Extract product name (h2 tag)
                h2 = product_elem.find('h2')
                if not h2:
                    continue
                
                product_name = h2.get_text(strip=True)
                
                # Extract prices from spans
                spans = product_elem.find_all('span')
                prices = []
                for span in spans:
                    text = span.get_text(strip=True)
                    # Check if it looks like a price (digits)
                    if text and re.search(r'\d+', text):
                        prices.append(text)
                
                # Determine regular and discount prices
                # Usually: [discount_price, regular_price] if discount exists
                # Or: [regular_price] if no discount
                regular_price_str = None
                discount_price_str = None
                
                if len(prices) >= 2:
                    # Has discount
                    discount_price_str = prices[0]
                    regular_price_str = prices[1]
                elif len(prices) == 1:
                    # No discount
                    regular_price_str = prices[0]
                
                # Clean prices
                regular_price = self.clean_price(regular_price_str)
                discount_price = self.clean_price(discount_price_str)
                
                # Build product dict
                product = {
                    "index": idx,
                    "name": product_name,
                    "regular_price": regular_price,
                    "regular_price_str": regular_price_str,
                    "discount_price": discount_price,
                    "discount_price_str": discount_price_str,
                    "final_price": discount_price if discount_price else regular_price,
                    "has_discount": discount_price is not None,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": self.url,
                }
                
                self.products.append(product)
                
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(likely_products)} products...")
                
            except Exception as e:
                logger.error(f"Error parsing product {idx}: {e}")
                continue
        
        logger.info(f"Parsing complete! Total products: {len(self.products)}")
    
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
        """Save scraped results to Excel and CSV"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        logger.info("Saving results...")
        
        try:
            excel_path = save_to_excel(self.products, filename=f"alta_bs4_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            logger.info(f"[OK] Saved to Excel: {excel_path}")
            
            csv_path = save_to_csv(self.products, filename=f"alta_bs4_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
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
            logger.info("ALTA DeLonghi BS4 Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            
            # Step 1: Load all products with Selenium
            product_count = self.load_all_products_selenium()
            
            # Step 2: Get HTML and parse with BS4 (FAST!)
            html = self.get_page_html()
            logger.info(f"Got HTML page source ({len(html)} chars)")
            
            # Step 3: Parse with BeautifulSoup
            self.parse_with_bs4(html)
            
            # Step 4: Save results
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
    scraper = AltaBS4Scraper()
    scraper.run()


if __name__ == "__main__":
    main()

