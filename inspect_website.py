#!/usr/bin/env python3
"""
Inspect 5ka.ru website structure to find correct selectors.
"""

import cloudscraper
from bs4 import BeautifulSoup
import config

# Create scraper
scraper = cloudscraper.create_scraper()
headers = config.DEFAULT_HEADERS.copy()
headers['User-Agent'] = config.USER_AGENTS[0]

# Fetch page
print("Fetching 5ka.ru...")
response = scraper.get('https://5ka.ru/catalog', headers=headers, timeout=30)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)} bytes")

# Parse HTML
soup = BeautifulSoup(response.text, 'lxml')

# Save HTML for inspection
with open('output/page_sample.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())
print("\n✓ Saved HTML to output/page_sample.html")

# Look for common patterns
print("\n" + "="*70)
print("SEARCHING FOR PRODUCT PATTERNS")
print("="*70)

# Look for price-related text
prices_found = soup.find_all(string=lambda text: '₽' in str(text) if text else False)
print(f"\nFound {len(prices_found)} elements with '₽' symbol")
if prices_found[:5]:
    print("Sample prices:")
    for i, price in enumerate(prices_found[:5], 1):
        print(f"  {i}. {price.strip()[:50]}")

# Look for common class patterns
print("\nSearching for common product-related classes...")
for pattern in ['product', 'item', 'card', 'goods', 'catalog']:
    elements = soup.find_all(class_=lambda x: x and pattern in x.lower() if x else False)
    if elements:
        classes = set()
        for elem in elements[:10]:
            if elem.get('class'):
                classes.update(elem['class'])
        print(f"\n  Pattern '{pattern}': {len(elements)} elements")
        print(f"  Classes: {', '.join(list(classes)[:5])}")

# Look for divs with data attributes
print("\nSearching for divs with data attributes...")
divs_with_data = soup.find_all('div', attrs=lambda x: any(k.startswith('data-') for k in x.keys()) if x else False)
print(f"Found {len(divs_with_data)} divs with data attributes")

# Check for JavaScript/React indicators
scripts = soup.find_all('script')
has_react = any('react' in str(script).lower() for script in scripts)
has_vue = any('vue' in str(script).lower() for script in scripts)
has_angular = any('angular' in str(script).lower() for script in scripts)

print(f"\n" + "="*70)
print("JAVASCRIPT FRAMEWORK DETECTION")
print("="*70)
print(f"React: {'Yes' if has_react else 'No'}")
print(f"Vue: {'Yes' if has_vue else 'No'}")
print(f"Angular: {'Yes' if has_angular else 'No'}")

if has_react or has_vue or has_angular:
    print("\n⚠️  This website uses JavaScript frameworks!")
    print("   You should use Selenium scraper instead:")
    print("   python selenium_scraper.py --max-pages 1")

print("\n" + "="*70)

