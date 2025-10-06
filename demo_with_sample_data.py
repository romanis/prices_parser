#!/usr/bin/env python3
"""
Demo script with sample data to show how the analyzer works.
This demonstrates the output format without needing to actually scrape.
"""

from price_analyzer import PriceAnalyzer
import pandas as pd

# Sample product data (realistic examples from Russian retail)
sample_products = [
    {
        "name": "Молоко Простоквашино 3,2% 1л",
        "price": 89.99,
        "old_price": 109.99,
        "price_text": "89,99 ₽",
        "image_url": "https://example.com/milk.jpg",
        "url": "/product/milk-1"
    },
    {
        "name": "Хлеб Бородинский нарезной 400г",
        "price": 45.50,
        "price_text": "45,50 ₽",
        "image_url": "https://example.com/bread.jpg",
        "url": "/product/bread-1"
    },
    {
        "name": "Куриное филе охлажденное 1кг",
        "price": 289.00,
        "old_price": 349.00,
        "price_text": "289,00 ₽",
        "image_url": "https://example.com/chicken.jpg",
        "url": "/product/chicken-1"
    },
    {
        "name": "Яблоки Голден 1кг",
        "price": 129.90,
        "price_text": "129,90 ₽",
        "image_url": "https://example.com/apples.jpg",
        "url": "/product/apples-1"
    },
    {
        "name": "Масло подсолнечное Золотая Семечка 1л",
        "price": 159.99,
        "old_price": 199.99,
        "price_text": "159,99 ₽",
        "image_url": "https://example.com/oil.jpg",
        "url": "/product/oil-1"
    },
    {
        "name": "Сыр Российский 45% 200г",
        "price": 179.00,
        "old_price": 229.00,
        "price_text": "179,00 ₽",
        "image_url": "https://example.com/cheese.jpg",
        "url": "/product/cheese-1"
    },
    {
        "name": "Йогурт Активиа клубника 150г",
        "price": 35.50,
        "price_text": "35,50 ₽",
        "image_url": "https://example.com/yogurt.jpg",
        "url": "/product/yogurt-1"
    },
    {
        "name": "Колбаса вареная Докторская 400г",
        "price": 249.00,
        "old_price": 299.00,
        "price_text": "249,00 ₽",
        "image_url": "https://example.com/sausage.jpg",
        "url": "/product/sausage-1"
    },
    {
        "name": "Бананы 1кг",
        "price": 79.90,
        "price_text": "79,90 ₽",
        "image_url": "https://example.com/bananas.jpg",
        "url": "/product/bananas-1"
    },
    {
        "name": "Творог 9% Простоквашино 200г",
        "price": 89.00,
        "old_price": 109.00,
        "price_text": "89,00 ₽",
        "image_url": "https://example.com/cottage.jpg",
        "url": "/product/cottage-1"
    },
    {
        "name": "Макароны Makfa спагетти 450г",
        "price": 69.90,
        "price_text": "69,90 ₽",
        "image_url": "https://example.com/pasta.jpg",
        "url": "/product/pasta-1"
    },
    {
        "name": "Сметана 20% Домик в деревне 300г",
        "price": 119.00,
        "old_price": 149.00,
        "price_text": "119,00 ₽",
        "image_url": "https://example.com/sour-cream.jpg",
        "url": "/product/sour-cream-1"
    },
    {
        "name": "Яйца куриные С0 10шт",
        "price": 95.00,
        "price_text": "95,00 ₽",
        "image_url": "https://example.com/eggs.jpg",
        "url": "/product/eggs-1"
    },
    {
        "name": "Рис Мистраль длиннозерный 900г",
        "price": 149.00,
        "old_price": 189.00,
        "price_text": "149,00 ₽",
        "image_url": "https://example.com/rice.jpg",
        "url": "/product/rice-1"
    },
    {
        "name": "Сахар-песок 1кг",
        "price": 69.50,
        "price_text": "69,50 ₽",
        "image_url": "https://example.com/sugar.jpg",
        "url": "/product/sugar-1"
    },
    {
        "name": "Гречка ядрица 900г",
        "price": 89.90,
        "old_price": 119.90,
        "price_text": "89,90 ₽",
        "image_url": "https://example.com/buckwheat.jpg",
        "url": "/product/buckwheat-1"
    },
    {
        "name": "Томаты свежие 1кг",
        "price": 199.00,
        "price_text": "199,00 ₽",
        "image_url": "https://example.com/tomatoes.jpg",
        "url": "/product/tomatoes-1"
    },
    {
        "name": "Огурцы свежие 1кг",
        "price": 149.00,
        "price_text": "149,00 ₽",
        "image_url": "https://example.com/cucumbers.jpg",
        "url": "/product/cucumbers-1"
    },
    {
        "name": "Мороженое Пломбир эскимо 80г",
        "price": 45.00,
        "old_price": 59.00,
        "price_text": "45,00 ₽",
        "image_url": "https://example.com/icecream.jpg",
        "url": "/product/icecream-1"
    },
    {
        "name": "Чай Greenfield Earl Grey 25 пак.",
        "price": 139.00,
        "price_text": "139,00 ₽",
        "image_url": "https://example.com/tea.jpg",
        "url": "/product/tea-1"
    },
]


