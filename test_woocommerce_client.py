"""
Test script for WooCommerce client
Tests connection and data retrieval
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from utils.woocommerce_client import WooCommerceClient, get_woocommerce_config

def test_config():
    """Test configuration loading"""
    print("="*80)
    print("TEST 1: Configuration Loading")
    print("="*80)
    
    config = get_woocommerce_config()
    
    if not config:
        print("[FAIL] Configuration not found")
        print("\nRequired environment variables:")
        print("  - WC_URL")
        print("  - WC_CONSUMER_KEY")
        print("  - WC_CONSUMER_SECRET")
        print("\nOptional:")
        print("  - WC_API_VERSION (default: wc/v3)")
        return False
    
    print("[OK] Configuration loaded:")
    print(f"  URL: {config['url']}")
    print(f"  Consumer Key: {config['consumer_key'][:10]}...")
    print(f"  Consumer Secret: {config['consumer_secret'][:10]}...")
    print(f"  API Version: {config['api_version']}")
    
    return True, config

def test_connection(config):
    """Test API connection"""
    print("\n" + "="*80)
    print("TEST 2: API Connection")
    print("="*80)
    
    try:
        client = WooCommerceClient(**config)
        print("[OK] Client created successfully")
        
        # Test simple API call
        print("\nTesting API endpoint...")
        response = client._make_request('products', {'per_page': 1})
        
        if response is None:
            print("[FAIL] API request failed")
            return False
        
        if isinstance(response, list) and len(response) > 0:
            print(f"[OK] API connection successful")
            print(f"  Sample product: {response[0].get('name', 'N/A')[:50]}...")
            return True, client
        else:
            print("[WARNING] API returned empty response")
            return False
            
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return False

def test_data_retrieval(client):
    """Test data retrieval"""
    print("\n" + "="*80)
    print("TEST 3: Data Retrieval")
    print("="*80)
    
    try:
        print("Fetching products...")
        df = client.get_stock_data()
        
        if df is None or len(df) == 0:
            print("[WARNING] No data retrieved")
            return False
        
        print(f"[OK] Retrieved {len(df)} products with models")
        print(f"\nColumns: {', '.join(df.columns)}")
        
        print("\nFirst 5 products:")
        print("-"*80)
        for idx, row in df.head().iterrows():
            print(f"  {idx+1}. Model: {row['model']}")
            print(f"     Name: {row['name'][:60]}...")
            print(f"     Price: {row['price']}")
            print(f"     Stock: {row['stock_quantity']}")
            print()
        
        print(f"\nStatistics:")
        print(f"  Total products: {len(df)}")
        print(f"  Products with price: {(df['price'].notna()).sum()}")
        print(f"  Products with stock: {(df['stock_quantity'] > 0).sum()}")
        print(f"  Total stock quantity: {df['stock_quantity'].sum()}")
        
        return True, df
        
    except Exception as e:
        print(f"[FAIL] Data retrieval error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_extraction(df):
    """Test model extraction quality"""
    print("\n" + "="*80)
    print("TEST 4: Model Extraction Quality")
    print("="*80)
    
    if df is None or len(df) == 0:
        print("[SKIP] No data to test")
        return True
    
    # Check for missing models
    missing_models = df[df['model'].isna() | (df['model'] == '')]
    if len(missing_models) > 0:
        print(f"[WARNING] {len(missing_models)} products without extracted models")
        print("\nSample products without models:")
        for idx, row in missing_models.head(3).iterrows():
            print(f"  - {row['name'][:60]}...")
    else:
        print("[OK] All products have extracted models")
    
    # Check model uniqueness
    unique_models = df['model'].nunique()
    print(f"\nUnique models: {unique_models}")
    print(f"Total products: {len(df)}")
    
    if unique_models < len(df) * 0.8:
        print("[WARNING] Many duplicate models (might indicate extraction issues)")
    else:
        print("[OK] Good model diversity")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("WOOCOMMERCE CLIENT TEST SUITE")
    print("="*80)
    print("\nThis script tests the WooCommerce API client.")
    print("Make sure you have set the required environment variables.\n")
    
    # Test 1: Configuration
    result = test_config()
    if not result:
        print("\n[STOP] Cannot continue without configuration")
        sys.exit(1)
    
    success, config = result if isinstance(result, tuple) else (result, None)
    if not success:
        sys.exit(1)
    
    # Test 2: Connection
    result = test_connection(config)
    if not result:
        print("\n[STOP] Cannot continue without API connection")
        sys.exit(1)
    
    success, client = result if isinstance(result, tuple) else (result, None)
    if not success:
        sys.exit(1)
    
    # Test 3: Data Retrieval
    result = test_data_retrieval(client)
    if not result:
        print("\n[WARNING] Data retrieval failed, but connection works")
        sys.exit(1)
    
    success, df = result if isinstance(result, tuple) else (result, None)
    if not success:
        sys.exit(1)
    
    # Test 4: Model Extraction
    test_model_extraction(df)
    
    # Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("[OK] All tests passed!")
    print(f"[OK] Retrieved {len(df)} products successfully")
    print("\nClient is ready for use in export script.")
    print("="*80)

if __name__ == "__main__":
    main()
