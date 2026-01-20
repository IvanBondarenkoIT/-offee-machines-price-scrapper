# WooCommerce API: Fetching Product Stock (Leftovers) with Names and Descriptions

## Overview
This prompt provides a complete guide for fetching product stock quantities (leftovers), names, and descriptions from a WordPress WooCommerce store using the WooCommerce REST API.

## Prerequisites

### 1. WooCommerce API Credentials
You need to obtain API credentials from your WordPress WooCommerce store:
- Go to: **WordPress Admin → WooCommerce → Settings → Advanced → REST API**
- Click **Add Key**
- Set permissions to **Read** (or Read/Write if you need to update)
- Copy the **Consumer Key** (starts with `ck_`) and **Consumer Secret` (starts with `cs_`)

### 2. Required Python Package
```bash
pip install woocommerce python-dotenv
```

## Configuration

### Environment Variables (.env file)
Create a `.env` file in your project root:
```
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_your_consumer_key_here
WC_CONSUMER_SECRET=cs_your_consumer_secret_here
WC_API_VERSION=wc/v3
WC_TIMEOUT=30
```

**Important Notes:**
- `WC_URL` should be your store URL without trailing slash
- `WC_API_VERSION` is typically `wc/v3` (not just `v3`)
- Consumer Key should start with `ck_`
- Consumer Secret should start with `cs_`

## Implementation

### Basic Connection Setup

```python
import os
from woocommerce import API
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize WooCommerce API client
wcapi = API(
    url=os.getenv('WC_URL'),
    consumer_key=os.getenv('WC_CONSUMER_KEY'),
    consumer_secret=os.getenv('WC_CONSUMER_SECRET'),
    version=os.getenv('WC_API_VERSION', 'wc/v3'),
    timeout=int(os.getenv('WC_TIMEOUT', 30)),
    query_string_auth=True
)
```

### Fetching Products with Stock Information

#### Method 1: Fetch All Products with Pagination

```python
def get_all_products_with_stock():
    """
    Fetch all products from WooCommerce store with stock quantities.
    Automatically handles pagination to get all products.
    
    Returns:
        List of products with stock information
    """
    all_products = []
    page = 1
    per_page = 100  # Maximum recommended per page
    
    while True:
        try:
            # Fetch products from current page
            response = wcapi.get(
                'products',
                params={
                    'per_page': per_page,
                    'page': page
                }
            )
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            products = response.json()
            
            # If no products returned, we've reached the end
            if not products:
                break
            
            # Process each product to extract stock information
            for product in products:
                product_data = {
                    'id': product.get('id'),
                    'name': product.get('name', ''),
                    'description': product.get('description', ''),
                    'short_description': product.get('short_description', ''),
                    'sku': product.get('sku', ''),
                    'stock_quantity': product.get('stock_quantity'),  # This is the "leftover" quantity
                    'stock_status': product.get('stock_status', 'unknown'),  # instock, outofstock, onbackorder
                    'manage_stock': product.get('manage_stock', False),
                    'price': product.get('price', '0'),
                    'regular_price': product.get('regular_price', '0'),
                    'sale_price': product.get('sale_price'),
                    'status': product.get('status', ''),
                    'categories': [cat.get('name') for cat in product.get('categories', [])]
                }
                all_products.append(product_data)
            
            # Check if there are more pages
            if len(products) < per_page:
                break  # Last page reached
            
            page += 1
            
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    return all_products

# Usage
products = get_all_products_with_stock()
for product in products:
    print(f"Product: {product['name']}")
    print(f"  Stock Quantity: {product['stock_quantity']}")
    print(f"  Stock Status: {product['stock_status']}")
    print(f"  Description: {product['description'][:100]}...")  # First 100 chars
    print()
```

#### Method 2: Fetch Products with Stock Filtering

```python
def get_products_by_stock_status(stock_status='instock'):
    """
    Fetch products filtered by stock status.
    
    Args:
        stock_status: 'instock', 'outofstock', or 'onbackorder'
    
    Returns:
        List of products matching the stock status
    """
    all_products = []
    page = 1
    per_page = 100
    
    while True:
        try:
            response = wcapi.get(
                'products',
                params={
                    'per_page': per_page,
                    'page': page,
                    'stock_status': stock_status  # Filter by stock status
                }
            )
            
            if response.status_code != 200:
                break
            
            products = response.json()
            if not products:
                break
            
            for product in products:
                all_products.append({
                    'id': product.get('id'),
                    'name': product.get('name', ''),
                    'description': product.get('description', ''),
                    'stock_quantity': product.get('stock_quantity'),
                    'stock_status': product.get('stock_status'),
                    'sku': product.get('sku', '')
                })
            
            if len(products) < per_page:
                break
            
            page += 1
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return all_products

# Get only products in stock
in_stock_products = get_products_by_stock_status('instock')

