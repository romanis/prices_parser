# Sample Parsed Price Output

This document shows examples of the parsed price data and analysis output.

## 📊 Sample Parsed Products

Here are examples of individual products that the scraper extracts:

### Product 1: Sale Item
```
Name: Молоко Простоквашино 3,2% 1л
Current Price: 89.99 ₽
Old Price: 109.99 ₽
Discount: 18.2% OFF
Savings: 20.00 ₽
URL: /product/milk-1
```

### Product 2: Regular Price Item
```
Name: Хлеб Бородинский нарезной 400г
Current Price: 45.50 ₽
URL: /product/bread-1
```

### Product 3: High-Value Sale
```
Name: Куриное филе охлажденное 1кг
Current Price: 289.00 ₽
Old Price: 349.00 ₽
Discount: 17.2% OFF
Savings: 60.00 ₽
URL: /product/chicken-1
```

## 🔥 Best Deals Analysis

The scraper automatically identifies the best discounts:

| Rank | Product | Current | Was | Discount | Savings |
|------|---------|---------|-----|----------|---------|
| 1 | Гречка ядрица 900г | 89.90 ₽ | 119.90 ₽ | 25.0% | 30.00 ₽ |
| 2 | Мороженое Пломбир эскимо 80г | 45.00 ₽ | 59.00 ₽ | 23.7% | 14.00 ₽ |
| 3 | Сыр Российский 45% 200г | 179.00 ₽ | 229.00 ₽ | 21.8% | 50.00 ₽ |
| 4 | Рис Мистраль длиннозерный 900г | 149.00 ₽ | 189.00 ₽ | 21.2% | 40.00 ₽ |
| 5 | Сметана 20% Домик в деревне 300г | 119.00 ₽ | 149.00 ₽ | 20.1% | 30.00 ₽ |

## 📈 Price Statistics Summary

```
Total Products: 20

Price Statistics:
  Average Price:    123.55 ₽
  Median Price:     107.00 ₽
  Min Price:         35.50 ₽
  Max Price:        289.00 ₽
  Std Deviation:     67.59 ₽

Discount Analysis:
  Products on Sale:         10 (50.0%)
  Avg Discount Amount:      35.40 ₽
  Avg Discount Percent:     20.2%
  Max Discount:             25.0%

Price Distribution:
  0-100 ₽:          10 products
  100-300 ₽:        10 products
  300-500 ₽:         0 products
  500-1000 ₽:        0 products
  1000+ ₽:           0 products
```

## 📁 Output File Formats

### 1. CSV Format (products.csv)
```csv
name,price,old_price,price_text,image_url,url,discount_percent,savings
"Молоко Простоквашино 3,2% 1л",89.99,109.99,"89,99 ₽",...,/product/milk-1,18.18,20.0
"Хлеб Бородинский нарезной 400г",45.5,,"45,50 ₽",...,/product/bread-1,,
```
**Use Case**: Import into Excel, Google Sheets, or databases

### 2. JSON Format (analysis.json)
```json
{
  "competitor": "5ka_demo",
  "timestamp": "2025-10-05T23:52:27.711071",
  "total_products": 20,
  "price_statistics": {
    "average_price": 123.554,
    "median_price": 107.0,
    "min_price": 35.5,
    "max_price": 289.0,
    "std_deviation": 67.59
  },
  "discounts": {
    "products_with_discount": 10,
    "discount_percentage": 50.0,
    "average_discount_amount": 35.4,
    "average_discount_percent": 20.23,
    "max_discount_percent": 25.02
  }
}
```
**Use Case**: API integration, web applications, data pipelines

### 3. Text Summary (summary.txt)
```
======================================================================
PRICE ANALYSIS REPORT - 5ka_demo
Generated: 2025-10-05T23:52:27.711071
======================================================================

Total Products Analyzed: 20

PRICE STATISTICS:
  Average Price:     123.55 ₽
  Median Price:      107.00 ₽
  ...
```
**Use Case**: Email reports, documentation, quick review

## 🎯 Data Fields Extracted

