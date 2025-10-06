# Quick Start Guide

Get started with the Retail Price Scraper in 3 simple steps!

## 1. Installation

Run the installation script:

```bash
bash install.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create output directory
mkdir -p output
```

## 2. Run Your First Scrape

### Option A: Simple Command

```bash
python main.py
```

This will scrape the first 5 pages of 5ka.ru catalog.

### Option B: Try Examples

```bash
python example_usage.py
```

This runs example scenarios showing different features.

### Option C: Custom Scraping

```bash
# Scrape 10 pages
python main.py --max-pages 10

# Scrape specific URL
python main.py --url "https://5ka.ru/catalog/category"

# Export to Excel
python main.py --output-format excel

# Export to all formats
python main.py --output-format all
```

## 3. View Results

Results are saved in the `output/` directory:

- `*_products.csv` - Raw product data
- `*_analysis.json` - Statistical analysis
- `*_summary.txt` - Human-readable report

## Advanced Usage

### Using Selenium (for JavaScript-heavy sites)

```bash
python selenium_scraper.py --max-pages 3
```

### Using Proxies

Edit `proxy_example.py` to add your proxy list, then integrate with the scraper.

### Programmatic Usage

```python
from scraper import RetailScraper
from price_analyzer import PriceAnalyzer

# Scrape
scraper = RetailScraper(use_cloudscraper=True)
products = scraper.scrape_5ka_catalog(max_pages=3)
scraper.close()

# Analyze
analyzer = PriceAnalyzer()
analysis = analyzer.analyze_products(products, '5ka')
analyzer.save_results(products, analysis, '5ka')
```

## Troubleshooting

### No products found
- The website structure may have changed
- Update CSS selectors in `scraper.py`
- Try the Selenium version: `python selenium_scraper.py`

### Getting blocked
- Increase delays in `config.py` (MIN_DELAY, MAX_DELAY)
- Reduce max pages to scrape
- Use proxies (see `proxy_example.py`)

### Installation issues
- Make sure Python 3.8+ is installed
- Try upgrading pip: `pip install --upgrade pip`
- Install dependencies one by one to identify issues

## Configuration

Edit `config.py` to customize:

```python
# Increase delays to be more polite
MIN_DELAY = 3
MAX_DELAY = 7

# Change output directory
OUTPUT_DIR = 'my_results'

# Adjust timeout
REQUEST_TIMEOUT = 60
```

## Tips for Avoiding Detection

1. ✅ Use reasonable delays (2-5 seconds minimum)
2. ✅ Don't scrape too many pages at once
3. ✅ Scrape during off-peak hours
4. ✅ Use cloudscraper (enabled by default)
5. ✅ Rotate user agents (automatic)
6. ✅ Consider using proxies for large-scale scraping
7. ✅ Respect robots.txt
8. ✅ Don't overload servers

## Legal Notice

⚠️ **Important**: Always:
- Check website Terms of Service
- Respect robots.txt
- Use data ethically
- Consider getting permission for commercial use

This tool is for educational and personal use only.

## Need Help?

1. Check `README.md` for detailed documentation
2. Review `example_usage.py` for code examples
3. Check logs in `scraper.log`
4. Inspect website HTML if selectors need updating

## What's Next?

- Customize for other competitors
- Add more analysis features
- Integrate with your database
- Set up scheduled scraping
- Build a price comparison dashboard

Happy scraping! 🚀

