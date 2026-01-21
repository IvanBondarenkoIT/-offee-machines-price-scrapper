"""
Build price comparison table from scraped data and inventory
Matches products by model codes and creates comparison report
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from utils.model_extractor import ModelExtractor

# WooCommerce imports (optional - graceful degradation if not available)
try:
    from utils.woocommerce_client import WooCommerceClient
    from config import WOOCOMMERCE_CONFIG
    WOOCOMMERCE_AVAILABLE = True
except ImportError:
    WOOCOMMERCE_AVAILABLE = False
    WOOCOMMERCE_CONFIG = {"enabled": False}

class PriceComparisonBuilder:
    """Build price comparison table"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / 'data' / 'output'
        self.inbox_dir = self.base_dir / 'data' / 'inbox'
        
        # Store loaded data
        self.inventory = None
        self.scraped_data = {}
        self.woocommerce_stock = None  # WooCommerce stock data
        
        # Model mapping: model -> list of products from different sources
        self.model_map = {}
    
    def load_inventory(self) -> pd.DataFrame:
        """Load inventory from остатки.xls"""
        print("\n[1/6] Loading INVENTORY...")
        
        file_path = self.inbox_dir / 'остатки.xls'
        if not file_path.exists():
            print("[WARNING] Inventory file not found")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path, header=None)
        
        products = []
        for i in range(len(df)):
            row = df.iloc[i]
            row_values = [v for v in row.values if pd.notna(v)]
            
            if len(row_values) < 4:
                continue
            
            row_str = ' '.join([str(v) for v in row_values])
            if 'delonghi' not in row_str.lower() and 'melitta' not in row_str.lower() and 'nivona' not in row_str.lower():
                continue
            
            try:
                name = qty = price = None
                
                if len(row_values) == 5:
                    name, qty, price = str(row_values[1]), row_values[2], row_values[3]
                elif len(row_values) == 6:
                    name, qty, price = str(row_values[1]), row_values[3], row_values[4]
                elif len(row_values) == 7:
                    name, qty, price = str(row_values[1]), row_values[4], row_values[5]
                
                if name and ('delonghi' in name.lower() or 'melitta' in name.lower() or 'nivona' in name.lower()):
                    if isinstance(qty, (int, float)) and isinstance(price, (int, float)):
                        if qty > 0 and price > 0:
                            products.append({
                                'name': name,
                                'quantity': int(qty),
                                'price': float(price),
                                'source': 'INVENTORY'
                            })
            except:
                pass
        
        df_result = pd.DataFrame(products)
        print(f"[OK] Loaded {len(df_result)} products from INVENTORY")
        return df_result
    
    def load_scraped_data(self) -> Dict[str, pd.DataFrame]:
        """Load all scraped data"""
        print("\n[2/6] Loading SCRAPED DATA...")
        
        sources = {
            'ALTA': 'alta_*_prices_*.xlsx',
            'KONTAKT': 'kontakt_*_prices_*.xlsx',
            'ELITE': 'elite_*_prices_*.xlsx',
            'DIM_KAVA': 'dimkava_*_prices_*.xlsx',
            'COFFEEHUB': 'coffeehub_prices_*.xlsx',
            'COFFEEPIN': 'coffeepin_prices_*.xlsx',
            'VELI_STORE': 'veli_store_prices_*.xlsx',
            'VEGA_GE': 'vega_ge_prices_*.xlsx',
        }
        
        result = {}
        
        for source_name, pattern in sources.items():
            files = list(self.output_dir.glob(pattern))
            if not files:
                print(f"[WARNING] {source_name}: No files found")
                continue
            
            # Get latest file
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            df = pd.read_excel(latest_file)
            
            # Add source column
            df['source'] = source_name
            
            result[source_name] = df
            print(f"[OK] {source_name}: {len(df)} products from {latest_file.name}")
        
        return result
    
    def load_woocommerce_stock(self) -> pd.DataFrame:
        """Load stock data from WooCommerce API"""
        print("\n[2.5/6] Loading WOOCOMMERCE STOCK...")
        
        # Check if WooCommerce is available
        if not WOOCOMMERCE_AVAILABLE:
            print("  [SKIP] WooCommerce client not available (utils/woocommerce_client.py not found)")
            return pd.DataFrame()
        
        # Check if WooCommerce is enabled
        if not WOOCOMMERCE_CONFIG.get("enabled", False):
            print("  [SKIP] WooCommerce integration is disabled (USE_WOOCOMMERCE_STOCK=false)")
            return pd.DataFrame()
        
        # Validate config
        if not WOOCOMMERCE_CONFIG.get("url"):
            print("  [WARNING] WC_URL not set in .env, skipping WooCommerce")
            return pd.DataFrame()
        
        if not WOOCOMMERCE_CONFIG.get("consumer_key"):
            print("  [WARNING] WC_CONSUMER_KEY not set in .env, skipping WooCommerce")
            return pd.DataFrame()
        
        if not WOOCOMMERCE_CONFIG.get("consumer_secret"):
            print("  [WARNING] WC_CONSUMER_SECRET not set in .env, skipping WooCommerce")
            return pd.DataFrame()
        
        try:
            print("  [WooCommerce] Connecting to API...")
            
            # Create WooCommerce client
            client = WooCommerceClient(
                url=WOOCOMMERCE_CONFIG["url"],
                consumer_key=WOOCOMMERCE_CONFIG["consumer_key"],
                consumer_secret=WOOCOMMERCE_CONFIG["consumer_secret"],
                api_version=WOOCOMMERCE_CONFIG.get("api_version", "wc/v3"),
                timeout=WOOCOMMERCE_CONFIG.get("timeout", 30),
                retry_attempts=WOOCOMMERCE_CONFIG.get("retry_attempts", 3),
                retry_delay=WOOCOMMERCE_CONFIG.get("retry_delay", 2)
            )
            
            # Get data
            df_result = client.get_stock_data()
            
            # Validate
            if df_result is None or len(df_result) == 0:
                print("  [WooCommerce] No products with stock > 0 returned")
                return pd.DataFrame()
            
            print(f"  [WooCommerce] [OK] Loaded {len(df_result)} products with stock > 0")
            print(f"                With discount: {client.stats['with_discount']}")
            print(f"                Without model: {client.stats['no_model']}")
            
            return df_result
            
        except Exception as e:
            print(f"  [WooCommerce] [ERROR] Failed to load: {e}")
            print("  [WooCommerce] [WARNING] Continuing without WooCommerce data (graceful degradation)")
            return pd.DataFrame()
    
    def extract_models_from_all_sources(self):
        """Extract models from all sources and build mapping with normalization"""
        print("\n[3/6] Extracting MODELS...")
        
        all_products = []
        
        # Process inventory
        if self.inventory is not None and len(self.inventory) > 0:
            for idx, row in self.inventory.iterrows():
                model = ModelExtractor.extract_model(row['name'])
                if model:
                    # Normalize for matching
                    model_normalized = ModelExtractor.normalize_for_matching(model)
                    
                    all_products.append({
                        'source': 'INVENTORY',
                        'name': row['name'],
                        'model': model,  # Original model
                        'model_normalized': model_normalized,  # For matching
                        'quantity': row['quantity'],
                        'price': row['price'],
                        'regular_price': None,
                        'discount_price': None,
                        'has_discount': False
                    })
        
        # Process scraped data
        for source_name, df in self.scraped_data.items():
            for idx, row in df.iterrows():
                model = ModelExtractor.extract_model(row['name'])
                if model:
                    # Normalize for matching
                    model_normalized = ModelExtractor.normalize_for_matching(model)
                    
                    # Normalize price data for different scraper formats
                    if 'final_price' in row:
                        # ALTA/KONTAKT/ELITE format
                        price = row['final_price']
                        regular_price = row.get('regular_price')
                        discount_price = row.get('discount_price')
                        has_discount = row.get('has_discount', False)
                    elif 'price' in row:
                        # CoffeeHub format
                        price = row['price']
                        regular_price = row.get('price') if not pd.isna(row.get('price')) else None
                        discount_price = row.get('discount_price') if not pd.isna(row.get('discount_price')) else None
                        has_discount = discount_price is not None and discount_price != price
                    else:
                        # Fallback
                        price = row.get('price', 0)
                        regular_price = row.get('regular_price', price)
                        discount_price = row.get('discount_price')
                        has_discount = row.get('has_discount', False)
                    
                    all_products.append({
                        'source': source_name,
                        'name': row['name'],
                        'model': model,  # Original model
                        'model_normalized': model_normalized,  # For matching
                        'quantity': None,
                        'price': price,
                        'regular_price': regular_price,
                        'discount_price': discount_price,
                        'has_discount': has_discount
                    })
        
        # Add WooCommerce stock data if available (before building model map)
        if self.woocommerce_stock is not None and len(self.woocommerce_stock) > 0:
            print("\n  Adding WooCommerce stock data to matching...")
            for _, row in self.woocommerce_stock.iterrows():
                model = row.get('model')
                if not model:
                    continue
                
                model_normalized = ModelExtractor.normalize_for_matching(model)
                
                # Add WooCommerce product to all_products
                wc_product = {
                    'source': 'WOOCOMMERCE_STOCK',
                    'name': row.get('name', ''),
                    'model': model,
                    'model_normalized': model_normalized,
                    'quantity': row.get('stock_quantity', 0),
                    'price': row.get('price', 0),
                    'regular_price': row.get('regular_price'),
                    'discount_price': row.get('sale_price'),
                    'has_discount': row.get('has_discount', False),
                    'stock_quantity': row.get('stock_quantity', 0),  # Keep for filtering
                }
                all_products.append(wc_product)
            
            print(f"  [OK] Added {len(self.woocommerce_stock)} WooCommerce products to matching")
        
        # Build model mapping using NORMALIZED models
        # First pass: exact matches
        for product in all_products:
            model_norm = product['model_normalized']
            if model_norm not in self.model_map:
                self.model_map[model_norm] = []
            self.model_map[model_norm].append(product)
        
        # Second pass: fuzzy matching for unmatched inventory items
        inventory_products = [p for p in all_products if p['source'] == 'INVENTORY']
        scraped_products = [p for p in all_products if p['source'] != 'INVENTORY' and p['source'] != 'WOOCOMMERCE_STOCK']
        wc_products = [p for p in all_products if p['source'] == 'WOOCOMMERCE_STOCK']
        
        fuzzy_matches = 0
        for inv_product in inventory_products:
            # Check if already has matches
            if len([p for p in self.model_map[inv_product['model_normalized']] if p['source'] != 'INVENTORY']) > 0:
                continue  # Already has competitors
            
            # Try fuzzy matching - look for base model match
            inv_norm = inv_product['model_normalized']
            
            for scraped_product in scraped_products:
                scraped_norm = scraped_product['model_normalized']
                
                # Check if one is substring of another (base model match)
                # EC9255 should match EC9255M, EC9255T
                # ECI341 should match ECI341BK, ECI341BZ
                if len(inv_norm) >= 5 and len(scraped_norm) >= 5:
                    if inv_norm in scraped_norm or scraped_norm in inv_norm:
                        # Add to same group
                        if scraped_product not in self.model_map[inv_norm]:
                            self.model_map[inv_norm].append(scraped_product)
                            fuzzy_matches += 1
        
        # Third pass: fuzzy matching for WooCommerce (separate to avoid conflicts)
        wc_fuzzy_matches = 0
        for inv_product in inventory_products:
            inv_model = inv_product['model']
            inv_norm = inv_product['model_normalized']
            
            # Check if WooCommerce product already in this group
            has_wc = any(p['source'] == 'WOOCOMMERCE_STOCK' for p in self.model_map[inv_norm])
            if has_wc:
                continue  # Already has WooCommerce match
            
            # Try fuzzy matching with WooCommerce products
            for wc_product in wc_products:
                wc_model = wc_product['model']
                if not wc_model:
                    continue
                
                # Use improved fuzzy matching
                is_match, confidence = ModelExtractor.match_models_fuzzy(inv_model, wc_model)
                
                if is_match and confidence >= 0.9:  # Only high-confidence matches
                    # Add to same group
                    if wc_product not in self.model_map[inv_norm]:
                        self.model_map[inv_norm].append(wc_product)
                        wc_fuzzy_matches += 1
                        break  # Only one WooCommerce match per inventory product
        
        # Fourth pass: Special handling for DimKava scraper ↔ WooCommerce
        # If product found via DimKava scraper but not via WooCommerce API, try name-based matching
        dimkava_scraper_products = [p for p in all_products if p['source'] == 'DIM_KAVA']
        dimkava_wc_matches = 0
        
        for dimkava_product in dimkava_scraper_products:
            dimkava_model = dimkava_product.get('model')
            dimkava_name = dimkava_product.get('name', '').upper()
            
            if not dimkava_model:
                continue
            
            # Find inventory product for this DimKava scraper product
            dimkava_norm = dimkava_product['model_normalized']
            inv_for_dimkava = next((p for p in self.model_map[dimkava_norm] if p['source'] == 'INVENTORY'), None)
            
            if not inv_for_dimkava:
                continue  # No inventory product for this DimKava scraper product
            
            # Check if WooCommerce already matched for this inventory product
            inv_norm = inv_for_dimkava['model_normalized']
            has_wc = any(p['source'] == 'WOOCOMMERCE_STOCK' for p in self.model_map[inv_norm])
            
            if has_wc:
                continue  # Already has WooCommerce match
            
            # Try to find WooCommerce product by name (if model didn't match)
            # Extract key words from DimKava scraper product name
            # Look for similar WooCommerce products
            for wc_product in wc_products:
                wc_name = wc_product.get('name', '').upper()
                wc_model = wc_product.get('model', '')
                
                # If WooCommerce product has a model, skip (already tried in fuzzy matching)
                if wc_model:
                    continue
                
                # Try name-based matching: check if key model parts are in WooCommerce name
                # Extract model parts from DimKava name
                model_parts = []
                if dimkava_model:
                    # Remove common suffixes and get base parts
                    base_model = ModelExtractor.normalize_for_matching(dimkava_model)
                    # Try to find base model in WooCommerce name
                    if base_model and len(base_model) >= 4:
                        # Check if base model appears in WooCommerce name
                        if base_model in wc_name.replace(' ', '').replace('-', '').replace('/', ''):
                            # Additional check: brand should match
                            inv_brand = inv_for_dimkava.get('name', '').upper()
                            brand_match = False
                            for brand in ['DELONGHI', 'MELITTA', 'MELITA', 'NIVONA', 'GAGGIA', 'SAECO']:
                                if brand in inv_brand and brand in wc_name:
                                    brand_match = True
                                    break
                            
                            if brand_match:
                                # Found match by name!
                                if wc_product not in self.model_map[inv_norm]:
                                    self.model_map[inv_norm].append(wc_product)
                                    dimkava_wc_matches += 1
                                    break  # Only one match per DimKava product
        
        print(f"[OK] Extracted {len(all_products)} products total")
        print(f"     - Inventory: {len(inventory_products)} products")
        print(f"     - Scraped: {len(scraped_products)} products")
        if len(wc_products) > 0:
            print(f"     - WooCommerce: {len(wc_products)} products")
        print(f"[OK] Found {len(self.model_map)} unique normalized models")
        print(f"[OK] Added {fuzzy_matches} fuzzy matches (confidence >= 0.9)")
        if wc_fuzzy_matches > 0:
            print(f"[OK] Added {wc_fuzzy_matches} WooCommerce fuzzy matches (confidence >= 0.9)")
        if dimkava_wc_matches > 0:
            print(f"[OK] Added {dimkava_wc_matches} DimKava scraper ↔ WooCommerce name-based matches")
        
        # Show matching statistics
        matched_inv = len([p for p in inventory_products if len([s for s in self.model_map[p['model_normalized']] if s['source'] != 'INVENTORY']) > 0])
        print(f"[OK] Matched {matched_inv}/{len(inventory_products)} inventory products ({matched_inv/len(inventory_products)*100:.1f}%)")
        
        return all_products
    
    def build_comparison_table(self) -> pd.DataFrame:
        """Build final comparison table"""
        print("\n[4/6] Building COMPARISON TABLE...")
        
        rows = []
        
        for model_norm, products in sorted(self.model_map.items()):
            # Find inventory product
            inventory_product = next((p for p in products if p['source'] == 'INVENTORY'), None)
            
            # Skip if no inventory (we only want our products)
            if not inventory_product:
                continue
            
            # Find competitor products
            competitor_products = {p['source']: p for p in products if p['source'] != 'INVENTORY'}
            
            # Skip if no competitors (need at least one for comparison)
            if not competitor_products:
                continue
            
            # Check if product has stock in WooCommerce (for additional information)
            wc_stock_product = next((p for p in products if p['source'] == 'WOOCOMMERCE_STOCK'), None)
            stock_quantity = wc_stock_product.get('stock_quantity', 0) if wc_stock_product else 0
            
            # NOTE: We show ALL inventory products, WooCommerce data is additional information
            # No filtering by WooCommerce stock - all inventory products are shown
            
            # Build row - keep Our Price as inventory input cost (per requirement)
            row = {
                'Quantity': inventory_product['quantity'],
                'Model': inventory_product['model'],  # Original model for display
                'Product Name': inventory_product['name'],
                'Our Price': inventory_product['price'],
            }
            
            # Add WooCommerce stock and price data
            if wc_stock_product:
                row['DIM_KAVA_STOCK'] = int(wc_stock_product.get('stock_quantity', 0))
                if wc_stock_product.get('has_discount') and wc_stock_product.get('regular_price') and wc_stock_product.get('discount_price'):
                    regular = round(wc_stock_product['regular_price'], 2)
                    discount = round(wc_stock_product['discount_price'], 2)
                    row['DIM_KAVA_WC_PRICE'] = f"{regular:.2f} \\ {discount:.2f}"
                else:
                    price = wc_stock_product.get('price') or wc_stock_product.get('regular_price')
                    if price and not pd.isna(price):
                        rounded = round(price, 2)
                        row['DIM_KAVA_WC_PRICE'] = f"{rounded:.2f}"
                    else:
                        row['DIM_KAVA_WC_PRICE'] = '-'
            else:
                row['DIM_KAVA_STOCK'] = '-'
                row['DIM_KAVA_WC_PRICE'] = '-'
            
            # Add competitor prices - DIM_KAVA first (our website), then others
            for source in ['DIM_KAVA', 'ALTA', 'KONTAKT', 'ELITE', 'COFFEEHUB', 'COFFEEPIN', 'VELI_STORE', 'VEGA_GE']:
                if source in competitor_products:
                    p = competitor_products[source]
                    if p['has_discount'] and p['regular_price'] and p['discount_price']:
                        row[source] = f"{p['regular_price']:.2f} \\ {p['discount_price']:.2f}"
                    else:
                        # Use regular_price if available and valid, otherwise price
                        regular_price = p.get('regular_price')
                        price = p.get('price')
                        
                        if regular_price and not pd.isna(regular_price):
                            row[source] = f"{regular_price:.2f}"
                        elif price and not pd.isna(price):
                            row[source] = f"{price:.2f}"
                        else:
                            row[source] = '-'
                else:
                    row[source] = '-'
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Sort by model
        df = df.sort_values('Model')
        
        print(f"[OK] Created comparison table with {len(df)} products")
        
        return df
    
    def save_comparison(self, df: pd.DataFrame) -> Path:
        """Save comparison table to Excel with separate sheets for each source"""
        print("\n[5/6] Saving COMPARISON TABLE...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'price_comparison_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main comparison sheet
            df.to_excel(writer, sheet_name='Price Comparison', index=False)
            
            # Add statistics sheet
            stats = self.calculate_statistics(df)
            stats_df = pd.DataFrame([stats])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Add individual source sheets with full scraped data
            print("  Adding individual source sheets...")
            for source_name, source_df in self.scraped_data.items():
                if not source_df.empty:
                    # Select relevant columns
                    cols = ['name', 'price', 'regular_price', 'discount_price', 'has_discount', 'url']
                    available_cols = [c for c in cols if c in source_df.columns]
                    sheet_df = source_df[available_cols].copy()
                    
                    # Rename for clarity
                    sheet_df = sheet_df.rename(columns={
                        'name': 'Product Name',
                        'price': 'Price',
                        'regular_price': 'Regular Price',
                        'discount_price': 'Discount Price',
                        'has_discount': 'Has Discount',
                        'url': 'URL'
                    })
                    
                    sheet_df.to_excel(writer, sheet_name=source_name, index=False)
                    print(f"    [{source_name}] {len(sheet_df)} products")
            
            # Add INVENTORY sheet with our stock
            inventory_data = self.load_inventory()
            if not inventory_data.empty:
                inventory_sheet = inventory_data[['name', 'quantity', 'price']].copy()
                inventory_sheet = inventory_sheet.rename(columns={
                    'name': 'Product Name',
                    'quantity': 'Quantity',
                    'price': 'Our Cost Price'
                })
                inventory_sheet.to_excel(writer, sheet_name='INVENTORY', index=False)
                print(f"    [INVENTORY] {len(inventory_sheet)} products")
        
        print(f"[OK] Saved to: {output_file.name}")
        
        return output_file
    
    def calculate_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate comparison statistics"""
        print("\n[6/6] Calculating STATISTICS...")
        
        stats = {
            'Total Products': len(df),
            'Total Quantity': df['Quantity'].sum(),
            'Total Value': (df['Quantity'] * df['Our Price']).sum(),
            'Avg Our Price': df['Our Price'].mean(),
            'Min Our Price': df['Our Price'].min(),
            'Max Our Price': df['Our Price'].max(),
        }
        
        # Count competitors per product
        competitor_cols = ['ALTA', 'KONTAKT', 'ELITE', 'DIM_KAVA']
        df['Competitor Count'] = df[competitor_cols].apply(
            lambda row: sum(1 for v in row if v != '-'), axis=1
        )
        
        stats['Avg Competitors per Product'] = df['Competitor Count'].mean()
        stats['Products with 1+ Competitors'] = (df['Competitor Count'] >= 1).sum()
        stats['Products with 2+ Competitors'] = (df['Competitor Count'] >= 2).sum()
        stats['Products with 3+ Competitors'] = (df['Competitor Count'] >= 3).sum()
        
        print(f"[OK] Statistics calculated")
        
        return stats
    
    def run(self):
        """Run full comparison build process"""
        print("="*80)
        print("BUILDING PRICE COMPARISON")
        print("="*80)
        
        # Load data
        self.inventory = self.load_inventory()
        self.scraped_data = self.load_scraped_data()
        self.woocommerce_stock = self.load_woocommerce_stock()  # Load WooCommerce stock
        
        # Extract models
        self.extract_models_from_all_sources()
        
        # Build comparison
        comparison_df = self.build_comparison_table()
        
        # Save
        output_file = self.save_comparison(comparison_df)
        
        print("\n" + "="*80)
        print("COMPARISON BUILD COMPLETE")
        print("="*80)
        print(f"\nOutput file: {output_file}")
        print(f"Products compared: {len(comparison_df)}")
        
        return comparison_df, output_file


if __name__ == "__main__":
    builder = PriceComparisonBuilder()
    df, output_file = builder.run()
    
    print("\nFirst 10 rows:")
    print(df.head(10).to_string(index=False))

