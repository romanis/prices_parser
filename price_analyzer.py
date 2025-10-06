"""
Price analyzer and summarizer for retail competitor data.
"""

import os
import json
import logging
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

import pandas as pd

import config


class PriceAnalyzer:
    """Analyze and summarize product prices from competitors."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.logger = logging.getLogger(__name__)
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(config.OUTPUT_DIR):
            os.makedirs(config.OUTPUT_DIR)
            self.logger.info(f"Created output directory: {config.OUTPUT_DIR}")
    
    def analyze_products(self, products: List[Dict], competitor_name: str = '5ka') -> Dict:
        """
        Analyze product prices and generate summary statistics.
        
        Args:
            products: List of product dictionaries
            competitor_name: Name of the competitor
            
        Returns:
            Dictionary with analysis results
        """
        if not products:
            self.logger.warning("No products to analyze")
            return {}
        
        df = pd.DataFrame(products)
        
        # Basic statistics
        analysis = {
            'competitor': competitor_name,
            'timestamp': datetime.now().isoformat(),
            'total_products': len(products),
            'price_statistics': {},
            'categories': {},
            'discounts': {}
        }
        
        # Price statistics
        if 'price' in df.columns:
            analysis['price_statistics'] = {
                'average_price': float(df['price'].mean()),
                'median_price': float(df['price'].median()),
                'min_price': float(df['price'].min()),
                'max_price': float(df['price'].max()),
                'std_deviation': float(df['price'].std())
            }
        
        # Discount analysis
        if 'old_price' in df.columns and 'price' in df.columns:
            discounted = df[df['old_price'].notna()]
            if len(discounted) > 0:
                discounted['discount_amount'] = discounted['old_price'] - discounted['price']
                discounted['discount_percent'] = (
                    (discounted['old_price'] - discounted['price']) / discounted['old_price'] * 100
                )
                
                analysis['discounts'] = {
                    'products_with_discount': len(discounted),
                    'discount_percentage': float(len(discounted) / len(df) * 100),
                    'average_discount_amount': float(discounted['discount_amount'].mean()),
                    'average_discount_percent': float(discounted['discount_percent'].mean()),
                    'max_discount_percent': float(discounted['discount_percent'].max())
                }
        
        # Price distribution
        if 'price' in df.columns:
            price_ranges = {
                '0-100': len(df[df['price'] < 100]),
                '100-300': len(df[(df['price'] >= 100) & (df['price'] < 300)]),
                '300-500': len(df[(df['price'] >= 300) & (df['price'] < 500)]),
                '500-1000': len(df[(df['price'] >= 500) & (df['price'] < 1000)]),
                '1000+': len(df[df['price'] >= 1000])
            }
            analysis['price_distribution'] = price_ranges
        
        return analysis
    
    def generate_summary_report(self, analysis: Dict) -> str:
        """
        Generate a human-readable summary report.
        
        Args:
            analysis: Analysis dictionary
            
        Returns:
            Formatted summary text
        """
        report_lines = [
            "=" * 70,
            f"PRICE ANALYSIS REPORT - {analysis.get('competitor', 'Unknown')}",
            f"Generated: {analysis.get('timestamp', 'N/A')}",
            "=" * 70,
            "",
            f"Total Products Analyzed: {analysis.get('total_products', 0)}",
            ""
        ]
        
        # Price statistics
        if 'price_statistics' in analysis:
            stats = analysis['price_statistics']
            report_lines.extend([
                "PRICE STATISTICS:",
                "-" * 40,
                f"  Average Price:     {stats.get('average_price', 0):.2f} ₽",
                f"  Median Price:      {stats.get('median_price', 0):.2f} ₽",
                f"  Min Price:         {stats.get('min_price', 0):.2f} ₽",
                f"  Max Price:         {stats.get('max_price', 0):.2f} ₽",
                f"  Std Deviation:     {stats.get('std_deviation', 0):.2f} ₽",
                ""
            ])
        
        # Discount information
        if 'discounts' in analysis and analysis['discounts']:
            disc = analysis['discounts']
            report_lines.extend([
                "DISCOUNT ANALYSIS:",
                "-" * 40,
                f"  Products on Sale:        {disc.get('products_with_discount', 0)}",
                f"  Percentage of Products:  {disc.get('discount_percentage', 0):.1f}%",
                f"  Avg Discount Amount:     {disc.get('average_discount_amount', 0):.2f} ₽",
                f"  Avg Discount Percent:    {disc.get('average_discount_percent', 0):.1f}%",
                f"  Max Discount Percent:    {disc.get('max_discount_percent', 0):.1f}%",
                ""
            ])
        
        # Price distribution
        if 'price_distribution' in analysis:
            dist = analysis['price_distribution']
            report_lines.extend([
                "PRICE DISTRIBUTION:",
                "-" * 40
            ])
            for range_name, count in dist.items():
                report_lines.append(f"  {range_name:15} : {count:5} products")
            report_lines.append("")
        
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
    
    def save_results(self, products: List[Dict], analysis: Dict, competitor_name: str = '5ka'):
        """
        Save products and analysis to files.
        
        Args:
            products: List of products
            analysis: Analysis dictionary
            competitor_name: Name of the competitor
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{competitor_name}_{timestamp}"
        
        # Save raw products data
        df = pd.DataFrame(products)
        
        if config.OUTPUT_FORMAT == 'csv' or config.OUTPUT_FORMAT == 'all':
            csv_path = os.path.join(config.OUTPUT_DIR, f"{base_filename}_products.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"Saved products to CSV: {csv_path}")
        
        if config.OUTPUT_FORMAT == 'excel' or config.OUTPUT_FORMAT == 'all':
            excel_path = os.path.join(config.OUTPUT_DIR, f"{base_filename}_products.xlsx")
            df.to_excel(excel_path, index=False, engine='openpyxl')
            self.logger.info(f"Saved products to Excel: {excel_path}")
        
        if config.OUTPUT_FORMAT == 'json' or config.OUTPUT_FORMAT == 'all':
            json_path = os.path.join(config.OUTPUT_DIR, f"{base_filename}_products.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved products to JSON: {json_path}")
        
        # Save analysis
        analysis_path = os.path.join(config.OUTPUT_DIR, f"{base_filename}_analysis.json")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Saved analysis to: {analysis_path}")
        
        # Save summary report
        report = self.generate_summary_report(analysis)
        report_path = os.path.join(config.OUTPUT_DIR, f"{base_filename}_summary.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        self.logger.info(f"Saved summary report to: {report_path}")
        
        # Also print to console
        print("\n" + report)
    
    def find_best_deals(self, products: List[Dict], top_n: int = 10) -> List[Dict]:
        """
        Find products with the best discounts.
        
        Args:
            products: List of products
            top_n: Number of top deals to return
            
        Returns:
            List of top deals
        """
        discounted = [p for p in products if 'old_price' in p and p.get('old_price')]
        
        for product in discounted:
            product['discount_percent'] = (
                (product['old_price'] - product['price']) / product['old_price'] * 100
            )
            product['savings'] = product['old_price'] - product['price']
        
        # Sort by discount percentage
        sorted_deals = sorted(discounted, key=lambda x: x['discount_percent'], reverse=True)
        
        return sorted_deals[:top_n]
    
    def compare_product_categories(self, products: List[Dict]) -> Dict:
        """
        Group and analyze products by category.
        
        Args:
            products: List of products
            
        Returns:
            Dictionary with category analysis
        """
        # This is a placeholder - actual categorization would need
        # product category data from the scraper
        categories = defaultdict(list)
        
        for product in products:
            # Simple keyword-based categorization
            name = product.get('name', '').lower()
            category = 'Other'
            
            # Basic category detection
            if any(word in name for word in ['молоко', 'сыр', 'йогурт', 'творог']):
                category = 'Dairy'
            elif any(word in name for word in ['хлеб', 'батон', 'булка']):
                category = 'Bakery'
            elif any(word in name for word in ['мясо', 'курица', 'колбаса']):
                category = 'Meat'
            elif any(word in name for word in ['овощ', 'фрукт', 'яблок', 'банан']):
                category = 'Produce'
            
            categories[category].append(product)
        
        # Analyze each category
        category_analysis = {}
        for cat_name, cat_products in categories.items():
            if cat_products:
                prices = [p['price'] for p in cat_products if 'price' in p]
                if prices:
                    category_analysis[cat_name] = {
                        'count': len(cat_products),
                        'avg_price': sum(prices) / len(prices),
                        'min_price': min(prices),
                        'max_price': max(prices)
                    }
        
        return category_analysis

