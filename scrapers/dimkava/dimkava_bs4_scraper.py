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
from utils.model_extractor import extract_model


logger = setup_logger("dimkava_bs4_scraper")


class DimKavaBS4Scraper:
    """Scraper for Dim Kava (our own store) supporting multiple brand URLs"""
    
    def __init__(self):
        self.urls = DIMKAVA_CONFIG.get("urls", []) or [DIMKAVA_CONFIG.get("url")]
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
        
    def load_page_and_wait(self, url: str):
        """Load page and wait for all products to load using dynamic scrolling"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        logger.info(f"Loading page: {url}")
        self.driver.get(url)
        
        # Initial wait for page to start loading (WordPress needs time)
        logger.info("Waiting for initial page load...")
        time.sleep(5)
        
        # WordPress lazy loading strategy - scroll slowly and wait longer
        scroll_pause = 3  # 3 seconds between scrolls for WordPress
        max_scrolls = 25  # More scrolls for long pages
        stable_threshold = 4  # Wait for 4 stable counts (WordPress is slow)
        
        logger.info(f"Scrolling to load all products (WordPress lazy loading)...")
        logger.info(f"  Scroll pause: {scroll_pause}s, Max scrolls: {max_scrolls}, Stability: {stable_threshold}")
        
        previous_count = 0
        stable_count = 0
        no_change_scrolls = 0
        
        for i in range(max_scrolls):
            # Scroll to bottom smoothly (better for WordPress)
            current_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.execute_script(f"window.scrollTo(0, {current_height});")
            
            # Wait for WordPress to load content
            logger.info(f"Scroll {i+1}/{max_scrolls}: Waiting {scroll_pause}s for content to load...")
            time.sleep(scroll_pause)
            
            # Check how many products loaded
            try:
                titles = self.driver.find_elements(By.CLASS_NAME, "un-product-title")
                current_count = len(titles)
                
                if current_count > previous_count:
                    logger.info(f"  [+] Products loaded: {previous_count} -> {current_count} (+{current_count - previous_count})")
                    stable_count = 0  # Reset stability counter
                    no_change_scrolls = 0
                    previous_count = current_count
                elif current_count == previous_count:
                    stable_count += 1
                    no_change_scrolls += 1
                    logger.info(f"  [=] No new products: {current_count} (stable: {stable_count}/{stable_threshold})")
                    
                    # If no change for multiple scrolls, we might be at the end
                    if stable_count >= stable_threshold:
                        logger.info(f"  [OK] Product count stabilized at {current_count}. Stopping scrolls.")
                        break
                    
                    # If really no change, try waiting a bit longer
                    if no_change_scrolls >= 2:
                        logger.info(f"  [WAIT] No change detected, waiting extra 2 seconds...")
                        time.sleep(2)
                else:
                    # Count decreased? Shouldn't happen, but reset
                    logger.warning(f"  [!] Product count decreased: {previous_count} -> {current_count}")
                    previous_count = current_count
                    stable_count = 0
                    
            except Exception as e:
                logger.warning(f"  ⚠ Error checking products: {e}")
                pass
        
        # Final wait for any remaining dynamic content to load
        logger.info(f"Final wait: 5 seconds for WordPress to finish loading...")
        time.sleep(5)
        
        # Try to trigger any pending lazy load
        logger.info("Triggering final lazy load...")
        self.driver.execute_script("""
            // Scroll to top and back to bottom to trigger any missed lazy loads
            window.scrollTo(0, 0);
            setTimeout(function() {
                window.scrollTo(0, document.body.scrollHeight);
            }, 1000);
        """)
        time.sleep(3)
        
        # Get final count using multiple selectors
        final_count = 0
        try:
            # Primary selector
            final_titles = self.driver.find_elements(By.CLASS_NAME, "un-product-title")
            final_count = len(final_titles)
            logger.info(f"Final product count (un-product-title): {final_count}")
            
            # Alternative selectors to check
            alt_selectors = [
                (By.CSS_SELECTOR, "li.product"),
                (By.CSS_SELECTOR, ".product-item"),
                (By.CSS_SELECTOR, "[class*='product']"),
                (By.CSS_SELECTOR, "ul.products li"),
            ]
            for selector_type, selector_value in alt_selectors:
                try:
                    alt_elements = self.driver.find_elements(selector_type, selector_value)
                    if len(alt_elements) > final_count:
                        logger.info(f"  Alternative selector {selector_value} found {len(alt_elements)} elements")
                except:
                    pass
            
            # Also check HTML source directly - this is critical for WordPress lazy loading
            html_source = self.driver.page_source
            html_count = html_source.count('un-product-title')
            logger.info(f"  HTML source contains 'un-product-title' {html_count} times")
            
            # Check for different variations in HTML
            variations = [
                'un-product-title',
                'product-title',
                'product_item',
                'woocommerce-loop-product__title',
            ]
            for variant in variations:
                variant_count = html_source.count(variant)
                if variant_count > 0:
                    logger.info(f"  HTML contains '{variant}': {variant_count} times")
            
            if html_count > final_count:
                logger.warning(f"  WARNING: HTML has {html_count} occurrences but only {final_count} elements found!")
                logger.warning(f"  This suggests WordPress lazy loading hasn't finished.")
                logger.warning(f"  Trying aggressive re-render strategy...")
                
                # Aggressive strategy for WordPress lazy loading
                self.driver.execute_script("""
                    // Scroll to top first
                    window.scrollTo(0, 0);
                """)
                time.sleep(2)
                
                # Scroll down in smaller increments
                logger.info("  Performing incremental scroll to trigger lazy load...")
                scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_step = scroll_height // 10  # Divide into 10 steps
                
                for step in range(10):
                    scroll_position = scroll_step * (step + 1)
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                    time.sleep(1)  # Short pause at each step
                
                # Final scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Trigger jQuery events if available
                self.driver.execute_script("""
                    if (window.jQuery) {
                        jQuery(window).trigger('scroll');
                        jQuery(window).trigger('resize');
                    }
                """)
                time.sleep(3)
                
                # Re-check after aggressive render
                try:
                    final_titles_rerender = self.driver.find_elements(By.CLASS_NAME, "un-product-title")
                    final_count_rerender = len(final_titles_rerender)
                    if final_count_rerender > final_count:
                        logger.info(f"  [OK] After aggressive re-render: {final_count_rerender} elements found! (+{final_count_rerender - final_count})")
                        final_count = final_count_rerender
                    else:
                        logger.info(f"  Still {final_count_rerender} elements. Using HTML source for parsing.")
                except Exception as e:
                    logger.warning(f"  Error in re-render check: {e}")
        except Exception as e:
            logger.warning(f"Could not get final product count: {e}")
        
        logger.info("Page loaded and content ready")
        
    def parse_with_bs4(self, html: str):
        """Parse products using BeautifulSoup - parse directly from HTML source"""
        logger.info("Parsing with BeautifulSoup (from HTML source, not DOM)...")
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all products by class 'un-product-title' - this will find ALL in HTML, even if not rendered
        product_titles = soup.find_all(class_='un-product-title')
        logger.info(f"Found {len(product_titles)} products with un-product-title class in HTML source")
        
        # Also try alternative selectors if primary doesn't find enough
        if len(product_titles) < 10:  # If we found very few, try alternatives
            logger.info("Trying alternative selectors...")
            alt_selectors = [
                soup.find_all('li', class_=lambda x: x and 'product' in ' '.join(x) if x else False),
                soup.find_all('div', class_=lambda x: x and 'product' in ' '.join(x) if x else False),
            ]
            for alt_products in alt_selectors:
                if len(alt_products) > len(product_titles):
                    logger.info(f"Alternative selector found {len(alt_products)} products")
                    # Use the alternative if it found more
                    if len(alt_products) > len(product_titles) * 1.5:
                        product_titles = alt_products
                        logger.info(f"Switching to alternative selector with {len(product_titles)} products")
        
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
                name = self._normalize_name(name)
                
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
                
                # Extract brand and model from name
                brand = None
                model = self._extract_model_enhanced(name)
                
                # Try to extract brand from name
                name_upper = name.upper()
                if 'DELONGHI' in name_upper or 'DE LONGHI' in name_upper or "DE'LONGHI" in name_upper:
                    brand = 'DeLonghi'
                elif 'MELITTA' in name_upper or 'MELITA' in name_upper:
                    brand = 'Melitta'
                elif 'NIVONA' in name_upper:
                    brand = 'Nivona'
                elif 'JURA' in name_upper:
                    brand = 'Jura'
                elif 'SAECO' in name_upper:
                    brand = 'Saeco'
                elif 'GAGGIA' in name_upper:
                    brand = 'Gaggia'
                
                # If no brand found, try to infer from model or product codes
                if not brand and model:
                    # DeLonghi models often start with EC, ECAM, ESAM, BCO, etc.
                    if any(model.upper().startswith(prefix) for prefix in ['EC', 'ECAM', 'ESAM', 'BCO', 'ETAM', 'DLSC', 'KG', 'KB', 'CT', 'ICM']):
                        brand = 'DeLonghi'
                    # Melitta models often start with F or contain specific patterns
                    elif model.upper().startswith('F') or 'BARISTA' in name_upper:
                        brand = 'Melitta'
                    # Nivona models start with NI
                    elif model.upper().startswith('NI'):
                        brand = 'Nivona'
                
                # Validate product before adding
                if not self._is_valid_product(name, final_price, brand, model):
                    continue
                
                # Build product dict
                product = {
                    "index": idx,
                    "name": name,
                    "brand": brand,
                    "model": model,
                    "regular_price": regular_price,
                    "regular_price_str": regular_price_str,
                    "discount_price": discount_price,
                    "discount_price_str": discount_price_str,
                    "final_price": final_price,
                    "has_discount": has_discount,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": "",
                    "store": "DIM_KAVA",
                }
                
                self.products.append(product)
                logger.debug(f"ADDED: {name[:50]} | Brand: {brand} | Model: {model} | Price: {final_price}")
                
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
    
    def _normalize_name(self, name: str) -> str:
        """Normalize product name: remove marketing/Georgian tails, collapse spaces"""
        if not name:
            return name
        # Collapse spaces
        name = re.sub(r"\s+", " ", name)
        # Remove common Georgian blocks and marketing tails
        patterns = [
            r"\(ქართული\).*$",
            r"When buying from us,.*$",
            r"Add to Wishlist$",
        ]
        for p in patterns:
            name = re.sub(p, "", name, flags=re.IGNORECASE).strip()
        return name.strip()
    
    def _is_accessory(self, name: str, price: float = 0) -> bool:
        """
        Check if product is an accessory (not a coffee machine)
        
        Args:
            name: Product name
            price: Product price (helps distinguish - coffee machines are expensive)
            
        Returns:
            True if accessory
        """
        name_upper = name.upper()
        
        # If price is very high (>1000), it's likely a coffee machine, not accessory
        if price > 1000:
            return False
        
        # Accessory keywords
        accessory_keywords = [
            'PITCHER', 'ПИТЧЕР',
            'TAMPER', 'ТЕМПЕР',
            'FILTER', 'ФИЛЬТР',
            'DESCAL', 'ДЕКАЛЬЦ',
            'CLEAN', 'ОЧИСТ',
            'TABLET', 'ТАБЛЕТК',
            'LIQUID', 'ЖИДКОСТ',
            'BRUSH', 'ЩЕТК',
            'CLOTH', 'САЛФЕТК',
            'MAT', 'КОВРИК',
            'SPOON', 'ЛОЖК',
            'CUP', 'ЧАШК',
            'GLASS', 'СТАКАН',
            'MUG', 'КРУЖК',
            'CARTRIDGE', 'КАРТРИДЖ',
            'FILTERBAG', 'ФИЛЬТР-ПАКЕТ',
        ]
        
        for keyword in accessory_keywords:
            if keyword in name_upper:
                return True
        
        return False
    
    def _is_spare_part(self, name: str) -> bool:
        """
        Check if product is a spare part
        
        Args:
            name: Product name
            
        Returns:
            True if spare part
        """
        name_upper = name.upper()
        
        # Spare part keywords
        spare_keywords = [
            'ASSY', 'PCB', 'TUBE', 'FUNNEL', 'SUPPORT',
            'DRAINING', 'CARAF', 'TANK', 'PIPE', 'CONNECTOR',
            'VALVE', 'GASKET', 'SEAL', 'SPRING', 'SCREW',
            'NUT', 'BOLT', 'WASHER', 'O-RING', 'BEARING',
            'MOTOR', 'PUMP', 'SENSOR', 'SWITCH', 'CABLE',
            'WIRE', 'BOARD', 'DISPLAY', 'BUTTON', 'KNOB',
        ]
        
        for keyword in spare_keywords:
            if keyword in name_upper:
                return True
        
        return False
    
    def _is_valid_product(self, name: str, price: float, brand: Optional[str], model: Optional[str]) -> bool:
        """
        Validate if product should be included in results
        
        Criteria:
        - Must have a price > 50 GEL (coffee machines are expensive)
        - Must not be an accessory
        - Must not be a spare part
        - Must have a brand
        - Name should be reasonable length
        
        Args:
            name: Product name
            price: Product price
            brand: Extracted brand
            model: Extracted model
            
        Returns:
            True if valid product
        """
        # Must have price
        if not price or price < 50:
            logger.debug(f"SKIP: Price too low ({price}): {name[:50]}")
            return False
        
        # Must not be accessory
        if self._is_accessory(name, price):
            logger.debug(f"SKIP: Accessory: {name[:50]}")
            return False
        
        # Must not be spare part
        if self._is_spare_part(name):
            logger.debug(f"SKIP: Spare part: {name[:50]}")
            return False
        
        # Must have brand
        if not brand:
            logger.debug(f"SKIP: No brand: {name[:50]}")
            return False
        
        # Name should be reasonable length
        if len(name) < 10:
            logger.debug(f"SKIP: Name too short: {name}")
            return False
        
        return True
    
    def _extract_model_enhanced(self, name: str) -> Optional[str]:
        """
        Enhanced model extraction with multiple attempts
        
        Args:
            name: Product name
            
        Returns:
            Extracted model or None
        """
        # Attempt 1: Standard extractor
        model = extract_model(name)
        if model:
            return model
        
        # Attempt 2: Look for model in parentheses
        match = re.search(r'\(([A-Z0-9\s\.]+)\)', name)
        if match:
            potential_model = match.group(1).strip()
            # Clean up spaces
            potential_model = re.sub(r'\s+', '', potential_model)
            if len(potential_model) >= 5:
                return potential_model
        
        # Attempt 3: Look after brand name
        name_upper = name.upper()
        brands = ['DELONGHI', 'DE LONGHI', 'MELITTA', 'NIVONA', 'JURA', 'SAECO', 'GAGGIA']
        
        for brand in brands:
            if brand in name_upper:
                # Split by brand and take what comes after
                parts = name_upper.split(brand)
                if len(parts) > 1:
                    after_brand = parts[1].strip()
                    # Extract first word/code that looks like a model
                    match = re.search(r'^([A-Z0-9\s\.]+?)(?:\s|$)', after_brand)
                    if match:
                        potential_model = match.group(1).strip()
                        potential_model = re.sub(r'\s+', '', potential_model)
                        if len(potential_model) >= 4:
                            return potential_model
        
        return None

    def run(self):
        """Main execution method"""
        try:
            logger.info("=" * 60)
            logger.info("DIM KAVA Multi-Brand Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            products_before_url = 0
            
            for idx, url in enumerate(self.urls, 1):
                logger.info("")
                logger.info(f"{'='*60}")
                logger.info(f"Processing URL {idx}/{len(self.urls)}: {url}")
                logger.info(f"{'='*60}")
                
                products_before_url = len(self.products)
                self.load_page_and_wait(url)
                
                # Get HTML source AFTER all scrolling and waiting
                logger.info("Getting final HTML page source...")
                html = self.driver.page_source
                logger.info(f"Got HTML page source ({len(html):,} chars)")
                
                # Count products in HTML
                html_title_count = html.count('un-product-title')
                logger.info(f"HTML contains 'un-product-title' {html_title_count} times")
                
                # Parse the HTML
                self.parse_with_bs4(html)
                
                products_from_url = len(self.products) - products_before_url
                logger.info(f"[OK] Collected {products_from_url} products from this URL")
                logger.info(f"  Total products so far: {len(self.products)}")
            
            logger.info("")
            logger.info("=" * 60)
            logger.info("Saving results...")
            logger.info("=" * 60)
            self.save_results()
            
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"SUCCESS! Scraped {len(self.products)} total products from {len(self.urls)} URLs")
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

