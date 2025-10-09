"""
KONTAKT BeautifulSoup Scraper - Fast version
Uses Selenium to load page, then BS4 to parse
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
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import KONTAKT_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("kontakt_bs4_scraper")


class KontaktBS4Scraper:
    """Fast scraper using BeautifulSoup after Selenium page load"""
    
    def __init__(self):
        self.url = KONTAKT_CONFIG["url"]
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
        
    def load_all_products_selenium(self):
        """Use Selenium to load page and click 'Load More'"""
        logger.info(f"Loading page: {self.url}")
        self.driver.get(self.url)
        time.sleep(3)
        logger.info("Page loaded")
        
        logger.info("Loading all products...")
        max_attempts = SELENIUM_CONFIG["max_load_more_attempts"]
        attempts = 0
        
        while attempts < max_attempts:
            # Count products
            try:
                product_elements = self.driver.find_elements(By.XPATH, "//div[@data-product-id]")
                
                delonghi_count = 0
                for elem in product_elements:
                    try:
                        if 'delonghi' in elem.text.lower():
                            delonghi_count += 1
                    except:
                        pass
                
                logger.info(f"Current DeLonghi products: {delonghi_count}")
                
                if delonghi_count >= KONTAKT_CONFIG["expected_products"]:
                    logger.info(f"All {delonghi_count} products loaded!")
                    break
            except:
                pass
            
            # Click Load More
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                
                button_xpath = KONTAKT_CONFIG["load_more_button_xpath"]
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
        
        logger.info("Finished loading all products")
    
    def parse_with_bs4(self, html: str):
        """Parse products using BeautifulSoup"""
        logger.info("Parsing with BeautifulSoup...")
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Find all product titles by class prodItem__title
        product_titles = soup.find_all(class_='prodItem__title')
        logger.info(f"Found {len(product_titles)} product titles")
        
        # Filter and parse DeLonghi products
        delonghi_products = []
        
        for title_elem in product_titles:
            try:
                # Extract name
                name = title_elem.get_text(strip=True)
                
                # Check if it's DeLonghi (case insensitive, also check for "Delonghi")
                if not name:
                    continue
                    
                name_lower = name.lower()
                if 'delonghi' not in name_lower and 'de longhi' not in name_lower:
                    continue
                
                # Find price container with class prodItem__prices
                prod_container = title_elem.parent
                price_container = None
                
                # Go up to find the price container
                for _ in range(10):
                    if prod_container:
                        price_elem = prod_container.find(class_='prodItem__prices')
                        if price_elem:
                            price_container = price_elem
                            break
                        prod_container = prod_container.parent
                    else:
                        break
                
                if not price_container:
                    logger.warning(f"Could not find price container for: {name[:50]}")
                    continue
                
                # Extract prices from strong > i or strong > b
                # IMPORTANT: There can be multiple prices (regular + discount)
                # We need to collect ALL prices and take the LAST one (final price)
                all_prices = []
                
                strong_tags = price_container.find_all('strong')
                for strong in strong_tags:
                    # Try i tag first
                    i_tag = strong.find('i')
                    if i_tag:
                        price_text = i_tag.get_text(strip=True)
                        if re.search(r'\d{2,}', price_text):
                            all_prices.append(price_text)
                    
                    # Try b tag
                    b_tag = strong.find('b')
                    if b_tag:
                        price_text = b_tag.get_text(strip=True)
                        if re.search(r'\d{2,}', price_text):
                            all_prices.append(price_text)
                
                # Determine regular and discount prices
                regular_price = None
                discount_price = None
                
                if len(all_prices) >= 2:
                    # Multiple prices = first is regular, last is discount (final)
                    regular_price = self.clean_price(all_prices[0])
                    discount_price = self.clean_price(all_prices[-1])
                elif len(all_prices) == 1:
                    # Single price = no discount
                    regular_price = self.clean_price(all_prices[0])
                    discount_price = None
                
                if regular_price:
                    delonghi_products.append({
                        'name': name,
                        'regular_price': regular_price,
                        'discount_price': discount_price,
                        'all_prices_found': all_prices,  # For debugging
                    })
                
            except Exception as e:
                logger.debug(f"Error parsing product: {e}")
                continue
        
        logger.info(f"Found {len(delonghi_products)} DeLonghi products")
        
        # Build final product list
        for idx, prod_data in enumerate(delonghi_products, 1):
            regular = prod_data['regular_price']
            discount = prod_data['discount_price']
            has_discount = discount is not None and discount > 0 and discount < regular
            final = discount if has_discount else regular
            
            product = {
                "index": idx,
                "name": prod_data['name'],
                "regular_price": regular,
                "regular_price_str": f"{regular:.2f}",
                "discount_price": discount if has_discount else None,
                "discount_price_str": f"{discount:.2f}" if has_discount else None,
                "final_price": final,
                "has_discount": has_discount,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "url": self.url,
                "store": "KONTAKT",
            }
            
            self.products.append(product)
            
            if idx % 10 == 0:
                logger.info(f"Progress: {idx}/{len(delonghi_products)} products...")
        
        logger.info(f"Parsing complete! Total products: {len(self.products)}")
    
    def clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Clean and convert price string to float"""
        if not price_str:
            return None
        
        try:
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
            excel_path = save_to_excel(self.products, filename=f"kontakt_bs4_prices_{timestamp}.xlsx")
            logger.info(f"[OK] Saved to Excel: {excel_path}")
            
            csv_path = save_to_csv(self.products, filename=f"kontakt_bs4_prices_{timestamp}.csv")
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
            logger.info("KONTAKT DeLonghi BS4 Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            self.load_all_products_selenium()
            
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
    scraper = KontaktBS4Scraper()
    scraper.run()


if __name__ == "__main__":
    main()