# Get out of stock products
out_of_stock_products = get_products_by_stock_status('outofstock')
```

#### Method 3: Fetch Single Product by ID

```python
def get_product_stock_by_id(product_id):
    """
    Fetch a specific product's stock information by ID.
    
    Args:
        product_id: The WooCommerce product ID
    
    Returns:
        Dictionary with product stock information
    """
    try:
        response = wcapi.get(f'products/{product_id}')
        
        if response.status_code == 200:
            product = response.json()
            return {
                'id': product.get('id'),
                'name': product.get('name', ''),
                'description': product.get('description', ''),
                'short_description': product.get('short_description', ''),
                'sku': product.get('sku', ''),
                'stock_quantity': product.get('stock_quantity'),
                'stock_status': product.get('stock_status'),
                'manage_stock': product.get('manage_stock', False),
                'price': product.get('price', '0')
            }
        else:
            print(f"Error: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching product {product_id}: {e}")
        return None

# Usage
product = get_product_stock_by_id(123)
if product:
    print(f"Product: {product['name']}")
    print(f"Stock: {product['stock_quantity']} units")
    print(f"Status: {product['stock_status']}")
```

#### Method 4: Fetch Products with Low Stock

```python
def get_low_stock_products(threshold=10):
    """
    Fetch products with stock quantity below a threshold.
    
    Args:
        threshold: Minimum stock quantity threshold
    
    Returns:
        List of products with low stock
    """
    all_products = get_all_products_with_stock()
    
    low_stock_products = []
    for product in all_products:
        stock_qty = product.get('stock_quantity')
        if stock_qty is not None and stock_qty < threshold:
            low_stock_products.append(product)
    
    return low_stock_products

# Get products with less than 10 units in stock
low_stock = get_low_stock_products(threshold=10)
```

## Complete Example: Full Implementation

```python
import os
import json
from woocommerce import API
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

class WooCommerceStockFetcher:
    """Class to fetch product stock information from WooCommerce API."""
    
    def __init__(self):
        """Initialize WooCommerce API connection."""
        self.wcapi = API(
            url=os.getenv('WC_URL'),
            consumer_key=os.getenv('WC_CONSUMER_KEY'),
            consumer_secret=os.getenv('WC_CONSUMER_SECRET'),
            version=os.getenv('WC_API_VERSION', 'wc/v3'),
            timeout=int(os.getenv('WC_TIMEOUT', 30)),
            query_string_auth=True
        )
    
    def get_all_products_with_stock(self) -> List[Dict]:
        """
        Fetch all products with their stock quantities (leftovers).
        
        Returns:
            List of dictionaries containing product information including:
            - id: Product ID
            - name: Product name
            - description: Full product description
            - short_description: Short product description
            - stock_quantity: Remaining stock quantity (leftovers)
            - stock_status: Stock status (instock, outofstock, onbackorder)
            - sku: Product SKU
            - price: Current price
            - categories: List of category names
        """
        all_products = []
        page = 1
        per_page = 100
        
        print("Fetching products from WooCommerce...")
        
        while True:
            try:
                response = self.wcapi.get(
                    'products',
                    params={
                        'per_page': per_page,
                        'page': page
                    }
                )
                
                if response.status_code != 200:
                    print(f"Error: Status {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                
                products = response.json()
                
                if not products:
                    break
                
                for product in products:
                    product_data = {
                        'id': product.get('id'),
                        'name': product.get('name', ''),
                        'description': product.get('description', ''),
                        'short_description': product.get('short_description', ''),
                        'sku': product.get('sku', ''),
                        'stock_quantity': product.get('stock_quantity'),  # Leftovers
                        'stock_status': product.get('stock_status', 'unknown'),
                        'manage_stock': product.get('manage_stock', False),
                        'price': product.get('price', '0'),
                        'regular_price': product.get('regular_price', '0'),
                        'sale_price': product.get('sale_price'),
                        'status': product.get('status', ''),
                        'categories': [cat.get('name') for cat in product.get('categories', [])],
                        'permalink': product.get('permalink', '')
                    }
                    all_products.append(product_data)
                
                print(f"Fetched page {page}: {len(products)} products (total: {len(all_products)})")
                
                if len(products) < per_page:
                    break
                
                page += 1
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        print(f"Total products fetched: {len(all_products)}")
        return all_products
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Fetch a specific product by ID.
        
        Args:
            product_id: WooCommerce product ID
        
        Returns:
            Dictionary with product information or None if not found
        """
        try:
            response = self.wcapi.get(f'products/{product_id}')
            
            if response.status_code == 200:
                product = response.json()
                return {
                    'id': product.get('id'),
                    'name': product.get('name', ''),
                    'description': product.get('description', ''),
                    'short_description': product.get('short_description', ''),
                    'sku': product.get('sku', ''),
                    'stock_quantity': product.get('stock_quantity'),
                    'stock_status': product.get('stock_status'),
                    'manage_stock': product.get('manage_stock', False),
                    'price': product.get('price', '0')
                }
            else:
                print(f"Error: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    def export_to_json(self, products: List[Dict], filename: str = 'products_stock.json'):
        """
        Export products with stock information to JSON file.
        
        Args:
            products: List of product dictionaries
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(products)} products to {filename}")


