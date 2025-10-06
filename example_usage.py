#!/usr/bin/env python3
"""
Example usage of the retail price scraper.
This demonstrates how to use the scraper programmatically.
"""

from scraper import RetailScraper
from price_analyzer import PriceAnalyzer
import config


def example_basic_scraping():
    """Basic example: Scrape and analyze 5ka.ru."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Scraping")
    print("=" * 70)
    
    # Initialize scraper
    scraper = RetailScraper(use_cloudscraper=True)
    
    # Scrape products (only 2 pages for this example)
    print("\nScraping 5ka.ru (2 pages)...")
    products = scraper.scrape_5ka_catalog(max_pages=2)
    
    # Close scraper
    scraper.close()
    
    if products:
        print(f"✓ Scraped {len(products)} products")
        
        # Analyze
        analyzer = PriceAnalyzer()
        analysis = analyzer.analyze_products(products, '5ka')
        
        # Save results
        analyzer.save_results(products, analysis, '5ka')
        print("✓ Results saved to output/ directory")
    else:
        print("⚠ No products found")


def example_find_best_deals():
    """Example: Find best deals."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Finding Best Deals")
    print("=" * 70)
    
    scraper = RetailScraper(use_cloudscraper=True)
    products = scraper.scrape_5ka_catalog(max_pages=2)
    scraper.close()
    
    if products:
        analyzer = PriceAnalyzer()
        
        # Find top 5 deals
        best_deals = analyzer.find_best_deals(products, top_n=5)
        
        print("\n🎯 Top 5 Best Deals:")
        print("-" * 70)
        for i, deal in enumerate(best_deals, 1):
            print(f"\n{i}. {deal.get('name', 'Unknown')}")
            print(f"   Current Price: {deal['price']:.2f} ₽")
            print(f"   Original Price: {deal['old_price']:.2f} ₽")
            print(f"   Discount: {deal['discount_percent']:.1f}% off")
            print(f"   You save: {deal['savings']:.2f} ₽")


def example_price_statistics():
    """Example: Get detailed price statistics."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Price Statistics")
    print("=" * 70)
    
    scraper = RetailScraper(use_cloudscraper=True)
    products = scraper.scrape_5ka_catalog(max_pages=2)
    scraper.close()
    
    if products:
        analyzer = PriceAnalyzer()
        analysis = analyzer.analyze_products(products, '5ka')
        
        stats = analysis.get('price_statistics', {})
        print("\n📊 Price Statistics:")
        print("-" * 70)
        print(f"Total Products:    {analysis.get('total_products', 0)}")
        print(f"Average Price:     {stats.get('average_price', 0):.2f} ₽")
        print(f"Median Price:      {stats.get('median_price', 0):.2f} ₽")
        print(f"Min Price:         {stats.get('min_price', 0):.2f} ₽")
        print(f"Max Price:         {stats.get('max_price', 0):.2f} ₽")
        print(f"Std Deviation:     {stats.get('std_deviation', 0):.2f} ₽")
        
        if 'price_distribution' in analysis:
            print("\n💰 Price Distribution:")
            print("-" * 70)
            for price_range, count in analysis['price_distribution'].items():
                print(f"{price_range:15}: {count:4} products")


def example_category_analysis():
    """Example: Analyze products by category."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Category Analysis")
    print("=" * 70)
    
    scraper = RetailScraper(use_cloudscraper=True)
    products = scraper.scrape_5ka_catalog(max_pages=2)
    scraper.close()
    
    if products:
        analyzer = PriceAnalyzer()
        categories = analyzer.compare_product_categories(products)
        
        print("\n📦 Category Analysis:")
        print("-" * 70)
        for category, stats in categories.items():
            print(f"\n{category}:")
            print(f"  Products:    {stats['count']}")
            print(f"  Avg Price:   {stats['avg_price']:.2f} ₽")
            print(f"  Price Range: {stats['min_price']:.2f} - {stats['max_price']:.2f} ₽")


def example_custom_url():
    """Example: Scrape a specific category URL."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Scraping Specific Category")
    print("=" * 70)
    
    # Replace with actual category URL from 5ka.ru
    custom_url = "https://5ka.ru/catalog"  # Change this to actual category
    
    scraper = RetailScraper(use_cloudscraper=True)
    products = scraper.scrape_5ka_catalog(category_url=custom_url, max_pages=1)
    scraper.close()
    
    print(f"\n✓ Scraped {len(products)} products from custom URL")


def example_working_with_data():
    """Example: Working with scraped data programmatically."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Working with Scraped Data")
    print("=" * 70)
    
    scraper = RetailScraper(use_cloudscraper=True)
    products = scraper.scrape_5ka_catalog(max_pages=1)
    scraper.close()
    
    if products:
        # Filter products under 100 rubles
        cheap_products = [p for p in products if p.get('price', 0) < 100]
        print(f"\n💸 Products under 100₽: {len(cheap_products)}")
        
        # Filter products with discounts over 30%
        if any('old_price' in p for p in products):
            big_discounts = []
            for p in products:
                if 'old_price' in p:
                    discount_pct = (p['old_price'] - p['price']) / p['old_price'] * 100
                    if discount_pct > 30:
                        big_discounts.append(p)
            print(f"🔥 Products with >30% discount: {len(big_discounts)}")
        
        # Find products by keyword
        keyword = "молоко"
        matching = [p for p in products if keyword.lower() in p.get('name', '').lower()]
        print(f"🔍 Products matching '{keyword}': {len(matching)}")
        
        # Calculate total value if bought everything
        total_value = sum(p.get('price', 0) for p in products)
        print(f"💰 Total value of all products: {total_value:.2f} ₽")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "RETAIL PRICE SCRAPER EXAMPLES" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print("This script demonstrates various ways to use the scraper.")
    print("Each example is independent and can be run separately.")
    print()
    
    # Run only one example to avoid excessive scraping
    # Uncomment the one you want to try:
    
    example_basic_scraping()
    # example_find_best_deals()
    # example_price_statistics()
    # example_category_analysis()
    # example_custom_url()
    # example_working_with_data()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
    print("\nTip: Edit this file to run different examples.")
    print("Always be respectful of the website's resources!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()