def main():
    """Run demo with sample data."""
    print("\n" + "=" * 70)
    print("DEMO: PRICE SCRAPER OUTPUT WITH SAMPLE DATA")
    print("=" * 70)
    print("\nThis demo shows what the scraper output looks like.")
    print("Using sample retail product data from Russian grocery stores.")
    print()
    
    # Show sample products
    print("\n📦 SAMPLE PARSED PRODUCTS:")
    print("-" * 70)
    for i, product in enumerate(sample_products[:5], 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Current Price: {product['price']:.2f} ₽")
        if 'old_price' in product:
            discount_pct = (product['old_price'] - product['price']) / product['old_price'] * 100
            print(f"   Old Price: {product['old_price']:.2f} ₽")
            print(f"   Discount: {discount_pct:.1f}% OFF")
        print(f"   URL: {product.get('url', 'N/A')}")
    
    print(f"\n... and {len(sample_products) - 5} more products")
    
    # Create analyzer
    analyzer = PriceAnalyzer()
    
    # Analyze products
    print("\n\n📊 ANALYZING PRODUCTS...")
    analysis = analyzer.analyze_products(sample_products, '5ka_demo')
    
    # Find best deals
    best_deals = analyzer.find_best_deals(sample_products, top_n=5)
    
    print("\n\n🔥 TOP 5 BEST DEALS:")
    print("-" * 70)
    for i, deal in enumerate(best_deals, 1):
        print(f"\n{i}. {deal['name']}")
        print(f"   Now: {deal['price']:.2f} ₽ (was {deal['old_price']:.2f} ₽)")
        print(f"   Save: {deal['savings']:.2f} ₽ ({deal['discount_percent']:.1f}% off)")
    
    # Save results
    print("\n\n💾 SAVING RESULTS...")
    analyzer.save_results(sample_products, analysis, '5ka_demo')
    
    # Show CSV preview
    print("\n\n📄 CSV FILE PREVIEW (first 10 rows):")
    print("-" * 70)
    df = pd.DataFrame(sample_products)
    print(df[['name', 'price', 'old_price']].head(10).to_string(index=False))
    
    # Show files created
    import os
    print("\n\n✅ FILES CREATED IN output/ DIRECTORY:")
    print("-" * 70)
    output_files = [f for f in os.listdir('output') if '5ka_demo' in f]
    for file in sorted(output_files):
        file_path = os.path.join('output', file)
        size = os.path.getsize(file_path)
        print(f"   📁 {file} ({size:,} bytes)")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("\nCheck the 'output' directory to see the generated files.")
    print("\nNote: For real scraping of 5ka.ru, you would need to:")
    print("  1. Use Selenium (JavaScript-rendered site)")
    print("  2. Handle their bot protection")
    print("  3. Or use their API if available")
    print()


if __name__ == '__main__':
    main()

