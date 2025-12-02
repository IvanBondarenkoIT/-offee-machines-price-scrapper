"""
Inventory Parser - Parse остатки.xls file with complex structure
Handles Georgian encoding, irregular headers, and mixed data types
"""

import pandas as pd
import re
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.model_extractor import ModelExtractor

logger = setup_logger("inventory_parser")


class InventoryParser:
    """
    Parser for остатки.xls file with special handling for its structure
    
    File structure:
    - Row 0-3: Headers and metadata (Georgian text)
    - Row 4: Column headers (п/п, Код, Наименование товара, etc.)
    - Row 5+: Actual data
    - Column 9: Product name
    - Column 17: Quantity
    - Column 18: Price
    """
    
    # Keywords to identify spare parts and accessories (to exclude)
    SPARE_PARTS_KEYWORDS = [
        'ASSY', 'PCB', 'TUBE', 'FUNNEL', 'SUPPORT', 'DRAINING',
        'CARAF', 'TANK', 'PIPE', 'CONNECTOR', 'VALVE', 'GASKET',
        'SEAL', 'SPRING', 'SCREW', 'NUT', 'BOLT', 'WASHER',
        'O-RING', 'BEARING', 'MOTOR', 'PUMP', 'SENSOR', 'SWITCH',
        'CABLE', 'WIRE', 'BOARD', 'DISPLAY', 'BUTTON', 'KNOB',
    ]
    
    ACCESSORIES_KEYWORDS = [
        'PITCHER', 'TAMPER', 'SPOON', 'MAT', 'BRUSH', 'CLOTH',
        'DESCAL', 'CLEAN', 'TABLET', 'LIQUID', 'POWDER',
        'FILTER', 'CARTRIDGE', 'SOFTBAL',
    ]
    
    # Valid brands
    VALID_BRANDS = [
        'DELONGHI', 'DE LONGHI', "DE'LONGHI",
        'MELITTA', 'MELITA',
        'NIVONA',
        'JURA',
        'SAECO',
        'GAGGIA',
    ]
    
    def __init__(self):
        self.raw_df = None
        self.parsed_df = None
        self.stats = {
            'total_rows': 0,
            'valid_products': 0,
            'spare_parts': 0,
            'accessories': 0,
            'no_brand': 0,
            'no_model': 0,
            'no_price': 0,
        }
    
    def parse_file(self, filepath: str) -> pd.DataFrame:
        """
        Parse inventory file and return normalized DataFrame
        
        Args:
            filepath: Path to остатки.xls file
            
        Returns:
            DataFrame with columns:
            - name: Full product name
            - model: Extracted model code
            - brand: Extracted brand
            - quantity: Stock quantity
            - price: Price
            - category: Product category (product/spare_part/accessory)
            - is_valid: Whether this is a valid product for comparison
        """
        logger.info(f"Parsing inventory file: {filepath}")
        
        # Read raw file
        try:
            self.raw_df = pd.read_excel(filepath)
            self.stats['total_rows'] = len(self.raw_df)
            logger.info(f"Loaded {len(self.raw_df)} rows from file")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise
        
        # Parse and normalize
        products = []
        
        # Start from row 5 (0-indexed), skip header rows
        for idx in range(5, len(self.raw_df)):
            try:
                row = self.raw_df.iloc[idx]
                
                # Extract product name from column 9
                name = self._get_cell_value(row, 9)
                if not name or len(str(name).strip()) < 3:
                    continue
                
                name = str(name).strip()
                
                # Extract quantity from column 17
                quantity = self._get_numeric_value(row, 17)
                
                # Extract price from column 18
                price = self._get_numeric_value(row, 18)
                
                # Skip if no price (likely not a product)
                if price is None or price <= 0:
                    continue
                
                # Extract brand
                brand = self._extract_brand(name)
                
                # Extract model
                model = self._extract_model(name)
                
                # Determine category
                category = self._categorize_product(name)
                
                # Determine if valid product
                is_valid = self._is_valid_product(name, brand, model, category, price)
                
                # Build product dict
                product = {
                    'name': name,
                    'model': model,
                    'brand': brand,
                    'quantity': quantity if quantity else 0,
                    'price': price,
                    'category': category,
                    'is_valid': is_valid,
                    'source_row': idx,
                }
                
                products.append(product)
                
                # Update stats
                if category == 'spare_part':
                    self.stats['spare_parts'] += 1
                elif category == 'accessory':
                    self.stats['accessories'] += 1
                
                if is_valid:
                    self.stats['valid_products'] += 1
                
                if not brand:
                    self.stats['no_brand'] += 1
                if not model:
                    self.stats['no_model'] += 1
                
            except Exception as e:
                logger.warning(f"Error parsing row {idx}: {e}")
                continue
        
        # Create DataFrame
        self.parsed_df = pd.DataFrame(products)
        
        logger.info(f"Parsed {len(self.parsed_df)} products from inventory")
        self._log_stats()
        
        return self.parsed_df
    
    def get_valid_products(self) -> pd.DataFrame:
        """
        Get only valid products (exclude spare parts, accessories, etc.)
        
        Returns:
            DataFrame with only valid products
        """
        if self.parsed_df is None:
            raise ValueError("No parsed data. Call parse_file() first.")
        
        valid_df = self.parsed_df[self.parsed_df['is_valid'] == True].copy()
        logger.info(f"Filtered to {len(valid_df)} valid products")
        return valid_df
    
    def get_products_by_brand(self, brand: str) -> pd.DataFrame:
        """Get products for specific brand"""
        if self.parsed_df is None:
            raise ValueError("No parsed data. Call parse_file() first.")
        
        brand_upper = brand.upper()
        brand_df = self.parsed_df[
            self.parsed_df['brand'].str.upper() == brand_upper
        ].copy()
        
        logger.info(f"Found {len(brand_df)} products for brand: {brand}")
        return brand_df
    
    def _get_cell_value(self, row: pd.Series, col_idx: int) -> Optional[str]:
        """Get cell value safely"""
        try:
            col_name = f'Unnamed: {col_idx}'
            if col_name in row.index:
                value = row[col_name]
                if pd.notna(value):
                    return str(value).strip()
        except Exception:
            pass
        return None
    
    def _get_numeric_value(self, row: pd.Series, col_idx: int) -> Optional[float]:
        """Get numeric value safely"""
        value = self._get_cell_value(row, col_idx)
        if value:
            try:
                # Remove any non-numeric characters except dot and comma
                cleaned = re.sub(r'[^\d.,]', '', value)
                # Replace comma with dot
                cleaned = cleaned.replace(',', '.')
                return float(cleaned)
            except (ValueError, TypeError):
                pass
        return None
    
    def _extract_brand(self, name: str) -> Optional[str]:
        """
        Extract brand from product name
        
        Examples:
        - "Delonghi ECAM 290.61.B" -> "DeLonghi"
        - "Melitta Solo & Perfect Milk" -> "Melitta"
        """
        name_upper = name.upper()
        
        # Check each valid brand
        for brand in self.VALID_BRANDS:
            if brand in name_upper:
                # Return standardized brand name
                if 'DELONGHI' in brand or 'DE LONGHI' in brand:
                    return 'DeLonghi'
                elif 'MELITTA' in brand or 'MELITA' in brand:
                    return 'Melitta'
                elif 'NIVONA' in brand:
                    return 'Nivona'
                elif 'JURA' in brand:
                    return 'Jura'
                elif 'SAECO' in brand:
                    return 'Saeco'
                elif 'GAGGIA' in brand:
                    return 'Gaggia'
        
        return None
    
    def _extract_model(self, name: str) -> Optional[str]:
        """
        Extract model code from product name using ModelExtractor
        
        Examples:
        - "Delonghi ECAM 290.61.B" -> "ECAM290.61.B"
        - "Delonghi ECAM290.42.TB" -> "ECAM290.42.TB"
        """
        try:
            model = ModelExtractor.extract_model(name)
            if model:
                return model
            
            # Fallback: Try to extract from name manually
            # Pattern: word with numbers and dots/dashes
            match = re.search(r'\b([A-Z]{2,}\s*\d+[\d\.\s]*[A-Z]*)\b', name.upper())
            if match:
                potential_model = match.group(1).strip()
                # Clean up spaces
                potential_model = re.sub(r'\s+', '', potential_model)
                if len(potential_model) >= 5:
                    return potential_model
            
        except Exception as e:
            logger.debug(f"Error extracting model from '{name}': {e}")
        
        return None
    
    def _categorize_product(self, name: str) -> str:
        """
        Categorize product as: product, spare_part, or accessory
        
        Args:
            name: Product name
            
        Returns:
            Category string
        """
        name_upper = name.upper()
        
        # Check for spare parts
        for keyword in self.SPARE_PARTS_KEYWORDS:
            if keyword in name_upper:
                return 'spare_part'
        
        # Check for accessories
        for keyword in self.ACCESSORIES_KEYWORDS:
            if keyword in name_upper:
                return 'accessory'
        
        return 'product'
    
    def _is_valid_product(
        self, 
        name: str, 
        brand: Optional[str], 
        model: Optional[str], 
        category: str,
        price: float
    ) -> bool:
        """
        Determine if this is a valid product for price comparison
        
        Criteria:
        - Must be category 'product' (not spare part or accessory)
        - Must have a brand
        - Must have a price > 50 (coffee machines are expensive)
        - Preferably has a model (but not required for some products)
        
        Args:
            name: Product name
            brand: Extracted brand
            model: Extracted model
            category: Product category
            price: Product price
            
        Returns:
            True if valid product
        """
        # Must be a product (not spare part or accessory)
        if category != 'product':
            return False
        
        # Must have a brand
        if not brand:
            return False
        
        # Must have reasonable price (coffee machines > 50 GEL)
        if price < 50:
            return False
        
        # Additional checks for name quality
        name_upper = name.upper()
        
        # Exclude if contains spare part indicators
        spare_indicators = ['SPARE', 'PART', 'REPLACEMENT', 'REPAIR']
        if any(ind in name_upper for ind in spare_indicators):
            return False
        
        # Exclude very short names (likely incomplete data)
        if len(name) < 10:
            return False
        
        return True
    
    def _log_stats(self):
        """Log parsing statistics"""
        logger.info("="*60)
        logger.info("INVENTORY PARSING STATISTICS")
        logger.info("="*60)
        logger.info(f"Total rows processed: {self.stats['total_rows']}")
        logger.info(f"Valid products: {self.stats['valid_products']}")
        logger.info(f"Spare parts: {self.stats['spare_parts']}")
        logger.info(f"Accessories: {self.stats['accessories']}")
        logger.info(f"Products without brand: {self.stats['no_brand']}")
        logger.info(f"Products without model: {self.stats['no_model']}")
        logger.info("="*60)
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate detailed parsing report
        
        Args:
            output_path: Optional path to save report
            
        Returns:
            Report as string
        """
        if self.parsed_df is None:
            return "No data parsed yet."
        
        lines = []
        lines.append("="*80)
        lines.append("INVENTORY PARSING REPORT")
        lines.append("="*80)
        lines.append("")
        
        # Overall stats
        lines.append("OVERALL STATISTICS:")
        lines.append(f"  Total rows in file: {self.stats['total_rows']}")
        lines.append(f"  Total products parsed: {len(self.parsed_df)}")
        lines.append(f"  Valid products: {self.stats['valid_products']}")
        lines.append(f"  Spare parts: {self.stats['spare_parts']}")
        lines.append(f"  Accessories: {self.stats['accessories']}")
        lines.append("")
        
        # Brand breakdown
        lines.append("PRODUCTS BY BRAND:")
        brand_counts = self.parsed_df['brand'].value_counts()
        for brand, count in brand_counts.items():
            if pd.notna(brand):
                valid_count = len(self.parsed_df[
                    (self.parsed_df['brand'] == brand) & 
                    (self.parsed_df['is_valid'] == True)
                ])
                lines.append(f"  {brand}: {count} total, {valid_count} valid")
        lines.append("")
        
        # Category breakdown
        lines.append("PRODUCTS BY CATEGORY:")
        category_counts = self.parsed_df['category'].value_counts()
        for category, count in category_counts.items():
            lines.append(f"  {category}: {count}")
        lines.append("")
        
        # Model extraction success
        with_model = len(self.parsed_df[self.parsed_df['model'].notna()])
        without_model = len(self.parsed_df[self.parsed_df['model'].isna()])
        lines.append("MODEL EXTRACTION:")
        lines.append(f"  With model: {with_model} ({with_model/len(self.parsed_df)*100:.1f}%)")
        lines.append(f"  Without model: {without_model} ({without_model/len(self.parsed_df)*100:.1f}%)")
        lines.append("")
        
        # Sample valid products
        lines.append("SAMPLE VALID PRODUCTS (first 10):")
        valid_products = self.parsed_df[self.parsed_df['is_valid'] == True].head(10)
        for idx, row in valid_products.iterrows():
            lines.append(f"  - {row['name'][:60]}")
            lines.append(f"    Brand: {row['brand']}, Model: {row['model']}, Price: {row['price']:.2f}")
        lines.append("")
        
        # Products without models
        lines.append("PRODUCTS WITHOUT MODELS (first 10):")
        no_model = self.parsed_df[
            (self.parsed_df['model'].isna()) & 
            (self.parsed_df['is_valid'] == True)
        ].head(10)
        for idx, row in no_model.iterrows():
            lines.append(f"  - {row['name'][:70]}")
        
        lines.append("")
        lines.append("="*80)
        
        report = "\n".join(lines)
        
        # Save if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_path}")
        
        return report


def main():
    """Test the parser"""
    parser = InventoryParser()
    
    # Parse file
    df = parser.parse_file('data/inbox/остатки.xls')
    
    # Get valid products
    valid_df = parser.get_valid_products()
    
    # Generate report
    report = parser.generate_report('data/output/inventory_parsing_report.txt')
    print(report)
    
    # Save parsed data
    df.to_excel('data/output/inventory_parsed.xlsx', index=False)
    valid_df.to_excel('data/output/inventory_valid_products.xlsx', index=False)
    
    logger.info("Done!")


if __name__ == "__main__":
    main()

