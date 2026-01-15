# Configuration for Coffee Machines Price Scraper
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "inbox"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ========================================
# STOCK API CONFIGURATION
# ========================================
STOCK_API_CONFIG = {
    # Enable/disable API (reads from .env: USE_STOCK_API)
    "enabled": os.getenv("USE_STOCK_API", "false").lower() == "true",
    
    # API endpoint URL
    "api_url": os.getenv("STOCK_API_URL", ""),
    
    # API tokens (primary and fallback)
    "api_token": os.getenv("STOCK_API_TOKEN", ""),
    "fallback_token": os.getenv("STOCK_API_FALLBACK_TOKEN", ""),
    
    # Timeout and retry settings
    "timeout": int(os.getenv("STOCK_API_TIMEOUT", "30")),
    "retry_attempts": 3,
    "retry_delay": 2,
    
    # Fallback to Excel if API fails
    "fallback_to_excel": os.getenv("STOCK_API_FALLBACK_TO_EXCEL", "true").lower() == "true",
}

# Validate API config if enabled
if STOCK_API_CONFIG["enabled"]:
    if not STOCK_API_CONFIG["api_url"]:
        print("[WARNING] USE_STOCK_API=true but STOCK_API_URL is not set in .env")
        print("          Will fall back to Excel file.")
        STOCK_API_CONFIG["enabled"] = False

# ALTA Configuration
ALTA_CONFIG = {
    "url": "https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s",
    # Additional URL with shop availability filter (shows more products in some shops)
    "url_with_shops": "https://alta.ge/en/coffee/available-shops=city-mall-saburtalo,saburtalo-branch,tbilisi-central,tbilisi-mall,east-point,city-mall-gldani,samgori-mall,rustavi-branch,telavi-branch,gori-branch,kutaisi-branch-2-zhiuli-shartava-str,zugdidi-branch,batumi-branch-chavchavadze-str;-c275s?shops=1,2,3,4,5,6,7,9,10,11,13,14,15",
    "excel_file": INPUT_DIR / "Parsing alta.xlsx",
    "load_more_button_xpath": "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[3]/button",  # Fixed: div[3] not div[4]
    "expected_products": 74,  # For main URL
    "expected_products_with_shops": 55,  # For URL with shop filter
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
    "urls": [
        # Brand category pages
        "https://dimkava.ge/brand/delonghi/",  # Expected: 42 products
        "https://dimkava.ge/brand/melita/",    # Expected: 22 products
        "https://dimkava.ge/brand/nivona/",    # Expected: 10 products
    ],
    "expected_products": 72,  # 42 DeLonghi + 22 Melitta + 10 Nivona - 2 without price = 72
}

# COFFEEHUB Configuration
COFFEEHUB_CONFIG = {
    "urls": [
        "https://coffeehub.ge/product-category/coffee-machines/",  # All coffee machines
    ],
    "pages_per_url": 13,  # Total pages (151 products / 12 per page ≈ 13 pages)
    "expected_products": 50,  # Expected DeLonghi + Melitta (will filter from 151 total)
    "pagination_url": "page/{page_num}/",  # URL pattern: .../page/2/
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

# VELI.STORE Configuration
VELI_STORE_CONFIG = {
    "urls": [
        # Coffee Makers & Pots category (all brands, page_size=40 shows all on one page)
        "https://veli.store/en/category/electronics/kitchen-appliances/for-tea-coffee/coffee-makers-pots/1332/?page_size=40",
    ],
    "pages_per_url": 1,  # Only 1 page needed (page_size=40 shows all products)
    "expected_products": 16,  # 12 from category + 4 from direct URLs (config/veli_direct_urls.json)
    "pagination_url": "?page={page_num}",  # URL pattern for pagination (if needed)
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
    "headless": False,  # Set to False for local testing (WordPress lazy loading detection)
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

