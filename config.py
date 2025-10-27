# Configuration for Alta Price Scraper
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "inbox"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ALTA Configuration
ALTA_CONFIG = {
    "url": "https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s",
    "excel_file": INPUT_DIR / "Parsing alta.xlsx",
    "load_more_button_xpath": "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button",
    "expected_products": 74,
    "product_container_base": "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/div[{index}]",
}

# KONTAKT Configuration
KONTAKT_CONFIG = {
    "urls": [
        # Coffee machines
        "https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi",
        # Toasters
        "https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/tosteri?kh_mtsarmoebeli=DeLonghi",
    ],
    "excel_file": INPUT_DIR / "Parsing kontakt.xlsx",
    "load_more_button_xpath": "/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/button",
    "expected_products": 30,  # 28 coffee machines + 2 toasters
    "product_container_base": "/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/div[{index}]",
}

# ELITE Configuration
ELITE_CONFIG = {
    "url_base": "https://ee.ge/en/coffee-machine/brand=delonghi;-c201t",
    "excel_file": INPUT_DIR / "Parsing elit.xlsx",
    "pages": 3,  # Total pages with pagination
    "items_per_page": 16,
    "expected_products": 48,  # 3 pages × 16 items (actually 40)
    "pagination_param": "page",  # URL: ?page=2
}

# DIM KAVA Configuration (our own store)
DIMKAVA_CONFIG = {
    "url": "https://dimkava.ge/brand/delonghi/",
    "expected_products": 42,  # Total items on page (41 with prices)
    "wait_for_load": 8,  # Seconds to wait after scrolling
    "scroll_pause": 3,  # Seconds between scrolls
    "num_scrolls": 5,  # Number of scrolls to trigger lazy loading
}

# COFFEEHUB Configuration
COFFEEHUB_CONFIG = {
    "urls": [
        "https://coffeehub.ge/shop/?s=Delonghi&post_type=product",  # DeLonghi filter
        "https://coffeehub.ge/shop/?s=Melitta&post_type=product",  # Melitta filter
    ],
    "pages_per_url": 2,  # Pages to scrape for each URL
    "expected_products": 50,  # Expected total (DeLonghi + Melitta)
    "pagination_url": "&paged={page_num}",  # URL pattern for pagination
}

# COFFEEPIN Configuration
COFFEEPIN_CONFIG = {
    "urls": [
        "https://coffeepin.ge/en/collections/vendors?q=DeLonghi",  # DeLonghi filter
        "https://coffeepin.ge/en/collections/vendors?q=Melitta",  # Melitta filter
        "https://coffeepin.ge/en/collections/vendors?q=Nivona",   # Nivona filter
    ],
    "pages_per_url": 3,  # Pages to scrape for each URL
    "expected_products": 30,  # Expected total (DeLonghi + Melitta + Nivona)
    "pagination_url": "&page={page_num}",  # URL pattern for pagination
}

# VEGA.GE Configuration
VEGA_GE_CONFIG = {
    "urls": [
        "https://vega.ge/en/kitchen-house/coffee-machines",  # Coffee machines general
        "https://vega.ge/en/kitchen-house/coffee-machines/?ocf=F1S0V35",  # DeLonghi filter
    ],
    "pages_per_url": 5,  # Pages to scrape for each URL
    "expected_products": 50,  # Expected total
    "pagination_url": "?page={page_num}",  # URL pattern for pagination
}

# Selenium Configuration
SELENIUM_CONFIG = {
    "implicit_wait": 3,  # Reduced for faster scraping
    "page_load_timeout": 30,
    "load_more_wait": 1,  # Seconds to wait after clicking "Load More"
    "max_load_more_attempts": 30,  # Increased for 74 products
    "headless": True,  # Set to True to run without browser window (required for Railway)
}

# User agents for rotation (if needed)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Output Configuration
OUTPUT_CONFIG = {
    "excel_filename": "alta_delonghi_prices_{timestamp}.xlsx",
    "csv_filename": "alta_delonghi_prices_{timestamp}.csv",
    "include_timestamp": True,
}

# Logging Configuration
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "filename": LOGS_DIR / "scraper.log",
}

