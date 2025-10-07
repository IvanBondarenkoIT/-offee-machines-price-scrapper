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
    "url": "https://kontakt.ge/en/samzareulos-teknika/samzareulos-tsvrili-teknika/qavis-aparatebi?kh_mtsarmoebeli=DeLonghi",
    "excel_file": INPUT_DIR / "Parsing kontakt.xlsx",
    "load_more_button_xpath": "/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/button",
    "expected_products": 28,
    "product_container_base": "/html/body/div[1]/main/div[4]/div/div[5]/div/div[2]/div[{index}]",
}

# Selenium Configuration
SELENIUM_CONFIG = {
    "implicit_wait": 3,  # Reduced for faster scraping
    "page_load_timeout": 30,
    "load_more_wait": 1,  # Seconds to wait after clicking "Load More"
    "max_load_more_attempts": 30,  # Increased for 74 products
    "headless": False,  # Set to True to run without browser window
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

