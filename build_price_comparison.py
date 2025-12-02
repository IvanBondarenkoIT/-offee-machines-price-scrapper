"""
Build price comparison table from scraped data and inventory
Matches products by model codes and creates comparison report
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from utils.model_extractor import ModelExtractor
from utils.inventory_parser import InventoryParser
from utils.enhanced_matcher import EnhancedMatcher

class PriceComparisonBuilder:
    """Build price comparison table"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / 'data' / 'output'
        self.inbox_dir = self.base_dir / 'data' / 'inbox'
        
        # Store loaded data
        self.inventory = None
        self.scraped_data = {}
        
        # Model mapping: model -> list of products from different sources
        self.model_map = {}
    
    def load_inventory(self) -> pd.DataFrame:
        """Load inventory from остатки.xls using InventoryParser"""
        print("\n[1/6] Loading INVENTORY (using InventoryParser)...")
        
        file_path = self.inbox_dir / 'остатки.xls'
        if not file_path.exists():
            print("[WARNING] Inventory file not found")
            return pd.DataFrame()
        
        try:
            # Use new InventoryParser
            parser = InventoryParser()
            df_all = parser.parse_file(str(file_path))
            
            # Get only valid products
            df_valid = parser.get_valid_products()
            
            # Convert to format expected by rest of code
            df_result = df_valid.rename(columns={
                'name': 'name',
                'quantity': 'quantity',
                'price': 'price',
                'model': 'model',
                'brand': 'brand'
            })
            df_result['source'] = 'INVENTORY'
            
            print(f"[OK] Loaded {len(df_result)} valid products from INVENTORY")
            print(f"     (Total parsed: {len(df_all)}, Valid: {len(df_valid)})")
            print(f"     Brands: {df_result['brand'].value_counts().to_dict()}")
            
            return df_result
            
        except Exception as e:
            print(f"[ERROR] Failed to parse inventory: {e}")
            print("[FALLBACK] Using old parsing method...")
            
            # Fallback to old method if new parser fails
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
            print(f"[OK] Loaded {len(df_result)} products from INVENTORY (fallback method)")
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
    
    def extract_models_from_all_sources(self):
        """Extract models from all sources and build mapping with EnhancedMatcher"""
        print("\n[3/6] Extracting MODELS and MATCHING (using EnhancedMatcher)...")
        
        # Prepare data for EnhancedMatcher
        # For Dim Kava specifically, use EnhancedMatcher
        if 'DIM_KAVA' in self.scraped_data and self.inventory is not None and len(self.inventory) > 0:
            print("\n  Using EnhancedMatcher for Dim Kava...")
            
            # Match Dim Kava with inventory using EnhancedMatcher
            matcher = EnhancedMatcher(self.inventory, self.scraped_data['DIM_KAVA'])
            matched_df = matcher.match_products()
            
            # Generate and save report
            report = matcher.generate_report('data/output/dimkava_matching_report.txt')
            print(f"\n  [OK] EnhancedMatcher: {len(matched_df)} matches found")
            print(f"       Report saved: data/output/dimkava_matching_report.txt")
            
            # Save matched products
            if len(matched_df) > 0:
                matched_df.to_excel('data/output/dimkava_matched_products.xlsx', index=False)
                print(f"       Matched products saved: data/output/dimkava_matched_products.xlsx")
        
        # Continue with old method for all sources (for backward compatibility)
        print("\n  Building model map for all sources...")
        all_products = []
        
        # Process inventory
        if self.inventory is not None and len(self.inventory) > 0:
            for idx, row in self.inventory.iterrows():
                # Use model from inventory if already extracted
                model = row.get('model') if 'model' in row and pd.notna(row.get('model')) else ModelExtractor.extract_model(row['name'])
                if model:
                    # Normalize for matching
                    model_normalized = ModelExtractor.normalize_for_matching(model)
                    
                    all_products.append({
                        'source': 'INVENTORY',
                        'name': row['name'],
                        'model': model,  # Original model
                        'model_normalized': model_normalized,  # For matching
                        'quantity': row.get('quantity', 0),
                        'price': row['price'],
                        'regular_price': None,
                        'discount_price': None,
                        'has_discount': False
                    })
        
        # Process scraped data
        for source_name, df in self.scraped_data.items():
            for idx, row in df.iterrows():
                # Use model from scraper if already extracted
                model = row.get('model') if 'model' in row and pd.notna(row.get('model')) else ModelExtractor.extract_model(row['name'])
                if model:
                    # Normalize for matching
                    model_normalized = ModelExtractor.normalize_for_matching(model)
                    
                    # Normalize price data for different scraper formats
                    if 'final_price' in row:
                        # ALTA/KONTAKT/ELITE/DIMKAVA format
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
        
        # Build model mapping using NORMALIZED models
        # First pass: exact matches
        for product in all_products:
            model_norm = product['model_normalized']
            if model_norm not in self.model_map:
                self.model_map[model_norm] = []
            self.model_map[model_norm].append(product)
        
        # Second pass: fuzzy matching using ModelExtractor.match_models_fuzzy
        inventory_products = [p for p in all_products if p['source'] == 'INVENTORY']
        scraped_products = [p for p in all_products if p['source'] != 'INVENTORY']
        
        fuzzy_matches = 0
        for inv_product in inventory_products:
            # Check if already has matches
            if len([p for p in self.model_map[inv_product['model_normalized']] if p['source'] != 'INVENTORY']) > 0:
                continue  # Already has competitors
            
            # Try fuzzy matching with confidence
            inv_model = inv_product['model']
            
            for scraped_product in scraped_products:
                scraped_model = scraped_product['model']
                
                # Use improved fuzzy matching
                is_match, confidence = ModelExtractor.match_models_fuzzy(inv_model, scraped_model)
                
                if is_match and confidence >= 0.9:  # Only high-confidence matches
                    # Add to same group
                    inv_norm = inv_product['model_normalized']
                    if scraped_product not in self.model_map[inv_norm]:
                        self.model_map[inv_norm].append(scraped_product)
                        fuzzy_matches += 1
        
        print(f"[OK] Extracted {len(all_products)} products total")
        print(f"     - Inventory: {len(inventory_products)} products")
        print(f"     - Scraped: {len(scraped_products)} products")
        print(f"[OK] Found {len(self.model_map)} unique normalized models")
        print(f"[OK] Added {fuzzy_matches} fuzzy matches (confidence >= 0.9)")
        
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
            
            # Build row - keep Our Price as inventory input cost (per requirement)
            row = {
                'Quantity': inventory_product['quantity'],
                'Model': inventory_product['model'],  # Original model for display
                'Product Name': inventory_product['name'],
                'Our Cost': inventory_product['price'],
                'Our Price': inventory_product['price'],
            }
            
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

        # If no rows matched (e.g., no competitors found), return empty-safe dataframe
        if df.empty:
            print("[WARNING] No matched products to compare (empty comparison table)")
            # Return an empty dataframe with expected columns so downstream steps succeed
            return pd.DataFrame(columns=[
                'Quantity', 'Model', 'Product Name', 'Our Price',
                'DIM_KAVA', 'ALTA', 'KONTAKT', 'ELITE', 'COFFEEHUB', 'COFFEEPIN', 'VELI_STORE', 'VEGA_GE'
            ])

        # Sort by model if column exists
        if 'Model' in df.columns:
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
        
        # Use Our Price (retail) for totals, and include cost metrics
        stats = {
            'Total Products': len(df),
            'Total Quantity': df['Quantity'].sum(),
            'Total Retail Value': (df['Quantity'] * df['Our Price']).sum() if 'Our Price' in df.columns else 0,
            'Avg Our Price (Retail)': df['Our Price'].mean() if 'Our Price' in df.columns else 0,
            'Min Our Price': df['Our Price'].min() if 'Our Price' in df.columns else 0,
            'Max Our Price': df['Our Price'].max() if 'Our Price' in df.columns else 0,
            'Total Cost Value': (df['Quantity'] * df['Our Cost']).sum() if 'Our Cost' in df.columns else 0,
            'Avg Our Cost': df['Our Cost'].mean() if 'Our Cost' in df.columns else 0,
            'Estimated Gross Margin %': (
                (1 - (df['Our Cost'].sum() / df['Our Price'].sum())) * 100
                if ('Our Cost' in df.columns and 'Our Price' in df.columns and df['Our Price'].sum() > 0)
                else 0
            ),
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

