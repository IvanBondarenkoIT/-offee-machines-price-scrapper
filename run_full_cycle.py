"""
Full cycle: Scrape all competitors → Build price comparison → Show results
This script runs the complete workflow for price monitoring
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

class FullCycleRunner:
    """Run complete price monitoring cycle"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.start_time = datetime.now()
        self.results = {}
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*80)
        print(text)
        print("="*80)
    
    def print_step(self, step_num, total_steps, text):
        """Print step info"""
        print(f"\n[STEP {step_num}/{total_steps}] {text}")
        print("-"*80)
    
    def run_scraper(self, scraper_name, scraper_path, expected_products):
        """Run a single scraper"""
        print(f"\nRunning {scraper_name} scraper...")
        print(f"Expected products: {expected_products}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(scraper_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                cwd=str(self.base_dir)  # Set working directory
            )
            
            if result.returncode == 0:
                # Parse output to find product count
                output = result.stdout
                if "products scraped successfully" in output.lower():
                    # Extract number
                    for line in output.split('\n'):
                        if 'products scraped' in line.lower():
                            print(f"  {line.strip()}")
                
                print(f"  [OK] {scraper_name} completed successfully")
                return True
            else:
                print(f"  [ERROR] {scraper_name} failed")
                print(f"  Error: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  [ERROR] {scraper_name} timed out (>5 min)")
            return False
        except Exception as e:
            print(f"  [ERROR] {scraper_name} error: {e}")
            return False
    
    def run_all_scrapers(self):
        """Run all scrapers sequentially"""
        self.print_step(1, 4, "SCRAPING ALL COMPETITORS")
        
        scrapers = [
            {
                'name': 'ALTA',
                'path': self.base_dir / 'scrapers' / 'alta' / 'alta_bs4_scraper.py',
                'expected': 74
            },
            {
                'name': 'KONTAKT',
                'path': self.base_dir / 'scrapers' / 'kontakt' / 'kontakt_bs4_scraper.py',
                'expected': 28
            },
            {
                'name': 'ELITE',
                'path': self.base_dir / 'scrapers' / 'elite' / 'elite_bs4_scraper.py',
                'expected': 40
            },
            {
                'name': 'DIM_KAVA',
                'path': self.base_dir / 'scrapers' / 'dimkava' / 'dimkava_bs4_scraper.py',
                'expected': 41
            }
        ]
        
        success_count = 0
        failed = []
        
        for scraper in scrapers:
            if scraper['path'].exists():
                if self.run_scraper(scraper['name'], scraper['path'], scraper['expected']):
                    success_count += 1
                    self.results[scraper['name']] = 'SUCCESS'
                else:
                    failed.append(scraper['name'])
                    self.results[scraper['name']] = 'FAILED'
            else:
                print(f"\n[WARNING] {scraper['name']} scraper not found: {scraper['path']}")
                self.results[scraper['name']] = 'NOT_FOUND'
        
        print(f"\n{'='*80}")
        print(f"SCRAPING SUMMARY: {success_count}/{len(scrapers)} successful")
        if failed:
            print(f"Failed: {', '.join(failed)}")
        print(f"{'='*80}")
        
        return success_count == len(scrapers)
    
    def verify_scraped_data(self):
        """Verify that scraped data files exist"""
        self.print_step(2, 4, "VERIFYING SCRAPED DATA")
        
        output_dir = self.base_dir / 'data' / 'output'
        
        patterns = {
            'ALTA': 'alta_*_prices_*.xlsx',
            'KONTAKT': 'kontakt_*_prices_*.xlsx',
            'ELITE': 'elite_*_prices_*.xlsx',
            'DIM_KAVA': 'dimkava_*_prices_*.xlsx',
        }
        
        all_found = True
        
        for source, pattern in patterns.items():
            files = list(output_dir.glob(pattern))
            if files:
                latest = max(files, key=lambda x: x.stat().st_mtime)
                df = pd.read_excel(latest)
                print(f"  [OK] {source:10s}: {len(df):3d} products in {latest.name}")
                self.results[f'{source}_products'] = len(df)
            else:
                print(f"  [ERROR] {source:10s}: No data files found")
                all_found = False
        
        return all_found
    
    def build_price_comparison(self):
        """Build price comparison table"""
        self.print_step(3, 4, "BUILDING PRICE COMPARISON")
        
        try:
            result = subprocess.run(
                [sys.executable, 'build_price_comparison.py'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.base_dir)  # Set working directory
            )
            
            if result.returncode == 0:
                output = result.stdout
                print(output)
                
                # Extract matched count
                for line in output.split('\n'):
                    if 'Products compared:' in line:
                        try:
                            count = int(line.split(':')[1].strip())
                            self.results['matched_products'] = count
                        except:
                            pass
                
                return True
            else:
                print(f"[ERROR] Price comparison failed")
                print(result.stderr[:500])
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    def show_final_results(self):
        """Show final comparison results"""
        self.print_step(4, 4, "FINAL RESULTS")
        
        # Find latest comparison file
        output_dir = self.base_dir / 'data' / 'output'
        comparison_files = list(output_dir.glob('price_comparison_*.xlsx'))
        
        if not comparison_files:
            print("[ERROR] No comparison file found")
            return False
        
        latest_file = max(comparison_files, key=lambda x: x.stat().st_mtime)
        
        print(f"\nComparison file: {latest_file.name}")
        print("-"*80)
        
        # Load and show summary
        df = pd.read_excel(latest_file, sheet_name='Price Comparison')
        stats = pd.read_excel(latest_file, sheet_name='Statistics')
        
        print(f"\nTOTAL PRODUCTS COMPARED: {len(df)}")
        print(f"Total quantity: {df['Quantity'].sum()}")
        print(f"Total value: {(df['Quantity'] * df['Our Price']).sum():,.2f} GEL")
        
        # Show top 10 products
        print("\nTOP 10 PRODUCTS BY QUANTITY:")
        print("-"*80)
        top10 = df.nlargest(10, 'Quantity')[['Quantity', 'Model', 'Our Price', 'DIM_KAVA', 'ALTA', 'KONTAKT', 'ELITE']]
        print(top10.to_string(index=False))
        
        # Show statistics
        print("\n" + "="*80)
        print("STATISTICS:")
        print("="*80)
        print(stats.T.to_string())
        
        # Price analysis
        print("\n" + "="*80)
        print("PRICE COMPETITIVENESS:")
        print("="*80)
        
        # Count where we have competitors
        competitor_cols = ['DIM_KAVA', 'ALTA', 'KONTAKT', 'ELITE']
        for col in competitor_cols:
            has_price = df[col] != '-'
            if has_price.sum() > 0:
                print(f"{col:10s}: {has_price.sum():2d} products with prices")
        
        return True
    
    def run(self):
        """Run complete cycle"""
        self.print_header("FULL PRICE MONITORING CYCLE")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Scrape all competitors
        if not self.run_all_scrapers():
            print("\n[WARNING] Some scrapers failed, but continuing...")
        
        # Step 2: Verify data
        if not self.verify_scraped_data():
            print("\n[ERROR] Data verification failed")
            return False
        
        # Step 3: Build comparison
        if not self.build_price_comparison():
            print("\n[ERROR] Price comparison failed")
            return False
        
        # Step 4: Show results
        if not self.show_final_results():
            print("\n[ERROR] Failed to show results")
            return False
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.print_header("CYCLE COMPLETE")
        print(f"Started:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        
        print("\nRESULTS SUMMARY:")
        print("-"*80)
        for key, value in self.results.items():
            print(f"  {key:25s}: {value}")
        
        print("\n" + "="*80)
        print("SUCCESS! All steps completed.")
        print("="*80)
        
        return True


if __name__ == "__main__":
    runner = FullCycleRunner()
    success = runner.run()
    
    sys.exit(0 if success else 1)

