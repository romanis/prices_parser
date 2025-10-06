# Retail Price Scraper - Project Overview

A comprehensive, production-ready web scraping solution for competitive retail price analysis with advanced anti-detection measures.

## 📁 Project Structure

```
retail-price-scraper/
├── config.py              # Configuration settings (delays, headers, etc.)
├── scraper.py             # Main scraper with cloudscraper
├── selenium_scraper.py    # Advanced scraper using Selenium
├── price_analyzer.py      # Data analysis and reporting
├── main.py                # CLI entry point
├── example_usage.py       # Usage examples and tutorials
├── test_connection.py     # Test script to verify setup
├── proxy_example.py       # Proxy configuration examples
├── requirements.txt       # Python dependencies
├── install.sh             # Installation script
├── README.md              # Full documentation
├── QUICKSTART.md          # Quick start guide
└── output/                # Generated reports (created on first run)
```

## 🎯 Key Features

### Anti-Detection Measures
- ✅ Random user agent rotation
- ✅ Random delays between requests (2-5 seconds)
- ✅ Cloudscraper for Cloudflare bypass
- ✅ Realistic browser headers
- ✅ Session management with cookies
- ✅ Selenium support for JavaScript-heavy sites
- ✅ Proxy support (optional)

### Data Collection
- ✅ Product names and descriptions
- ✅ Current prices
- ✅ Original/sale prices
- ✅ Discount calculations
- ✅ Product images and URLs
- ✅ Multi-page pagination support

### Analysis Features
- ✅ Statistical analysis (mean, median, min, max, std dev)
- ✅ Discount analysis (percentage, amount)
- ✅ Price distribution charts
- ✅ Best deals identification
- ✅ Category comparison
- ✅ Custom filtering and queries

### Output Formats
- ✅ CSV (Excel-compatible)
- ✅ JSON (for APIs/databases)
- ✅ Excel (.xlsx)
- ✅ Text summary reports

## 🚀 Quick Start

```bash
# 1. Install
bash install.sh

# 2. Test connection
python test_connection.py

# 3. Run scraper
python main.py

# 4. Check results in output/ directory
```

## 📊 Example Output

### Console Output
```
======================================================================
RETAIL PRICE SCRAPER - STARTING
======================================================================
Competitor: 5ka
Max pages: 5
Output format: csv

Starting to scrape 5ka.ru...
✓ Successfully scraped 127 products

Analyzing product prices...

Top 10 Best Deals:
  1. Product Name: 149.99 ₽ (was 299.99 ₽, save 50.0%)
  ...

Saving results...
✓ Saved to output/5ka_20231006_143022_products.csv
```

### Generated Files
- `5ka_20231006_143022_products.csv` - Raw data
- `5ka_20231006_143022_analysis.json` - Statistics
- `5ka_20231006_143022_summary.txt` - Report

## 🛠️ Usage Examples

### Command Line

```bash
# Basic usage
python main.py

# Scrape more pages
python main.py --max-pages 10

# Specific category
python main.py --url "https://5ka.ru/catalog/dairy"

# Excel output
python main.py --output-format excel

# All formats
python main.py --output-format all
```

### Programmatic Usage

```python
from scraper import RetailScraper
from price_analyzer import PriceAnalyzer

# Initialize and scrape
scraper = RetailScraper(use_cloudscraper=True)
products = scraper.scrape_5ka_catalog(max_pages=5)
scraper.close()

# Analyze
analyzer = PriceAnalyzer()
analysis = analyzer.analyze_products(products, '5ka')

# Find best deals
best_deals = analyzer.find_best_deals(products, top_n=10)

# Save results
analyzer.save_results(products, analysis, '5ka')
```

## 🔧 Configuration

Edit `config.py` to customize behavior:

```python
# Delays between requests (seconds)
MIN_DELAY = 2  # Minimum delay
MAX_DELAY = 5  # Maximum delay

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5

# Timeout
REQUEST_TIMEOUT = 30

# Output
OUTPUT_DIR = 'output'
OUTPUT_FORMAT = 'csv'  # csv, json, excel, all
```

## 📦 Dependencies

Core libraries:
- `requests` - HTTP requests
- `cloudscraper` - Cloudflare bypass
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parsing
- `fake-useragent` - User agent rotation
- `pandas` - Data analysis
- `selenium` - Browser automation (optional)

## 🎓 Use Cases