Each product includes:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Product name | "Молоко Простоквашино 3,2% 1л" |
| `price` | Current price (numeric) | 89.99 |
| `old_price` | Original price if on sale | 109.99 |
| `price_text` | Formatted price with currency | "89,99 ₽" |
| `image_url` | Product image URL | "https://..." |
| `url` | Product page URL | "/product/milk-1" |
| `discount_percent` | Calculated discount % | 18.18 |
| `savings` | Amount saved | 20.00 |

## 💡 Use Cases

### 1. Price Monitoring
```python
# Track daily price changes
products_today = scraper.scrape_5ka_catalog()
analyzer.save_results(products_today, analysis, f'5ka_{date}')
# Compare with yesterday's data
```

### 2. Competitive Analysis
```python
# Find products cheaper than our prices
cheap_products = [p for p in products if p['price'] < our_price_database[p['name']]]
```

### 3. Deal Alerts
```python
# Alert on discounts > 30%
big_deals = analyzer.find_best_deals(products, top_n=10)
send_email_alert(big_deals)
```

### 4. Market Research
```python
# Analyze pricing strategies
analysis = analyzer.analyze_products(products)
avg_price = analysis['price_statistics']['average_price']
discount_rate = analysis['discounts']['discount_percentage']
```

## 🔄 Integration Examples

### Excel/Google Sheets
1. Open CSV file directly
2. Use VLOOKUP for price comparisons
3. Create pivot tables for analysis

### Python/Pandas
```python
import pandas as pd
df = pd.read_csv('5ka_demo_products.csv')
# Filter products under 100 rubles
cheap = df[df['price'] < 100]
# Calculate average discount
avg_discount = df['discount_percent'].mean()
```

### Database (PostgreSQL/MySQL)
```python
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('5ka_demo_products.csv')
engine = create_engine('postgresql://user:pass@localhost/db')
df.to_sql('competitor_prices', engine, if_exists='append')
```

### REST API
```python
import json
with open('5ka_demo_analysis.json') as f:
    data = json.load(f)
# Send to your API
requests.post('https://api.example.com/prices', json=data)
```

## 📊 Example Analytics Queries

### Find cheapest products in category
```python
dairy = [p for p in products if 'молоко' in p['name'].lower() or 'сыр' in p['name'].lower()]
cheapest_dairy = min(dairy, key=lambda x: x['price'])
```

### Calculate total savings
```python
total_savings = sum(p.get('savings', 0) for p in products if 'savings' in p)
print(f"Total potential savings: {total_savings:.2f} ₽")
```

### Price trends (with historical data)
```python
# Compare average prices over time
dates = ['2025-10-01', '2025-10-02', '2025-10-03']
avg_prices = [load_analysis(date)['price_statistics']['average_price'] for date in dates]
plot_trend(dates, avg_prices)
```

## 🎓 Key Features Demonstrated

✅ **Complete Product Data** - Name, price, discounts, images, URLs  
✅ **Automatic Discount Calculation** - Percentage and absolute savings  
✅ **Statistical Analysis** - Mean, median, min, max, std deviation  
✅ **Best Deals Ranking** - Sorted by discount percentage  
✅ **Multiple Output Formats** - CSV, JSON, TXT for different uses  
✅ **Price Distribution** - Products grouped by price ranges  
✅ **Discount Summary** - % of products on sale, average discount  

## ⚠️ Important Notes

### For Real 5ka.ru Scraping:
- Site uses JavaScript rendering (requires Selenium)
- Has bot protection (ServicePipe)
- May need to inspect current HTML structure
- Respect robots.txt and terms of service

### Anti-Detection in Place:
- Random user agents
- Random delays (2-5 seconds)
- Realistic browser headers
- Cloudscraper for Cloudflare bypass
- Session management

### Data Freshness:
- Timestamps included in all files
- Recommended: scrape daily or weekly
- Store historical data for trend analysis

---

**This sample demonstrates the complete workflow from scraping to analysis.**

For real-world use, adjust selectors based on target website structure.

