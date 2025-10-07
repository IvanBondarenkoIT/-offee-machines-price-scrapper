"""Debug HTML structure to understand product layout"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Setup
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load page
url = "https://alta.ge/en/small-domestic-appliances/brand=delonghi;-c7s"
driver.get(url)
time.sleep(3)

# Click Load More once
try:
    button = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div/div[2]/div[2]/div[4]/button")
    button.click()
    time.sleep(2)
except:
    pass

# Get HTML
html = driver.page_source

# Parse with BS4
soup = BeautifulSoup(html, 'lxml')

# Save to file for inspection
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("Saved to debug_page.html")

# Try to find products by different methods
print("\n=== Method 1: Find h2 tags ===")
h2_tags = soup.find_all('h2')
print(f"Found {len(h2_tags)} h2 tags")
for i, h2 in enumerate(h2_tags[:5], 1):
    print(f"{i}. {h2.get_text(strip=True)[:60]}")

print("\n=== Method 2: Find by class patterns ===")
# Common patterns: product, card, item
for pattern in ['product', 'card', 'item']:
    divs = soup.find_all('div', class_=lambda x: x and pattern in x.lower() if x else False)
    print(f"Divs with '{pattern}' in class: {len(divs)}")

print("\n=== Method 3: Find price spans ===")
# Prices usually in spans
spans_with_numbers = [s for s in soup.find_all('span') if s.get_text(strip=True).isdigit()]
print(f"Spans with pure numbers: {len(spans_with_numbers)}")

driver.quit()
print("\nCheck debug_page.html to see the structure")

