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
from urllib.parse import unquote
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config import VELI_STORE_CONFIG, SELENIUM_CONFIG
from utils.model_extractor import ModelExtractor

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
    def __init__(self, enable_google_search=False, inventory_models=None, use_direct_urls=True):
        """
        Initialize Veli Store scraper
        Args:
            enable_google_search: If True, search missing products via Google (DEFAULT: False)
            inventory_models: List of model codes from inventory to search for
            use_direct_urls: If True, use direct URLs from config file (DEFAULT: True)
        """
        self.config = VELI_STORE_CONFIG
        self.driver = None
        self.products = []
        self.enable_google_search = enable_google_search
        self.inventory_models = inventory_models or []
        self.use_direct_urls = use_direct_urls
        self.model_extractor = ModelExtractor()
        self.direct_urls = self.load_direct_urls()
    
    def load_direct_urls(self):
        """Load direct URLs from config file"""
        import json
        config_file = project_root / "config" / "veli_direct_urls.json"
        
        if not config_file.exists():
            logger.debug("No direct URLs config file found")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            urls = data.get('products', {})
            logger.info(f"Loaded {len(urls)} direct URLs from config")
            return urls
        except Exception as e:
            logger.warning(f"Failed to load direct URLs: {e}")
            return {}
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        # More realistic user agent (Chrome 120)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        # Additional options to avoid detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
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
        
        logger.info(f"Total products scraped from categories: {len(self.products)}")
        
        # Try to add products from direct URLs if enabled
        if self.use_direct_urls and self.direct_urls:
            direct_products = self.scrape_direct_urls()
            if direct_products:
                self.products.extend(direct_products)
                logger.info(f"Added {len(direct_products)} products via direct URLs")
        
        # Search for missing products via Google if enabled (fallback)
        if self.enable_google_search and self.inventory_models:
            missing_products = self.search_missing_products()
            if missing_products:
                self.products.extend(missing_products)
                logger.info(f"Added {len(missing_products)} products via Google search")
        
        logger.info(f"Total products: {len(self.products)}")
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
    
    def scrape_direct_urls(self):
        """
        Scrape products from direct URLs (for products not in categories)
        Returns: List of products
        """
        if not self.direct_urls:
            return []
        
        logger.info("=" * 60)
        logger.info("SCRAPING PRODUCTS FROM DIRECT URLs")
        logger.info("=" * 60)
        logger.info(f"Found {len(self.direct_urls)} direct URLs in config")
        
        # Check which models we already have
        found_models = set()
        for product in self.products:
            model = self.extract_model_from_name(product['name'])
            if model:
                found_models.add(model.upper())
        
        products = []
        for model_code, info in self.direct_urls.items():
            # Check if already found in category
            if model_code.upper() in found_models:
                logger.info(f"[SKIP] {model_code} - already found in category")
                continue
            
            url = info['url']
            logger.info(f"[{len(products)+1}/{len(self.direct_urls)}] Scraping: {model_code}")
            
            product = self.parse_product_page(url)
            if product:
                products.append(product)
                logger.info(f"  -> {product['name']} - {product['price']} GEL")
            else:
                logger.warning(f"  -> Failed to parse {model_code}")
            
            time.sleep(2)  # Pause between products
        
        logger.info(f"Successfully scraped {len(products)} products from direct URLs")
        return products
    
    def extract_model_from_name(self, name):
        """
        Extract model code from product name using existing ModelExtractor
        Examples:
            "DeLonghi ECAM22.110.SB Magnifica" -> "ECAM22.110.SB"
            "DeLonghi CTJ2103.BK Toaster" -> "CTJ2103.BK"
        """
        model = self.model_extractor.extract_model(name)
        return model if model else None
    
    def search_missing_products(self):
        """
        Search for products that were not found in categories via Google Search
        Returns: List of additional products
        """
        logger.info("=" * 60)
        logger.info("SEARCHING FOR MISSING PRODUCTS VIA GOOGLE")
        logger.info("=" * 60)
        
        # Extract models from already found products
        found_models = set()
        for product in self.products:
            model = self.extract_model_from_name(product['name'])
            if model:
                found_models.add(model)
        
        logger.info(f"Already found models from category: {len(found_models)}")
        if found_models:
            logger.info(f"  Models: {sorted(found_models)}")
        logger.info(f"Inventory models to check: {len(self.inventory_models)}")
        
        # Normalize inventory models (uppercase, remove spaces)
        inventory_models_normalized = {m.upper().replace(' ', '') for m in self.inventory_models}
        
        # Find missing models (EXCLUDE already found from category!)
        missing_models = inventory_models_normalized - found_models
        
        if not missing_models:
            logger.info("✓ No missing products - all inventory items found in categories!")
            logger.info("  Skipping Google search - not needed!")
            return []
        
        logger.info(f"✗ Missing {len(missing_models)} models (NOT found in category):")
        logger.info(f"  {sorted(missing_models)}")
        logger.info(f"  → Will search these via Google...")
        
        # Limit to avoid too many Google searches (can be adjusted)
        max_searches = 20
        if len(missing_models) > max_searches:
            logger.warning(f"Limiting Google search to {max_searches} products (out of {len(missing_models)})")
            missing_models = list(missing_models)[:max_searches]
        
        # Search via Google
        found_products = []
        for i, model in enumerate(sorted(missing_models), 1):
            logger.info(f"[{i}/{len(missing_models)}] Searching via Google: {model}")
            
            try:
                # Search on Google
                url = self.google_search_product(model)
                
                if url:
                    # Parse product page
                    product = self.parse_product_page(url)
                    if product:
                        found_products.append(product)
                        logger.info(f"  -> Found: {product['name']} - {product['price']} GEL")
                    
                    # Pause between products
                    time.sleep(3)
                else:
                    logger.info(f"  -> Not found on Veli Store")
                
                # Pause between Google searches (important to avoid blocking!)
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"  -> Error searching {model}: {e}")
                continue
        
        logger.info(f"Found {len(found_products)} missing products via Google")
        return found_products
    
    def google_search_product(self, model_code):
        """
        Search for a product on Veli Store via DuckDuckGo (more reliable than Google)
        Returns: URL of the product page or None
        """
        # Try multiple search variations
        search_queries = [
            f"site:veli.store {model_code}",
            f"veli.store {model_code}",
            f"veli.store delonghi {model_code}",
        ]
        
        for query in search_queries:
            try:
                # Use DuckDuckGo (no CAPTCHA, simpler structure)
                search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
                logger.debug(f"  Trying: {query}")
                
                self.driver.get(search_url)
                time.sleep(3)  # Wait for DuckDuckGo results
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Method 1: Direct links (DuckDuckGo uses direct links, not redirects!)
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # DuckDuckGo direct links to veli.store
                    if 'veli.store' in href and ('/details/' in href or '/product/' in href):
                        # Clean URL (remove DuckDuckGo tracking params if any)
                        if 'uddg=' in href:
                            href = href.split('uddg=')[1]
                        url = unquote(href)
                        logger.info(f"  Found: {url}")
                        return url
                
                # Method 2: Look in Selenium elements
                try:
                    elements = self.driver.find_elements(By.TAG_NAME, 'a')
                    for elem in elements:
                        try:
                            href = elem.get_attribute('href')
                            if href and 'veli.store' in href and ('/details/' in href or '/product/' in href):
                                logger.info(f"  Found via Selenium: {href}")
                                return href
                        except:
                            continue
                except:
                    pass
                
                # Method 3: Regex search in page text
                page_text = soup.get_text()
                if 'veli.store' in page_text:
                    import re
                    urls = re.findall(r'https?://veli\.store/(?:details|product)/[^\s<>"\']+', page_text)
                    if urls:
                        logger.info(f"  Found via regex: {urls[0]}")
                        return urls[0]
                
            except Exception as e:
                logger.debug(f"Search query '{query}' failed: {e}")
                continue
        
        # Not found with any query
        return None
    
    def parse_product_page(self, url):
        """
        Parse a Veli Store product page (improved for direct URLs)
        Returns: dict with product info
        """
        try:
            logger.debug(f"Parsing: {url}")
            self.driver.get(url)
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract name (h1 tag)
            name_elem = soup.find('h1')
            if not name_elem:
                logger.error("Could not find product name (h1)")
                return None
            
            name = name_elem.get_text(strip=True)
            
            # Clean Georgian text (but keep spaces!)
            georgian_pattern = r'[ა-ჰ]+'  # Only Georgian chars, NOT spaces
            name = re.sub(georgian_pattern, '', name)
            # Normalize spaces (collapse multiple spaces into one)
            name = re.sub(r'\s+', ' ', name).strip()
            
            # Extract prices - improved method
            prices = []
            
            # Method 1: Look for h3 tags with prices (main price display)
            h3_tags = soup.find_all('h3')
            for h3 in h3_tags:
                text = h3.get_text()
                if '₾' in text:
                    # Extract all numbers that look like prices
                    price_matches = re.findall(r'(\d+\.?\d*)\s*₾', text)
                    for match in price_matches:
                        try:
                            price = float(match)
                            if 10 < price < 10000:
                                prices.append(price)
                        except:
                            pass
            
            # Method 2: Look in all elements with ₾ symbol
            if not prices:
                all_text_with_currency = soup.find_all(string=re.compile(r'\d+\.?\d*\s*₾'))
                for text in all_text_with_currency:
                    matches = re.findall(r'(\d+\.?\d*)\s*₾', str(text))
                    for match in matches:
                        try:
                            price = float(match)
                            if 10 < price < 10000:
                                prices.append(price)
                        except:
                            pass
            
            # Remove duplicates and sort
            prices = sorted(list(set(prices)))
            
            if not prices:
                logger.error(f"No prices found on page: {url}")
                # Save HTML for debugging
                with open("debug_veli_page.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                logger.info("Saved HTML to debug_veli_page.html for inspection")
                return None
            
            logger.debug(f"Found prices: {prices}")
            
            # Determine discount (if multiple prices, highest is old, lowest is current)
            if len(prices) >= 2:
                discount_price = min(prices)
                regular_price = max(prices)
                has_discount = True
            else:
                regular_price = prices[0]
                discount_price = None
                has_discount = False
            
            final_price = discount_price if discount_price else regular_price
            
            product = {
                'name': name,
                'price': final_price,
                'regular_price': regular_price,
                'discount_price': discount_price,
                'has_discount': has_discount,
                'url': url,
                'source': 'VELI_STORE'
            }
            
            logger.debug(f"Parsed product: {name} - {final_price} GEL")
            return product
            
        except Exception as e:
            logger.error(f"Error parsing product page {url}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
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
    
    # Print summary for integration with run_full_cycle.py
    if scraper.products:
        # Count products from direct URLs
        direct_count = 0
        if scraper.use_direct_urls and scraper.direct_urls:
            for product in scraper.products:
                for info in scraper.direct_urls.values():
                    # Check if URL matches (ignore query params)
                    direct_url_base = info['url'].split('?')[0]
                    product_url_base = product['url'].split('?')[0]
                    if product_url_base.startswith(direct_url_base):
                        direct_count += 1
                        break
        
        category_count = len(scraper.products) - direct_count
        
        print(f"\n[SUCCESS] {len(scraper.products)} products scraped successfully")
        print(f"  - From category: {category_count}")
        if direct_count > 0:
            print(f"  - From direct URLs: {direct_count}")

if __name__ == "__main__":
    main()
