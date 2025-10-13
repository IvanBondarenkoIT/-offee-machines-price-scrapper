"""
ALTA Selenium Scraper for DeLonghi Coffee Machines
Scrapes product names and prices from alta.ge
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
sys.path.append(str(Path(__file__).parent.parent))

from config import ALTA_CONFIG, SELENIUM_CONFIG
from utils.logger import setup_logger
from utils.excel_writer import save_to_excel, save_to_csv


logger = setup_logger("alta_scraper")


class AltaScraper:
    """Scraper for ALTA website"""
    
    def __init__(self):
        self.url = ALTA_CONFIG["url"]
        self.driver = None
        self.products = []
        
    def setup_driver(self):
        """Initialize and configure Chrome WebDriver"""
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        # Add options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Headless mode (optional)
        if SELENIUM_CONFIG.get("headless", False):
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Window size
        chrome_options.add_argument("--start-maximized")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        self.driver.implicitly_wait(SELENIUM_CONFIG["implicit_wait"])
        self.driver.set_page_load_timeout(SELENIUM_CONFIG["page_load_timeout"])
        
        logger.info("WebDriver setup complete")
        
    def load_page(self):
        """Load the ALTA page with DeLonghi filter"""
        logger.info(f"Loading page: {self.url}")
        self.driver.get(self.url)
        time.sleep(3)  # Wait for page to fully load
        logger.info("Page loaded successfully")
        
    def click_load_more(self) -> bool:
        """
        Click 'Load More' button if it exists
        
        Returns:
            True if button was clicked, False if not found or not clickable
        """
        try:
            # Прокручиваем вниз страницы, чтобы кнопка загрузилась
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            
            # Try to find the button using the exact XPath
            button_xpath = "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button"
            
            try:
                # Ждем появления кнопки
                button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, button_xpath))
                )
                
                # Проверяем, видима ли кнопка
                if button.is_displayed():
                    # Прокручиваем к кнопке
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    
                    # Пробуем кликнуть через JavaScript (надежнее)
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("Clicked 'Load More' button")
                    time.sleep(2)  # Ждем загрузки новых товаров
                    return True
                else:
                    logger.debug("Button found but not visible")
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
            
            # Check if we've reached the expected count
            if product_count >= ALTA_CONFIG["expected_products"]:
                logger.info(f"All {product_count} products loaded!")
                break
            
            # Try to click 'Load More'
            if not self.click_load_more():
                logger.info("'Load More' button not found or not clickable. Stopping.")
                break
            
            attempts += 1
            
            # Check if product count changed
            new_count = self.count_products()
            if new_count == product_count:
                logger.info("Product count did not increase. All products likely loaded.")
                break
        
        final_count = self.count_products()
        logger.info(f"Finished loading. Total products: {final_count}")
        
    def count_products(self) -> int:
        """
        Count currently visible products on the page
        
        Returns:
            Number of products found
        """
        try:
            # Main selector for product containers
            selector = "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div"
            elements = self.driver.find_elements(By.XPATH, selector)
            return len(elements)
            
        except Exception as e:
            logger.error(f"Error counting products: {e}")
            return 0
    
    def extract_text_safe(self, xpath: str) -> Optional[str]:
        """
        Safely extract text from element by XPath
        
        Args:
            xpath: XPath to the element
            
        Returns:
            Text content or None if not found
        """
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except NoSuchElementException:
            return None
        except Exception as e:
            logger.debug(f"Error extracting text from {xpath}: {e}")
            return None
    
    def clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """
        Clean and convert price string to float
        
        Args:
            price_str: Price string (e.g., "1499", "₾1,499", "1499.99", "799 GEL")
            
        Returns:
            Float price or None if invalid
        """
        if not price_str:
            return None
        
        try:
            # Remove currency symbols, spaces, quotes, and text like "GEL"
            cleaned = re.sub(r'[₾₽$€\s",\']|GEL|gel', '', price_str, flags=re.IGNORECASE)
            # Convert to float
            return float(cleaned)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert price: {price_str}")
            return None
    
    def scrape_products(self):
        """Scrape all product information"""
        logger.info("Starting product scraping...")
        
        self.products = []
        product_count = self.count_products()
        
        logger.info(f"Scraping {product_count} products...")
        
        for i in range(1, product_count + 1):
            try:
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{product_count} products...")
                
                # Build XPaths for this product - используем fullXPath
                # Pattern variations based on the Excel file
                name_xpaths = [
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[3]/a/h2",
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[2]/a/h2",
                ]
                
                price_xpaths = [
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[3]/div[1]/span[2]",
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[2]/div[1]/span[2]",
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[3]/div[1]/span",
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[2]/div[1]/span",
                ]
                
                discount_price_xpaths = [
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[3]/div[1]/span[1]",
                    f"/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{i}]/div/div[2]/div[1]/span[1]",
                ]
                
                # Extract product name
                product_name = None
                for xpath in name_xpaths:
                    product_name = self.extract_text_safe(xpath)
                    if product_name:
                        break
                
                if not product_name:
                    logger.warning(f"Could not find name for product {i}")
                    continue
                
                # Extract regular price
                regular_price_str = None
                for xpath in price_xpaths:
                    regular_price_str = self.extract_text_safe(xpath)
                    if regular_price_str:
                        break
                
                regular_price = self.clean_price(regular_price_str)
                
                # Extract discount price (if exists)
                discount_price_str = None
                for xpath in discount_price_xpaths:
                    discount_price_str = self.extract_text_safe(xpath)
                    if discount_price_str:
                        break
                
                discount_price = self.clean_price(discount_price_str)
                
                # Build product dict
                product = {
                    "index": i,
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
                logger.info(f"[OK] Product {i}: {product_name} - {product.get('final_price')} GEL")
                
            except Exception as e:
                logger.error(f"Error scraping product {i}: {e}")
                continue
        
        logger.info(f"Scraping complete! Total products scraped: {len(self.products)}")
    
    def save_results(self):
        """Save scraped results to Excel and CSV"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        logger.info("Saving results...")
        
        try:
            # Save to Excel
            excel_path = save_to_excel(self.products)
            logger.info(f"✓ Saved to Excel: {excel_path}")
            
            # Save to CSV
            csv_path = save_to_csv(self.products)
            logger.info(f"✓ Saved to CSV: {csv_path}")
            
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
            logger.info("ALTA DeLonghi Scraper Started")
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
    scraper = AltaScraper()
    scraper.run()


if __name__ == "__main__":
    main()

