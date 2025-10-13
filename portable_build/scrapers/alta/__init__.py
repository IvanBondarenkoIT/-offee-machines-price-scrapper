"""
ALTA.ge Scraper Package

Two scraper implementations:
- AltaBS4Scraper: Fast BeautifulSoup-based scraper (recommended)
- AltaScraper: Robust Selenium-based scraper
"""

from .alta_bs4_scraper import AltaBS4Scraper
from .alta_selenium_scraper import AltaScraper

__all__ = ['AltaBS4Scraper', 'AltaScraper']

