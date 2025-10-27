#!/usr/bin/env python3
"""
VEGA.GE Scraper
Scrapes coffee machine prices from vega.ge
Supports DeLonghi, Melitta, and Nivona brands
"""

import os
import sys
import re
import time
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config import VEGA_GE_CONFIG, SELENIUM_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vega_ge_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('vega_ge_scraper')

class VegaGeScraper:
    def __init__(self):
        self.config = VEGA_GE_CONFIG
        self.driver = None
        self.products = []
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(SELENIUM_CONFIG['implicit_wait'])
            self.driver.set_page_load_timeout(SELENIUM_CONFIG['page_load_timeout'])
            logger.info("Chrome driver setup completed")
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def scrape_page(self, url):
        """Scrape a single page"""
        try:
            logger.info(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return self.parse_with_bs4(soup, url)
            
        except TimeoutException:
            logger.warning(f"Timeout loading page: {url}")
            return []
        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return []
    
    def parse_with_bs4(self, soup, base_url):
        """Parse page content with BeautifulSoup"""
        products = []
        
        # Find product containers based on XPath structure
        containers = soup.find_all('div', recursive=True)
        
        logger.info(f"Found {len(containers)} potential containers")
        
        for container in containers:
            try:
                # Look for product name link
                name_link = container.find('a')
                if not name_link:
                    continue
                    
                name = name_link.get_text(strip=True)
                if not name:
                    continue
                
                # Filter by brands
                if not name or not any(brand in name.lower() for brand in ['delonghi', 'melitta', 'nivona']):
                    continue
                
                # Remove Georgian and common words
                georgian_patterns = [
                    r'coffee\s+machines?\s+automatic\s*',
                    r'[ა-ჰ]+',  # any Georgian characters
                ]
                
                for pattern in georgian_patterns:
                    name = re.sub(pattern, '', name, flags=re.IGNORECASE)
                
                # Clean up extra spaces
                name = re.sub(r'\s+', ' ', name).strip()
                
                # Get product URL
                url = name_link.get('href', '')
                if url and not url.startswith('http'):
                    url = f"https://vega.ge{url}" if url.startswith('/') else f"https://vega.ge/{url}"
                
                # Extract price information
                # Based on XPath structure:
                # span[1]/span[1] = regular price (3,719.00)
                # span[2]/span = discount price (2,599.00 ₾)
                regular_price = None
                discount_price = None
                price = None
                
                # Look for price container - try multiple approaches
                price_container = None
                
                # Method 1: Look for div with price class
                price_container = container.find('div', class_=re.compile(r'price', re.I))
                
                # Method 2: Look for any div containing price spans
                if not price_container:
                    for div in container.find_all('div'):
                        spans = div.find_all('span')
                        if len(spans) >= 2:  # Need at least 2 spans for regular/discount
                            price_container = div
                            break
                
                # Method 3: Look for any element containing price patterns
                if not price_container:
                    for element in container.find_all(['div', 'span', 'p']):
                        text = element.get_text(strip=True)
                        # Look for price patterns with currency symbols
                        if re.search(r'\d{1,4}(?:,\d{3})*(?:\.\d{2})?\s*₾', text):
                            price_container = element
                            break
                
                if price_container:
                    # Collect all prices from the container and its children
                    prices_found = []
                    
                    # Get all text content and extract prices
                    all_text = price_container.get_text(strip=True)
                    
                    # Look for all price patterns in the text
                    price_matches = re.findall(r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)', all_text)
                    
                    for price_str in price_matches:
                        try:
                            parsed_price = float(price_str.replace(',', ''))
                            # Only accept reasonable prices
                            if 10 <= parsed_price <= 10000:
                                prices_found.append(parsed_price)
                        except:
                            continue
                    
                    # Remove duplicates and sort
                    prices_found = sorted(list(set(prices_found)), reverse=True)
                    
                    if len(prices_found) >= 2:
                        # If we have 2+ prices, the larger is regular, smaller is discount
                        regular_price = prices_found[0]
                        discount_price = prices_found[1] if prices_found[1] < regular_price else None
                        
                        # Validate discount makes sense (at least 5% off)
                        if discount_price and regular_price:
                            discount_percent = ((regular_price - discount_price) / regular_price) * 100
                            if discount_percent < 5:  # Less than 5% discount, treat as single price
                                regular_price = discount_price
                                discount_price = None
                    elif len(prices_found) == 1:
                        regular_price = prices_found[0]
                        discount_price = None
                    
                    # Also try to find specific span elements for more precise extraction
                    spans = price_container.find_all('span')
                    if len(spans) >= 2:
                        span_prices = []
                        for span in spans:
                            span_text = span.get_text(strip=True)
                            price_match = re.search(r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)', span_text)
                            if price_match:
                                try:
                                    span_price = float(price_match.group(1).replace(',', ''))
                                    if 10 <= span_price <= 10000:
                                        span_prices.append(span_price)
                                except:
                                    continue
                        
                        # If span prices are different from general prices, use them
                        if len(span_prices) >= 2:
                            span_prices = sorted(list(set(span_prices)), reverse=True)
                            if span_prices[0] != regular_price or (len(span_prices) > 1 and span_prices[1] != discount_price):
                                regular_price = span_prices[0]
                                discount_price = span_prices[1] if len(span_prices) > 1 and span_prices[1] < regular_price else None
                
                # Set main price
                if discount_price and discount_price != regular_price:
                    price = discount_price
                    has_discount = True
                else:
                    price = regular_price
                    has_discount = False
                
                if not price:
                    continue
                
                # Clean name for logging
                clean_name = name.encode('ascii', 'ignore').decode()
                
                # Log price information
                try:
                    if discount_price and discount_price != regular_price:
                        logger.info(f"Found product: {clean_name} - {regular_price} -> {discount_price} (discount)")
                    else:
                        logger.info(f"Found product: {clean_name} - {price}")
                except:
                    if discount_price and discount_price != regular_price:
                        logger.info(f"Found product with discount: {regular_price} -> {discount_price}")
                    else:
                        logger.info(f"Found product: {price}")
                
                product = {
                    'name': name,
                    'price': price,  # Main price (discount if available, regular otherwise)
                    'regular_price': regular_price,
                    'discount_price': discount_price,
                    'has_discount': has_discount,
                    'url': url,
                    'source': 'VEGA_GE'
                }
                
                products.append(product)
                
            except Exception as e:
                logger.warning(f"Error parsing product container: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(products)} products from {base_url}")
        return products
    
    def scrape_all_pages(self):
        """Scrape all pages from all URLs"""
        logger.info(f"Scraping {len(self.config['urls'])} URLs with {self.config['pages_per_url']} pages each...")
        
        # Use set to track unique products
        seen_products = set()
        
        for url_idx, base_url in enumerate(self.config['urls'], 1):
            logger.info(f"Processing URL {url_idx}/{len(self.config['urls'])}: {base_url}")
            
            for page_num in range(1, self.config['pages_per_url'] + 1):
                if page_num == 1:
                    url = base_url
                else:
                    # Fix pagination URL - check if base_url already has query params
                    if '?' in base_url:
                        url = f"{base_url}&page={page_num}"
                    else:
                        url = f"{base_url}{self.config['pagination_url'].format(page_num=page_num)}"
                
                logger.info(f"Loading page {page_num}: {url}")
                
                page_products = self.scrape_page(url)
                logger.info(f"Page {page_num}: Found {len(page_products)} products")
                
                # Deduplicate products
                for product in page_products:
                    product_key = (product['name'], product['price'], product.get('url', ''))
                    if product_key not in seen_products:
                        seen_products.add(product_key)
                        self.products.append(product)
                
                logger.info(f"Total so far: {len(self.products)} unique products")
                
                # Wait between pages
                if page_num < self.config['pages_per_url']:
                    time.sleep(2)
        
        logger.info(f"Total unique products scraped: {len(self.products)}")
        return self.products
    
    def save_to_excel(self, products):
        """Save products to Excel file"""
        if not products:
            logger.warning("No products to save")
            return
        
        # Create output directory
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vega_ge_prices_{timestamp}.xlsx"
        filepath = output_dir / filename
        
        # Create DataFrame
        df = pd.DataFrame(products)
        
        # Save to Excel
        df.to_excel(filepath, index=False)
        logger.info(f"[OK] Saved to Excel: {filepath}")
        
        # Also save to CSV
        csv_filename = f"vega_ge_prices_{timestamp}.csv"
        csv_filepath = output_dir / csv_filename
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved to CSV: {csv_filepath}")
        
        return filepath
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting VEGA.GE scraper...")
            
            # Setup driver
            self.setup_driver()
            
            # Scrape all pages
            products = self.scrape_all_pages()
            
            if products:
                # Save results
                self.save_to_excel(products)
                logger.info(f"SUCCESS! Scraped {len(products)} products from {len(self.config['urls'])} URLs")
            else:
                logger.warning("No products found")
            
        except Exception as e:
            logger.error(f"Scraper failed: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Driver closed")

def main():
    scraper = VegaGeScraper()
    scraper.run()
    print(f"[OK] VEGA.GE scraper completed successfully!")
    print(f"[INFO] Scraped {len(scraper.products)} products")

if __name__ == "__main__":
    main()
