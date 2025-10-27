"""
CoffeePin BeautifulSoup Scraper with Pagination
Scrapes DeLonghi, Melitta, and Nivona products from coffeepin.ge across multiple pages
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

from config import COFFEEPIN_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("coffeepin_bs4_scraper")


class CoffeePinBS4Scraper:
    """Fast scraper for CoffeePin using BeautifulSoup with pagination"""
    
    def __init__(self):
        self.urls = COFFEEPIN_CONFIG["urls"]
        self.pages_per_url = COFFEEPIN_CONFIG["pages_per_url"]
        self.pagination_url = COFFEEPIN_CONFIG["pagination_url"]
        self.driver = None
        self.products = []
    
    def setup_driver(self):
        """Setup Chrome driver with optimized settings"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(5)
            
            logger.info("Chrome driver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def scrape_page(self, page_num: int, base_url: str = None) -> List[Dict]:
        """Scrape products from a single page with retry logic"""
        # Build URL
        if base_url is None:
            base_url = self.urls[0]  # Fallback to first URL
        
        if page_num == 1:
            url = base_url
        else:
            url = f"{base_url}{self.pagination_url.format(page_num=page_num)}"
        
        logger.info(f"Loading page {page_num}: {url}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(5)  # Wait for page to load
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                products = self.parse_with_bs4(soup, url)
                
                logger.info(f"Page {page_num}: Found {len(products)} products")
                return products
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(3)
                else:
                    logger.error(f"All {max_retries} attempts failed for page {page_num}")
                    return []
    
    def parse_with_bs4(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Parse products using BeautifulSoup"""
        products = []
        
        try:
            # Find product containers - using more flexible selectors
            product_containers = soup.find_all('div', class_=re.compile(r'product|item|card'))
            
            if not product_containers:
                # Try alternative selectors based on template
                product_containers = soup.select('div[class*="product"]')
            
            logger.info(f"Found {len(product_containers)} product containers")
            
            for container in product_containers:
                try:
                    # Extract product name
                    name_element = container.find(['h3', 'h2', 'h4'], class_=re.compile(r'title|name|product'))
                    if not name_element:
                        name_element = container.find('a', class_=re.compile(r'title|name|product'))
                    
                    if not name_element:
                        continue
                    
                    name = name_element.get_text(strip=True)
                    
                    # Check if DeLonghi, Melitta, or Nivona
                    if not name or not any(brand in name.lower() for brand in ['delonghi', 'melitta', 'nivona']):
                        continue
                    
                    # Extract price using CoffeePin specific selectors
                    # Look for price container with class t4s-product-price
                    price_container = container.find('div', class_='t4s-product-price')
                    if not price_container:
                        # Fallback: try to find any price element
                        price_container = container.find(['div', 'span'], class_=re.compile(r'price|cost'))
                    
                    if not price_container:
                        # Try to find price in text
                        price_text = container.get_text()
                        price_match = re.search(r'(\d+[.,]\d+)\s*GEL', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', '.'))
                            regular_price = price
                            discount_price = None
                        else:
                            continue
                    else:
                        # Check for discount structure: <del> (regular) and <ins> (discount)
                        del_element = price_container.find('del')
                        ins_element = price_container.find('ins')
                        
                        if del_element and ins_element:
                            # Has discount: regular price in <del>, discount price in <ins>
                            regular_text = del_element.get_text(strip=True)
                            discount_text = ins_element.get_text(strip=True)
                            
                            regular_match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', regular_text)
                            discount_match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', discount_text)
                            
                            if regular_match and discount_match:
                                # Handle both comma and dot as thousand separators
                                regular_str = regular_match.group(1)
                                discount_str = discount_match.group(1)
                                
                                # Convert to float: if last separator is dot, treat as decimal
                                if regular_str.count('.') == 1 and regular_str.count(',') == 0:
                                    regular_price = float(regular_str)
                                elif regular_str.count(',') == 1 and regular_str.count('.') == 0:
                                    regular_price = float(regular_str.replace(',', '.'))
                                elif regular_str.count(',') == 1 and regular_str.count('.') == 1:
                                    # Format like 2,649.00 - comma is thousand separator
                                    regular_price = float(regular_str.replace(',', ''))
                                else:
                                    regular_price = float(regular_str.replace(',', '.'))
                                
                                if discount_str.count('.') == 1 and discount_str.count(',') == 0:
                                    discount_price = float(discount_str)
                                elif discount_str.count(',') == 1 and discount_str.count('.') == 0:
                                    discount_price = float(discount_str.replace(',', '.'))
                                elif discount_str.count(',') == 1 and discount_str.count('.') == 1:
                                    # Format like 2,649.00 - comma is thousand separator
                                    discount_price = float(discount_str.replace(',', ''))
                                else:
                                    discount_price = float(discount_str.replace(',', '.'))
                                
                                price = discount_price  # Use discount price as main price
                            else:
                                continue
                        else:
                            # No discount: single price
                            price_text = price_container.get_text(strip=True)
                            price_match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', price_text)
                            if price_match:
                                price_str = price_match.group(1)
                                
                                # Handle both comma and dot as thousand separators
                                if price_str.count('.') == 1 and price_str.count(',') == 0:
                                    price = float(price_str)
                                elif price_str.count(',') == 1 and price_str.count('.') == 0:
                                    price = float(price_str.replace(',', '.'))
                                elif price_str.count(',') == 1 and price_str.count('.') == 1:
                                    # Format like 2,649.00 - comma is thousand separator
                                    price = float(price_str.replace(',', ''))
                                else:
                                    price = float(price_str.replace(',', '.'))
                                
                                regular_price = price
                                discount_price = None
                            else:
                                continue
                    
                    # Clean product name from price information
                    if '₾' in name or 'GEL' in name:
                        name = re.split(r'[₾GEL]', name)[0].strip()
                    
                    # Clean name for logging
                    clean_name = name.split('₾')[0].strip() if '₾' in name else name
                    
                    # Log price information
                    if discount_price and discount_price != regular_price:
                        logger.info(f"Found product: {clean_name} - {regular_price} -> {discount_price} (discount)")
                    else:
                        logger.info(f"Found product: {clean_name} - {price}")
                    
                    product = {
                        'name': name,
                        'price': price,  # Main price (discount if available, regular otherwise)
                        'regular_price': regular_price,
                        'discount_price': discount_price,
                        'has_discount': discount_price is not None and discount_price != regular_price,
                        'url': url,
                        'source': 'COFFEEPIN'
                    }
                    
                    products.append(product)
                    
                except Exception as e:
                    logger.warning(f"Error parsing product container: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(products)} products from {url}")
            
        except Exception as e:
            logger.error(f"Error parsing page: {e}")
        
        return products
    
    def scrape_all_pages(self):
        """Scrape all pages from all URLs"""
        logger.info(f"Scraping {len(self.urls)} URLs with {self.pages_per_url} pages each...")
        
        for url_index, base_url in enumerate(self.urls, 1):
            logger.info(f"Processing URL {url_index}/{len(self.urls)}: {base_url}")
            
            for page_num in range(1, self.pages_per_url + 1):
                try:
                    products = self.scrape_page(page_num, base_url)
                    self.products.extend(products)
                    logger.info(f"Total so far: {len(self.products)} products")
                    
                    # Small delay between pages
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page_num} of URL {url_index}: {e}")
                    continue
        
        logger.info(f"Total products scraped: {len(self.products)}")
    
    def save_results(self):
        """Save scraped results to Excel and CSV"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to Excel
        excel_path = Path(__file__).parent.parent.parent / 'data' / 'output' / f'coffeepin_prices_{timestamp}.xlsx'
        save_to_excel(self.products, excel_path)
        logger.info(f"[OK] Saved to Excel: {excel_path}")
        
        # Save to CSV
        csv_path = Path(__file__).parent.parent.parent / 'data' / 'output' / f'coffeepin_prices_{timestamp}.csv'
        save_to_csv(self.products, csv_path)
        logger.info(f"[OK] Saved to CSV: {csv_path}")
    
    def run(self):
        """Main execution method"""
        logger.info("Starting CoffeePin scraper...")
        
        try:
            if not self.setup_driver():
                logger.error("Failed to setup driver")
                return False
            
            self.scrape_all_pages()
            self.save_results()
            
            logger.info(f"SUCCESS! Scraped {len(self.products)} products from {len(self.urls)} URLs")
            return True
            
        except Exception as e:
            logger.error(f"Scraper failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Driver closed")


if __name__ == "__main__":
    scraper = CoffeePinBS4Scraper()
    success = scraper.run()
    
    if success:
        print(f"[OK] CoffeePin scraper completed successfully!")
        print(f"[INFO] Scraped {len(scraper.products)} products")
    else:
        print("[ERROR] CoffeePin scraper failed!")