1. **Price Monitoring**
   - Track competitor prices daily
   - Set up automated alerts for price changes

2. **Market Research**
   - Analyze pricing strategies
   - Identify market trends
   - Find pricing gaps

3. **Competitive Analysis**
   - Compare product ranges
   - Analyze discount patterns
   - Benchmark pricing

4. **Deal Finding**
   - Automatically find best deals
   - Track sale patterns
   - Identify seasonal trends

## ⚠️ Legal & Ethical Considerations

**Important**: Before using this tool:

1. ✅ Read the target website's Terms of Service
2. ✅ Check and respect robots.txt
3. ✅ Use reasonable delays (don't overload servers)
4. ✅ Consider getting explicit permission for commercial use
5. ✅ Use data ethically and responsibly
6. ✅ Be aware that some websites explicitly prohibit scraping

**This tool is provided for educational purposes and personal use only.**

## 🔒 Anti-Detection Best Practices

1. **Use Reasonable Delays**
   - Keep MIN_DELAY at 2-5 seconds minimum
   - Increase for heavy scraping

2. **Limit Scope**
   - Don't scrape too many pages at once
   - Consider splitting into multiple sessions

3. **Rotate Resources**
   - User agents (automatic)
   - IP addresses (use proxies)
   - Request patterns

4. **Scrape Smart**
   - Off-peak hours (late night/early morning)
   - Weekends when traffic is lower
   - Gradually increase scraping over time

5. **Monitor Performance**
   - Check logs regularly
   - Watch for rate limiting (429 errors)
   - Adjust delays if needed

6. **Use Cloudscraper**
   - Handles Cloudflare automatically
   - Better success rate than raw requests

7. **Consider Selenium**
   - For JavaScript-heavy sites
   - More realistic browser behavior
   - Slower but more reliable

## 🐛 Troubleshooting

### No products found
**Solution**: Website structure may have changed
```bash
# 1. Try Selenium version
python selenium_scraper.py

# 2. Inspect website and update selectors in scraper.py
```

### Getting blocked (403/429 errors)
**Solution**: Increase delays or use proxies
```python
# In config.py
MIN_DELAY = 5
MAX_DELAY = 10
```

### Cloudflare challenges
**Solution**: Cloudscraper should handle automatically
```bash
# If issues persist, try Selenium
python selenium_scraper.py --headless
```

### Installation errors
**Solution**: Check Python version and dependencies
```bash
python3 --version  # Should be 3.8+
pip install --upgrade pip
pip install -r requirements.txt
```

## 🚀 Advanced Features

### Using Proxies
See `proxy_example.py` for proxy configuration and integration.

### Custom Competitors
Add new competitors in `config.py` and create parsing methods.

### Automated Scheduling
Use cron (Linux/Mac) or Task Scheduler (Windows):
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/scraper && python main.py
```

### Database Integration
Extend `price_analyzer.py` to save to PostgreSQL, MySQL, or MongoDB.

### API Development
Build a REST API around the scraper using Flask or FastAPI.

## 📈 Performance

- **Speed**: ~5-10 products/minute (with delays)
- **Reliability**: High with cloudscraper
- **Memory**: Low (<100MB typically)
- **CPU**: Minimal for requests-based scraping

Selenium version is slower but more reliable for complex sites.

## 🤝 Contributing

To extend this project:

1. Add new competitor support
2. Improve parsing algorithms
3. Add more analysis features
4. Create visualization dashboards
5. Improve anti-detection measures

## 📝 Version History

- **v1.0** - Initial release
  - Basic scraping with cloudscraper
  - Price analysis
  - Multiple output formats
  - Anti-detection measures
  - Selenium support
  - Example usage

## 📞 Support

For issues:
1. Check `README.md` for detailed docs
2. Review `QUICKSTART.md` for setup
3. Run `test_connection.py` to diagnose issues
4. Check logs in `scraper.log`

## 🎯 Future Enhancements

Potential additions:
- Web dashboard for results
- Email notifications for price changes
- Machine learning for price predictions
- Multi-competitor comparison
- Historical price tracking
- API endpoints
- Docker containerization
- Cloud deployment guides

## 📄 License

This project is for educational purposes only. Use responsibly and in accordance with applicable laws and regulations.

---

**Happy Scraping! 🎉**

Remember: Always scrape ethically and respect the websites you're scraping from.

