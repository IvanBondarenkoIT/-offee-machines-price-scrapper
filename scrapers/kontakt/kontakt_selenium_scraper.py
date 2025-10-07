"""
KONTAKT Selenium Scraper for DeLonghi Coffee Machines
Scrapes product names and prices from kontakt.ge
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import KONTAKT_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("kontakt_scraper")


class KontaktScraper:
    """Scraper for KONTAKT website"""
    
    def __init__(self):
        self.url = KONTAKT_CONFIG["url"]
        self.driver = None
        self.products = []
        
    def setup_driver(self):
        """Initialize and configure Chrome WebDriver"""
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
        self.driver.implicitly_wait(SELENIUM_CONFIG["implicit_wait"])
        self.driver.set_page_load_timeout(SELENIUM_CONFIG["page_load_timeout"])
        
        logger.info("WebDriver setup complete")
        
    def load_page(self):
        """Load the KONTAKT page with DeLonghi filter"""
        logger.info(f"Loading page: {self.url}")
        self.driver.get(self.url)
        time.sleep(3)
        logger.info("Page loaded successfully")
        
    def click_load_more(self) -> bool:
        """Click 'Load More' button if it exists"""
        try:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            
            # Button XPath from Excel
            button_xpath = KONTAKT_CONFIG["load_more_button_xpath"]
            
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, button_xpath))
                )
                
                if button.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("Clicked 'Load More' button")
                    time.sleep(2)
                    return True
                else:
                    return False
                    
            except TimeoutException:
                logger.debug("Load More button not found")
                return False
            
        except Exception as e:
            logger.debug(f"Error clicking 'Load More': {e}")
            return False
    
    def load_all_products(self):
        """Click 'Load More' button until all products are loaded"""
        logger.info("Loading all products...")
        
        max_attempts = SELENIUM_CONFIG["max_load_more_attempts"]
        attempts = 0
        
        while attempts < max_attempts:
            product_count = self.count_products()
            logger.info(f"Current product count: {product_count}")
            
            if product_count >= KONTAKT_CONFIG["expected_products"]:
                logger.info(f"All {product_count} products loaded!")
                break
            
            if not self.click_load_more():
                logger.info("'Load More' button not found or not clickable. Stopping.")
                break
            
            attempts += 1
            
            new_count = self.count_products()
            if new_count == product_count:
                logger.info("Product count did not increase. All products likely loaded.")
                break
        
        final_count = self.count_products()
        logger.info(f"Finished loading. Total products: {final_count}")
        
    def count_products(self) -> int:
        """Count currently visible products on the page"""
        try:
            # Use data-product-id attribute to count actual products
            elements = self.driver.find_elements(By.XPATH, "//div[@data-product-id]")
            
            # Filter only DeLonghi products
            delonghi_count = 0
            for elem in elements:
                try:
                    text = elem.text.lower()
                    if 'delonghi' in text:
                        delonghi_count += 1
                except:
                    continue
            
            return delonghi_count
            
        except Exception as e:
            logger.error(f"Error counting products: {e}")
            return 0
    
    def extract_text_safe(self, xpath: str) -> Optional[str]:
        """Safely extract text from element by XPath"""
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except NoSuchElementException:
            return None
        except Exception as e:
            logger.debug(f"Error extracting text from {xpath}: {e}")
            return None
    
    def clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Clean and convert price string to float"""
        if not price_str:
            return None
        
        try:
            # Remove currency symbols, spaces, quotes, and text like "GEL"
            cleaned = re.sub(r'[₾₽$€\s",\']|GEL|gel', '', price_str, flags=re.IGNORECASE)
            return float(cleaned)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert price: {price_str}")
            return None
    
    def scrape_products(self):
        """Scrape all product information"""
        logger.info("Starting product scraping...")
        
        self.products = []
        
        # Find all product elements by data-product-id attribute
        try:
            product_elements = self.driver.find_elements(By.XPATH, "//div[@data-product-id]")
            logger.info(f"Found {len(product_elements)} product elements with data-product-id")
            
            # Filter DeLonghi products
            delonghi_products = []
            for elem in product_elements:
                try:
                    text = elem.text.lower()
                    if 'delonghi' in text:
                        delonghi_products.append(elem)
                except:
                    continue
            
            logger.info(f"Scraping {len(delonghi_products)} DeLonghi products...")
            
        except Exception as e:
            logger.error(f"Error finding product elements: {e}")
            return
        
        # Parse each product element
        for idx, product_elem in enumerate(delonghi_products, 1):
            try:
                if idx % 10 == 0:
                    logger.info(f"Progress: {idx}/{len(delonghi_products)} products...")
                
                # Extract product name - try different tags and attributes
                product_name = None
                
                # Try to find by specific attributes or tags
                for tag in ['h3', 'h4', 'h2', 'a']:
                    try:
                        elem = product_elem.find_element(By.TAG_NAME, tag)
                        text = elem.text.strip()
                        # Validate: should contain 'delonghi' and be reasonable length
                        if text and 'delonghi' in text.lower() and 10 < len(text) < 150:
                            # Make sure it's not generic text like "Shop By" or "Price"
                            if 'shop by' not in text.lower() and 'manufacturer' not in text.lower():
                                product_name = text
                                break
                    except:
                        continue
                
                # Fallback: try to find link/title
                if not product_name:
                    try:
                        link = product_elem.find_element(By.TAG_NAME, 'a')
                        title = link.get_attribute('title') or link.get_attribute('aria-label')
                        if title and 'delonghi' in title.lower():
                            product_name = title
                    except:
                        pass
                
                if not product_name or len(product_name) < 10:
                    logger.warning(f"Could not find valid name for product {idx}")
                    continue
                
                # Extract price - usually in <strong> or <i> tags
                price_str = None
                try:
                    # Try strong/i combination
                    strong_elem = product_elem.find_element(By.TAG_NAME, 'strong')
                    i_elem = strong_elem.find_element(By.TAG_NAME, 'i')
                    price_str = i_elem.text.strip()
                except:
                    try:
                        # Try just strong
                        strong_elem = product_elem.find_element(By.TAG_NAME, 'strong')
                        price_str = strong_elem.text.strip()
                    except:
                        # Try to find any number-like text
                        text_lines = product_elem.text.split('\n')
                        for line in text_lines:
                            if re.search(r'\d{2,}', line):
                                price_str = line
                                break
                
                regular_price = self.clean_price(price_str)
                
                # Try to find discount price (if exists)
                discount_price_str = None
                discount_price = None
                
                # Build product dict
                product = {
                    "index": idx,
                    "name": product_name,
                    "regular_price": regular_price,
                    "regular_price_str": price_str,
                    "discount_price": discount_price,
                    "discount_price_str": discount_price_str,
                    "final_price": discount_price if discount_price else regular_price,
                    "has_discount": discount_price is not None,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "url": self.url,
                    "store": "KONTAKT",
                }
                
                self.products.append(product)
                logger.info(f"[OK] Product {idx}: {product_name[:60]} - {product.get('final_price')} GEL")
                
            except Exception as e:
                logger.error(f"Error scraping product {idx}: {e}")
                continue
        
        logger.info(f"Scraping complete! Total products scraped: {len(self.products)}")
    
    def save_results(self):
        """Save scraped results to Excel and CSV"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        logger.info("Saving results...")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = save_to_excel(self.products, filename=f"kontakt_delonghi_prices_{timestamp}.xlsx")
            logger.info(f"[OK] Saved to Excel: {excel_path}")
            
            csv_path = save_to_csv(self.products, filename=f"kontakt_delonghi_prices_{timestamp}.csv")
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
            logger.info("KONTAKT DeLonghi Scraper Started")
            logger.info("=" * 60)
            
            self.setup_driver()
            self.load_page()
            self.load_all_products()
            self.scrape_products()
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
    scraper = KontaktScraper()
    scraper.run()


if __name__ == "__main__":
    main()

