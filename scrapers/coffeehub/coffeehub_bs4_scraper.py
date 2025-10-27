"""
CoffeeHub BeautifulSoup Scraper with Pagination
Scrapes DeLonghi products from coffeehub.ge across multiple pages
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

from config import COFFEEHUB_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("coffeehub_bs4_scraper")


class CoffeeHubBS4Scraper:
    """Fast scraper for CoffeeHub using BeautifulSoup with pagination"""
    
    def __init__(self):
        self.urls = COFFEEHUB_CONFIG["urls"]
        self.pages_per_url = COFFEEHUB_CONFIG["pages_per_url"]
        self.pagination_url = COFFEEHUB_CONFIG["pagination_url"]
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
        
        # Find product containers - looking for product cards
        product_containers = soup.find_all('div', class_=lambda x: x and 'product' in x.lower())
        logger.info(f"Found {len(product_containers)} product containers on page {page_num}")
        
        # Alternative: look for product titles/names
        if not product_containers:
            # Try to find product titles directly
            product_titles = soup.find_all(['h2', 'h3', 'h4'], class_=lambda x: x and 'title' in x.lower())
            logger.info(f"Found {len(product_titles)} product titles on page {page_num}")
        
        # Filter DeLonghi products
        page_products = []
        
        # Look for all potential product elements
        all_products = soup.find_all(['div', 'article'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['product', 'item', 'card']
        ))
        
        logger.info(f"Found {len(all_products)} potential products on page {page_num}")
        
        for product in all_products:
            try:
                # Look for product name/title
                name_element = None
                for tag in ['h2', 'h3', 'h4', 'h5', 'a']:
                    name_element = product.find(tag, class_=lambda x: x and any(
                        keyword in x.lower() for keyword in ['title', 'name', 'product']
                    ))
                    if name_element:
                        break
                
                if not name_element:
                    # Try to find any text that might be a product name
                    name_element = product.find(['h2', 'h3', 'h4', 'h5'])
                
                if not name_element:
                    continue
                
                name = name_element.get_text(strip=True)
                
                # Clean name from price information
                if '₾' in name:
                    name = name.split('₾')[0].strip()
                
                # Check if DeLonghi or Melitta
                if not name or ('delonghi' not in name.lower() and 'melitta' not in name.lower()):
                    continue
                
                # Look for prices
                price_element = None
                price_text = None
                
                # Try different price selectors
                price_selectors = [
                    'span.price',
                    'div.price',
                    '.woocommerce-Price-amount',
                    '.price',
                    '[class*="price"]'
                ]
                
                for selector in price_selectors:
                    price_element = product.select_one(selector)
                    if price_element:
                        price_text = price_element.get_text(strip=True)
                        break
                
                if not price_text:
                    # Look for any text that contains currency symbol
                    price_spans = product.find_all('span', string=re.compile(r'[₾$€£]'))
                    if price_spans:
                        price_text = price_spans[0].get_text(strip=True)
                
                if not price_text:
                    continue
                
                # Extract price numbers
                price_match = re.search(r'([\d,]+\.?\d*)', price_text.replace(',', ''))
                if not price_match:
                    continue
                
                price = float(price_match.group(1))
                
                # Look for discount price
                discount_price = None
                discount_element = product.find(['del', 's'], class_=lambda x: x and 'price' in x.lower())
                if discount_element:
                    discount_text = discount_element.get_text(strip=True)
                    discount_match = re.search(r'([\d,]+\.?\d*)', discount_text.replace(',', ''))
                    if discount_match:
                        discount_price = float(discount_match.group(1))
                
                # Get product URL
                product_url = None
                link_element = product.find('a', href=True)
                if link_element:
                    product_url = link_element['href']
                    if not product_url.startswith('http'):
                        product_url = f"https://coffeehub.ge{product_url}"
                
                product_data = {
                    'name': name,
                    'price': price,
                    'discount_price': discount_price,
                    'url': product_url,
                    'source': 'COFFEEHUB',
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                page_products.append(product_data)
                # Clean name for logging (remove price info)
                clean_name = name.split('₾')[0].strip() if '₾' in name else name
                logger.info(f"Found DeLonghi product: {clean_name} - {price}")
                
            except Exception as e:
                logger.warning(f"Error processing product: {e}")
                continue
        
        logger.info(f"Page {page_num}: Found {len(page_products)} DeLonghi products")
        return page_products
    
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
        """Save results to Excel and CSV"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save to Excel
        excel_path = Path(__file__).parent.parent.parent / 'data' / 'output' / f'coffeehub_prices_{timestamp}.xlsx'
        save_to_excel(self.products, excel_path)
        logger.info(f"[OK] Saved to Excel: {excel_path}")
        
        # Save to CSV
        csv_path = Path(__file__).parent.parent.parent / 'data' / 'output' / f'coffeehub_prices_{timestamp}.csv'
        save_to_csv(self.products, csv_path)
        logger.info(f"[OK] Saved to CSV: {csv_path}")
    
    def run(self):
        """Run the scraper"""
        try:
            logger.info("=" * 60)
            logger.info("CoffeeHub DeLonghi BS4 Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            self.scrape_all_pages()
            self.save_results()
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS! Scraped {len(self.products)} products from {len(self.urls)} URLs")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise
        finally:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
                logger.info("Browser closed")


def main():
    """Main function"""
    scraper = CoffeeHubBS4Scraper()
    scraper.run()


if __name__ == "__main__":
    main()
