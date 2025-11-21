#!/usr/bin/env python3
"""
VELI.STORE Scraper
Scrapes coffee machine prices from veli.store
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
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config import VELI_STORE_CONFIG, SELENIUM_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('veli_store_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('veli_store_scraper')

class VeliStoreScraper:
    def __init__(self):
        self.config = VELI_STORE_CONFIG
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
        """Parse page content with BeautifulSoup using user-provided structure"""
        products = []
        
        # Find product containers
        # User provided path: /html/body/div[3]/section/div/div[3]/div[4]/div[1]
        # This suggests a grid structure. We'll look for the grid container first.
        # The grid seems to be in a section.
        
        # Strategy: Find all 'a' tags that look like product links, then traverse up to find the container
        # Or find the grid container and iterate children.
        
        # Let's try to find the grid container based on the structure
        # div[3]/section/div/div[3]/div[4] seems to be the grid
        
        # Since class names are likely dynamic (Next.js/React), we rely on structure or attributes.
        # We can look for the 'section' tag and then drill down.
        
        potential_products = []
        
        # Fallback: Find all links that contain product-like hrefs (usually have IDs or specific patterns)
        # But user gave specific XPaths. Let's try to map them to BS4.
        
        # Title link: .../span/a
        # Price: .../div/span[1]
        
        # Let's look for all 'a' tags that might be titles.
        # Usually they are inside a span as per user input.
        
        links = soup.find_all('a', href=True)
        for link in links:
            # Check if it's a product link (heuristic)
            # Veli store product links usually look like /en/product/... or similar
            # But we are in a category, so links might be relative.
            
            # User said: /html/body/div[3]/section/div/div[3]/div[4]/div[1]/div[1]/span/a
            # This implies the 'a' is inside a 'span' which is inside a 'div' etc.
            
            parent_span = link.find_parent('span')
            if not parent_span:
                continue
                
            # Go up to find the product card container
            # span -> div -> div (card?)
            card_div = parent_span.find_parent('div')
            if not card_div:
                continue
            
            # The card_div might be the inner wrapper.
            # User: .../div[1]/div[1]/span/a -> card is div[1] (outer)
            
            # Let's try to extract info relative to this link
            name = link.get_text(strip=True)
            if not name:
                continue
                
            # Filter by brands
            if not any(brand in name.lower() for brand in ['delonghi', 'melitta', 'nivona']):
                continue
                
            url = link['href']
            if not url.startswith('http'):
                url = f"https://veli.store{url}" if url.startswith('/') else f"https://veli.store/{url}"
            
            # Now find price. User says price is in .../div[2]/div[1]/div/span[1]
            # The title was in .../div[1]/div[1]/span/a
            # So they are siblings in the main container?
            # Let's go up to the main container.
            
            # card_div is likely .../div[1] (if we went up from span)
            # We need to go up one more level to find the sibling div[2] which has price?
            # User: 
            # Title: .../div[N]/div[1]/span/a
            # Price: .../div[N]/div[1]/div/span[1] (Wait, user said div[1] for title, div[1] for price?)
            
            # Let's re-read user input carefully:
            # Title: .../div[4]/div[1]/div[1]/span/a
            # Price: .../div[4]/div[1]/div[1]/div/span/text()[1]
            
            # Ah, for the FIRST item (div[1]):
            # Title: div[1]/span/a
            # Price: div[1]/div/span
            
            # It seems Title and Price are close.
            # Let's look for the price relative to the title link.
            
            # Usually price is in a sibling div or nearby.
            # Let's search the whole card_div for text that looks like price.
            
            # We need to be careful not to mix products.
            # Let's assume card_div is the container for ONE product info block.
            # Or maybe we need to go up one level to the real card container.
            
            container = card_div.find_parent('div') # This should be the main product cell
            if not container:
                continue

            # Now search for price inside this container
            # We look for text matching price pattern
            
            price_text_nodes = container.find_all(string=re.compile(r'\d+[.,]\d+'))
            
            regular_price = None
            discount_price = None
            
            prices = []
            for node in price_text_nodes:
                text = node.strip()
                # Clean text
                text = text.replace('₾', '').replace('GEL', '').strip()
                try:
                    val = float(text.replace(',', '.')) # Assuming dot or comma decimal
                    if 10 < val < 10000: # Sanity check
                        prices.append(val)
                except:
                    pass
            
            # Deduplicate and sort
            prices = sorted(list(set(prices)), reverse=True)
            
            if not prices:
                continue
                
            if len(prices) >= 2:
                regular_price = prices[0]
                discount_price = prices[1]
            else:
                regular_price = prices[0]
                discount_price = None
            
            # Set main price
            if discount_price:
                price = discount_price
                has_discount = True
            else:
                price = regular_price
                has_discount = False
            
            # Clean name
            clean_name = name
            georgian_patterns = [
                r'ყავის\s+აპარატი\s*',
                r'[ა-ჰ]+',
            ]
            for pattern in georgian_patterns:
                clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\s+', ' ', clean_name).strip()
            
            product = {
                'name': clean_name,
                'price': price,
                'regular_price': regular_price,
                'discount_price': discount_price,
                'has_discount': has_discount,
                'url': url,
                'source': 'VELI_STORE'
            }
            
            # Avoid duplicates in the list
            if not any(p['url'] == url for p in products):
                products.append(product)
                logger.info(f"Found: {clean_name} - {price}")

        logger.info(f"Successfully parsed {len(products)} products from {base_url}")
        return products
    
    def scrape_all_pages(self):
        """Scrape all pages from all URLs"""
        logger.info(f"Scraping {len(self.config['urls'])} URLs with {self.config['pages_per_url']} pages each...")
        
        for url_idx, base_url in enumerate(self.config['urls'], 1):
            logger.info(f"Processing URL {url_idx}/{len(self.config['urls'])}: {base_url}")
            
            for page_num in range(1, self.config['pages_per_url'] + 1):
                if page_num == 1:
                    url = base_url
                else:
                    url = f"{base_url}{self.config['pagination_url'].format(page_num=page_num)}"
                
                logger.info(f"Loading page {page_num}: {url}")
                
                page_products = self.scrape_page(url)
                logger.info(f"Page {page_num}: Found {len(page_products)} products")
                
                self.products.extend(page_products)
                
                # Wait between pages
                if page_num < self.config['pages_per_url']:
                    time.sleep(2)
        
        logger.info(f"Total products scraped: {len(self.products)}")
        return self.products
    
    def save_to_excel(self, products):
        """Save products to Excel file"""
        if not products:
            logger.warning("No products to save")
            return
        
        output_dir = Path("data/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"veli_store_prices_{timestamp}.xlsx"
        filepath = output_dir / filename
        
        df = pd.DataFrame(products)
        df.to_excel(filepath, index=False)
        logger.info(f"[OK] Saved to Excel: {filepath}")
        
        csv_filename = f"veli_store_prices_{timestamp}.csv"
        csv_filepath = output_dir / csv_filename
        df.to_csv(csv_filepath, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved to CSV: {csv_filepath}")
        
        return filepath
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting VELI.STORE scraper...")
            self.setup_driver()
            products = self.scrape_all_pages()
            
            if products:
                self.save_to_excel(products)
                logger.info(f"SUCCESS! Scraped {len(products)} products")
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
    scraper = VeliStoreScraper()
    scraper.run()

if __name__ == "__main__":
    main()