# Usage Example
if __name__ == "__main__":
    # Initialize fetcher
    fetcher = WooCommerceStockFetcher()
    
    # Fetch all products with stock information
    products = fetcher.get_all_products_with_stock()
    
    # Display products with stock information
    print("\n" + "="*80)
    print("PRODUCTS WITH STOCK INFORMATION")
    print("="*80)
    
    for product in products[:10]:  # Show first 10 products
        print(f"\nProduct ID: {product['id']}")
        print(f"Name: {product['name']}")
        print(f"SKU: {product['sku']}")
        print(f"Stock Quantity (Leftovers): {product['stock_quantity']}")
        print(f"Stock Status: {product['stock_status']}")
        print(f"Description: {product['description'][:100]}...")  # First 100 chars
        print(f"Categories: {', '.join(product['categories'])}")
        print("-" * 80)
    
    # Export to JSON
    fetcher.export_to_json(products, 'products_with_stock.json')
    
    # Filter products with stock
    in_stock = [p for p in products if p['stock_status'] == 'instock' and p['stock_quantity'] is not None]
    print(f"\nProducts in stock: {len(in_stock)}")
    
    # Filter products with low stock (less than 10 units)
    low_stock = [p for p in products if p['stock_quantity'] is not None and p['stock_quantity'] < 10]
    print(f"Products with low stock (<10 units): {len(low_stock)}")
```

## Key Product Fields for Stock Information

When fetching products, the following fields are relevant for stock/leftovers:

| Field | Type | Description |
|-------|------|-------------|
| `stock_quantity` | int or null | **The remaining stock quantity (leftovers)** - This is the main field you need |
| `stock_status` | string | Stock status: `'instock'`, `'outofstock'`, or `'onbackorder'` |
| `manage_stock` | boolean | Whether stock management is enabled for this product |
| `name` | string | Product name |
| `description` | string | Full product description (HTML) |
| `short_description` | string | Short product description |
| `sku` | string | Product SKU (Stock Keeping Unit) |
| `id` | int | Product ID |

## Error Handling

```python
def safe_get_products():
    """Fetch products with comprehensive error handling."""
    try:
        response = wcapi.get('products', params={'per_page': 10, 'page': 1})
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise Exception("Authentication failed. Check your API credentials.")
        elif response.status_code == 404:
            raise Exception("Products endpoint not found. Check API version.")
        else:
            raise Exception(f"API Error: Status {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        return []
```

## Important Notes

1. **Stock Quantity (`stock_quantity`)**: 
   - This field contains the actual remaining stock quantity (leftovers)
   - Can be `null` if stock management is disabled (`manage_stock: false`)
   - Always check if it's `None` before using it in calculations

2. **Stock Status (`stock_status`)**:
   - `'instock'`: Product is in stock
   - `'outofstock'`: Product is out of stock
   - `'onbackorder'`: Product is on backorder

3. **Pagination**:
   - WooCommerce API returns maximum 100 products per page
   - Always implement pagination to get all products
   - Check if returned products count is less than `per_page` to detect last page

4. **API Rate Limits**:
   - Be mindful of API rate limits
   - Add delays between requests if fetching large amounts of data
   - Consider caching results for frequently accessed data

5. **Description Field**:
   - `description`: Full HTML description (may contain HTML tags)
   - `short_description`: Plain text or HTML short description
   - Both fields may contain HTML, so strip tags if needed: `from bs4 import BeautifulSoup; text = BeautifulSoup(html, 'html.parser').get_text()`

## Testing the Connection

```python
def test_connection():
    """Test WooCommerce API connection."""
    try:
        response = wcapi.get('products', params={'per_page': 1})
        if response.status_code == 200:
            print("✓ Connection successful!")
            product = response.json()[0] if response.json() else None
            if product:
                print(f"✓ Sample product: {product.get('name')}")
                print(f"✓ Stock quantity: {product.get('stock_quantity')}")
            return True
        else:
            print(f"✗ Connection failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

# Run test
test_connection()
```

## Summary

This guide provides everything needed to:
1. ✅ Connect to WooCommerce REST API
2. ✅ Fetch all products with automatic pagination
3. ✅ Extract stock quantities (leftovers) from products
4. ✅ Get product names and descriptions
5. ✅ Handle errors and edge cases
6. ✅ Filter products by stock status
7. ✅ Export data to JSON

The main field for product leftovers is **`stock_quantity`**, which contains the remaining stock quantity for each product.
