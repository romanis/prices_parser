# Retail Price Scraper

A sophisticated web scraper for collecting and analyzing competitor retail prices with anti-detection measures.

## Features

- **Anti-Detection Measures**
  - Random user agent rotation
  - Random delays between requests
  - Cloudscraper integration to bypass Cloudflare
  - Realistic browser headers
  - Session management with cookies

- **Data Collection**
  - Product names and prices
  - Old/sale prices and discounts
  - Product images and URLs
  - Multi-page scraping support

- **Price Analysis**
  - Statistical analysis (mean, median, min, max, std dev)
  - Discount analysis
  - Price distribution
  - Best deals identification
  - Category comparison

- **Multiple Output Formats**
  - CSV
  - JSON
  - Excel
  - Text summary reports

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Scrape 5ka.ru catalog (first 5 pages):
```bash
python main.py
```

### Advanced Options

```bash
# Scrape specific number of pages
python main.py --max-pages 10

# Scrape specific URL/category
python main.py --url "https://5ka.ru/catalog/some-category"

# Change output format
python main.py --output-format excel

# Multiple formats
python main.py --output-format all
```

### Command Line Arguments

- `--competitor`: Competitor to scrape (default: 5ka)
- `--url`: Specific URL to scrape (optional)
- `--max-pages`: Maximum pages to scrape (default: 5)
- `--use-cloudscraper`: Use cloudscraper for Cloudflare bypass (default: True)
- `--output-format`: Output format - csv, json, excel, or all (default: csv)

## Configuration

Edit `config.py` to customize:

- **Request delays**: `MIN_DELAY` and `MAX_DELAY`
- **Retry settings**: `MAX_RETRIES` and `RETRY_DELAY`
- **User agents**: Add more user agents to `USER_AGENTS` list
- **Timeout**: Adjust `REQUEST_TIMEOUT`
- **Output directory**: Change `OUTPUT_DIR`

## Anti-Detection Best Practices

1. **Use reasonable delays**: Keep `MIN_DELAY` at 2-5 seconds
2. **Limit pages**: Don't scrape too many pages at once
3. **Rotate IP addresses**: Consider using proxies for large-scale scraping
4. **Respect robots.txt**: Check the website's robots.txt file
5. **Use cloudscraper**: Enabled by default to handle Cloudflare
6. **Scrape during off-peak hours**: Reduces detection risk

## Output Files

After scraping, you'll find in the `output/` directory:

- `{competitor}_{timestamp}_products.csv` - Raw product data
- `{competitor}_{timestamp}_analysis.json` - Statistical analysis
- `{competitor}_{timestamp}_summary.txt` - Human-readable summary report

## Customizing for Different Websites

To adapt the scraper for other retail websites:

1. Add website configuration to `config.py`:
```python
COMPETITORS = {
    'your_competitor': {
        'name': 'Display Name',
        'url': 'https://example.com',
        'catalog_url': 'https://example.com/catalog',
        'enabled': True
    }
}
```

2. Create a new parsing method in `scraper.py`:
```python
def parse_your_competitor(self, html: str) -> List[Dict]:
    # Implement parsing logic
    pass
```

3. Add competitor to main.py choices

## Website Structure Changes

If scraping fails with no products found:

1. **Inspect the website HTML**:
   - Open the website in a browser
   - Right-click and "Inspect Element"
   - Find product containers and their CSS classes

2. **Update selectors in scraper.py**:
   - Modify `product_selectors` list in `parse_5ka_products()`
   - Update `name_selectors`, `price_selectors`, etc. in `_extract_product_data()`

3. **Check for JavaScript rendering**:
   - If products load via JavaScript, use the Selenium version (see `selenium_scraper.py`)

## Advanced: Using Selenium for JavaScript Sites

If the website heavily relies on JavaScript, use Selenium:

```bash
python selenium_scraper.py --max-pages 3
```

Selenium is slower but can handle dynamic content.

## Legal and Ethical Considerations

⚠️ **Important**: Web scraping may have legal implications:

- Check the website's Terms of Service
- Respect robots.txt
- Don't overload servers with requests
- Use data responsibly and ethically
- Consider getting explicit permission for commercial use
- Some websites explicitly prohibit scraping in their ToS

This tool is provided for educational purposes and personal use only.

## Troubleshooting

### No products found
- Website structure may have changed - update CSS selectors
- Website may use JavaScript - try Selenium version
- Check if you're being blocked - increase delays or use proxies

### Getting blocked/rate limited
- Increase `MIN_DELAY` and `MAX_DELAY` in config.py
- Reduce `--max-pages`
- Use proxies
- Try different user agents

### CloudFlare challenges
- cloudscraper should handle most challenges automatically
- For advanced protection, consider using undetected-chromedriver

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: Fast XML/HTML parser
- `fake-useragent`: User agent rotation
- `cloudscraper`: Cloudflare bypass
- `selenium`: Browser automation (optional)
- `pandas`: Data analysis
- `python-dotenv`: Environment variables

## License

This project is for educational purposes only. Use responsibly and in accordance with applicable laws and regulations.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Support

For issues or questions, please check:
1. Website structure hasn't changed
2. All dependencies are installed
3. Configuration settings are appropriate
4. Check logs in `scraper.log`

