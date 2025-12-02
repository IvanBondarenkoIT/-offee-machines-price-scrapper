"""
Enhanced Product Matcher - Multiple strategies for matching inventory with scraped data
"""

import pandas as pd
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.model_extractor import ModelExtractor

logger = setup_logger("enhanced_matcher")


class EnhancedMatcher:
    """
    Enhanced product matcher with multiple strategies
    
    Strategies (in order):
    1. Exact model match (confidence: 1.0)
    2. Fuzzy model match - color variants (confidence: 0.9)
    3. Manual synonyms from CSV (confidence: as specified)
    4. Name-based fuzzy match (confidence: 0.6-0.8)
    """
    
    def __init__(self, inventory_df: pd.DataFrame, scraped_df: pd.DataFrame):
        """
        Initialize matcher
        
        Args:
            inventory_df: DataFrame from InventoryParser
            scraped_df: DataFrame from scrapers (Dim Kava, etc.)
        """
        self.inventory = inventory_df.copy()
        self.scraped = scraped_df.copy()
        self.matches = []
        self.unmatched_inventory = []
        self.unmatched_scraped = []
        self.manual_synonyms = self._load_manual_synonyms()
        
        # Statistics
        self.stats = {
            'exact_matches': 0,
            'fuzzy_matches': 0,
            'synonym_matches': 0,
            'name_matches': 0,
            'total_matches': 0,
        }
    
    def _load_manual_synonyms(self) -> Dict[str, Dict]:
        """Load manual synonyms from CSV"""
        synonyms = {}
        csv_path = Path('config/model_synonyms.csv')
        
        if not csv_path.exists():
            logger.warning(f"Manual synonyms file not found: {csv_path}")
            return synonyms
        
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                inv_model = row['inventory_model']
                scr_model = row['scraped_model']
                
                # Normalize both
                inv_norm = ModelExtractor.normalize_for_matching(inv_model)
                scr_norm = ModelExtractor.normalize_for_matching(scr_model)
                
                synonyms[scr_norm] = {
                    'inventory_normalized': inv_norm,
                    'confidence': row.get('confidence', 1.0),
                    'notes': row.get('notes', ''),
                }
            
            logger.info(f"Loaded {len(synonyms)} manual synonyms")
        except Exception as e:
            logger.error(f"Error loading manual synonyms: {e}")
        
        return synonyms
    
    def match_products(self) -> pd.DataFrame:
        """
        Match products using all strategies
        
        Returns:
            DataFrame with matched products
        """
        logger.info("="*60)
        logger.info("Starting enhanced product matching...")
        logger.info("="*60)
        logger.info(f"Inventory products: {len(self.inventory)}")
        logger.info(f"Scraped products: {len(self.scraped)}")
        logger.info("")
        
        # Create indices for faster lookup
        self._create_indices()
        
        # Strategy 1: Exact model match
        self._match_exact_models()
        
        # Strategy 2: Fuzzy model match (color variants)
        self._match_fuzzy_models()
        
        # Strategy 3: Manual synonyms
        self._match_by_synonyms()
        
        # Strategy 4: Name-based matching (for products without models)
        self._match_by_name()
        
        # Build result DataFrame
        result_df = self._build_result_dataframe()
        
        # Log statistics
        self._log_statistics()
        
        return result_df
    
    def _create_indices(self):
        """Create normalized model indices for faster lookup"""
        # Index for inventory
        self.inv_model_index = {}
        for idx, row in self.inventory.iterrows():
            if pd.notna(row.get('model')):
                norm_model = ModelExtractor.normalize_for_matching(row['model'])
                if norm_model not in self.inv_model_index:
                    self.inv_model_index[norm_model] = []
                self.inv_model_index[norm_model].append(idx)
        
        # Index for scraped
        self.scr_model_index = {}
        for idx, row in self.scraped.iterrows():
            if pd.notna(row.get('model')):
                norm_model = ModelExtractor.normalize_for_matching(row['model'])
                if norm_model not in self.scr_model_index:
                    self.scr_model_index[norm_model] = []
                self.scr_model_index[norm_model].append(idx)
        
        logger.info(f"Created indices: {len(self.inv_model_index)} inventory, {len(self.scr_model_index)} scraped")
    
    def _match_exact_models(self):
        """Strategy 1: Exact model matching"""
        logger.info("\nStrategy 1: Exact model matching...")
        
        matched_inv_idx = set()
        matched_scr_idx = set()
        
        for norm_model, inv_indices in self.inv_model_index.items():
            if norm_model in self.scr_model_index:
                scr_indices = self.scr_model_index[norm_model]
                
                # Match first available pair
                for inv_idx in inv_indices:
                    if inv_idx in matched_inv_idx:
                        continue
                    
                    for scr_idx in scr_indices:
                        if scr_idx in matched_scr_idx:
                            continue
                        
                        # Found a match!
                        inv_row = self.inventory.loc[inv_idx]
                        scr_row = self.scraped.loc[scr_idx]
                        
                        self.matches.append({
                            'inventory_idx': inv_idx,
                            'scraped_idx': scr_idx,
                            'inventory_name': inv_row['name'],
                            'scraped_name': scr_row['name'],
                            'inventory_model': inv_row['model'],
                            'scraped_model': scr_row['model'],
                            'inventory_price': inv_row['price'],
                            'scraped_price': scr_row.get('final_price', scr_row.get('price')),
                            'match_type': 'exact_model',
                            'confidence': 1.0,
                            'normalized_model': norm_model,
                        })
                        
                        matched_inv_idx.add(inv_idx)
                        matched_scr_idx.add(scr_idx)
                        self.stats['exact_matches'] += 1
                        
                        logger.debug(f"  MATCH: {inv_row['model']} <-> {scr_row['model']}")
                        break
        
        logger.info(f"  Found {self.stats['exact_matches']} exact matches")
    
    def _match_fuzzy_models(self):
        """Strategy 2: Fuzzy model matching (color variants)"""
        logger.info("\nStrategy 2: Fuzzy model matching (color variants)...")
        
        # Get already matched indices
        matched_inv_idx = {m['inventory_idx'] for m in self.matches}
        matched_scr_idx = {m['scraped_idx'] for m in self.matches}
        
        # Try fuzzy matching for unmatched products
        for inv_idx, inv_row in self.inventory.iterrows():
            if inv_idx in matched_inv_idx:
                continue
            
            if pd.isna(inv_row.get('model')):
                continue
            
            inv_model = inv_row['model']
            
            for scr_idx, scr_row in self.scraped.iterrows():
                if scr_idx in matched_scr_idx:
                    continue
                
                if pd.isna(scr_row.get('model')):
                    continue
                
                scr_model = scr_row['model']
                
                # Try fuzzy match
                is_match, confidence = ModelExtractor.match_models_fuzzy(inv_model, scr_model)
                
                if is_match and confidence >= 0.9:  # Only high-confidence fuzzy matches
                    self.matches.append({
                        'inventory_idx': inv_idx,
                        'scraped_idx': scr_idx,
                        'inventory_name': inv_row['name'],
                        'scraped_name': scr_row['name'],
                        'inventory_model': inv_model,
                        'scraped_model': scr_model,
                        'inventory_price': inv_row['price'],
                        'scraped_price': scr_row.get('final_price', scr_row.get('price')),
                        'match_type': 'fuzzy_model',
                        'confidence': confidence,
                        'normalized_model': ModelExtractor.normalize_for_matching(inv_model),
                    })
                    
                    matched_inv_idx.add(inv_idx)
                    matched_scr_idx.add(scr_idx)
                    self.stats['fuzzy_matches'] += 1
                    
                    logger.debug(f"  FUZZY MATCH ({confidence:.1f}): {inv_model} <-> {scr_model}")
                    break
        
        logger.info(f"  Found {self.stats['fuzzy_matches']} fuzzy matches")
    
    def _match_by_synonyms(self):
        """Strategy 3: Manual synonym matching"""
        logger.info("\nStrategy 3: Manual synonym matching...")
        
        if not self.manual_synonyms:
            logger.info("  No manual synonyms loaded, skipping")
            return
        
        # Get already matched indices
        matched_inv_idx = {m['inventory_idx'] for m in self.matches}
        matched_scr_idx = {m['scraped_idx'] for m in self.matches}
        
        for scr_idx, scr_row in self.scraped.iterrows():
            if scr_idx in matched_scr_idx:
                continue
            
            if pd.isna(scr_row.get('model')):
                continue
            
            scr_norm = ModelExtractor.normalize_for_matching(scr_row['model'])
            
            if scr_norm in self.manual_synonyms:
                synonym_info = self.manual_synonyms[scr_norm]
                inv_norm = synonym_info['inventory_normalized']
                
                # Find inventory product with this normalized model
                if inv_norm in self.inv_model_index:
                    for inv_idx in self.inv_model_index[inv_norm]:
                        if inv_idx not in matched_inv_idx:
                            inv_row = self.inventory.loc[inv_idx]
                            
                            self.matches.append({
                                'inventory_idx': inv_idx,
                                'scraped_idx': scr_idx,
                                'inventory_name': inv_row['name'],
                                'scraped_name': scr_row['name'],
                                'inventory_model': inv_row['model'],
                                'scraped_model': scr_row['model'],
                                'inventory_price': inv_row['price'],
                                'scraped_price': scr_row.get('final_price', scr_row.get('price')),
                                'match_type': 'manual_synonym',
                                'confidence': synonym_info['confidence'],
                                'normalized_model': inv_norm,
                            })
                            
                            matched_inv_idx.add(inv_idx)
                            matched_scr_idx.add(scr_idx)
                            self.stats['synonym_matches'] += 1
                            
                            logger.debug(f"  SYNONYM MATCH: {inv_row['model']} <-> {scr_row['model']}")
                            break
        
        logger.info(f"  Found {self.stats['synonym_matches']} synonym matches")
    
    def _match_by_name(self):
        """Strategy 4: Name-based matching (for products without models)"""
        logger.info("\nStrategy 4: Name-based matching...")
        logger.info("  (Skipping for now - requires more sophisticated fuzzy string matching)")
        # TODO: Implement name-based matching using fuzzy string matching
        # This is lower priority as most products have models
    
    def _build_result_dataframe(self) -> pd.DataFrame:
        """Build result DataFrame from matches"""
        if not self.matches:
            logger.warning("No matches found!")
            return pd.DataFrame()
        
        df = pd.DataFrame(self.matches)
        
        # Calculate price difference
        df['price_diff'] = df['scraped_price'] - df['inventory_price']
        df['price_diff_pct'] = (df['price_diff'] / df['inventory_price'] * 100).round(2)
        
        # Sort by confidence (highest first)
        df = df.sort_values('confidence', ascending=False)
        
        self.stats['total_matches'] = len(df)
        
        return df
    
    def _log_statistics(self):
        """Log matching statistics"""
        logger.info("")
        logger.info("="*60)
        logger.info("MATCHING STATISTICS")
        logger.info("="*60)
        logger.info(f"Total matches: {self.stats['total_matches']}")
        logger.info(f"  - Exact model matches: {self.stats['exact_matches']}")
        logger.info(f"  - Fuzzy model matches: {self.stats['fuzzy_matches']}")
        logger.info(f"  - Manual synonym matches: {self.stats['synonym_matches']}")
        logger.info(f"  - Name-based matches: {self.stats['name_matches']}")
        logger.info("")
        logger.info(f"Match rate: {self.stats['total_matches']/len(self.inventory)*100:.1f}%")
        logger.info("="*60)
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate detailed matching report"""
        lines = []
        lines.append("="*80)
        lines.append("PRODUCT MATCHING REPORT")
        lines.append("="*80)
        lines.append("")
        
        # Overall stats
        lines.append("OVERALL STATISTICS:")
        lines.append(f"  Inventory products: {len(self.inventory)}")
        lines.append(f"  Scraped products: {len(self.scraped)}")
        lines.append(f"  Total matches: {self.stats['total_matches']}")
        lines.append(f"  Match rate: {self.stats['total_matches']/len(self.inventory)*100:.1f}%")
        lines.append("")
        
        # Match breakdown
        lines.append("MATCH BREAKDOWN:")
        lines.append(f"  Exact model matches: {self.stats['exact_matches']}")
        lines.append(f"  Fuzzy model matches: {self.stats['fuzzy_matches']}")
        lines.append(f"  Manual synonym matches: {self.stats['synonym_matches']}")
        lines.append(f"  Name-based matches: {self.stats['name_matches']}")
        lines.append("")
        
        # Sample matches
        if self.matches:
            lines.append("SAMPLE MATCHES (first 10):")
            for i, match in enumerate(self.matches[:10], 1):
                lines.append(f"\n{i}. {match['match_type'].upper()} (confidence: {match['confidence']:.2f})")
                lines.append(f"   Inventory: {match['inventory_name'][:60]}")
                lines.append(f"              Model: {match['inventory_model']}, Price: {match['inventory_price']:.2f}")
                lines.append(f"   Scraped:   {match['scraped_name'][:60]}")
                lines.append(f"              Model: {match['scraped_model']}, Price: {match['scraped_price']:.2f}")
                lines.append(f"   Price diff: {match.get('price_diff', 0):+.2f} GEL ({match.get('price_diff_pct', 0):+.1f}%)")
        
        lines.append("")
        lines.append("="*80)
        
        report = "\n".join(lines)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_path}")
        
        return report


def main():
    """Test the enhanced matcher"""
    from utils.inventory_parser import InventoryParser
    
    # Load inventory
    logger.info("Loading inventory...")
    parser = InventoryParser()
    inv_df = parser.parse_file('data/inbox/остатки.xls')
    valid_inv = parser.get_valid_products()
    
    # Load Dim Kava scraped data
    logger.info("Loading Dim Kava data...")
    dimkava_df = pd.read_excel('data/output/dimkava_delonghi_prices_20251201_101126.xlsx')
    
    # Match
    logger.info("Matching products...")
    matcher = EnhancedMatcher(valid_inv, dimkava_df)
    matched_df = matcher.match_products()
    
    # Generate report
    report = matcher.generate_report('data/output/enhanced_matching_report.txt')
    print(report)
    
    # Save results
    matched_df.to_excel('data/output/enhanced_matched_products.xlsx', index=False)
    
    logger.info("Done!")


if __name__ == "__main__":
    main()

