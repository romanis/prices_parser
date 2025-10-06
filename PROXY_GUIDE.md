# Proxy Setup Guide for Automatic IP Rotation

This guide explains how to set up proxies for automatic IP rotation when the parser is blocked.

## 🎯 Why Use Proxies?

When scraping retail websites, you may encounter:
- **IP blocks** after too many requests
- **Rate limiting** (429 errors)
- **Access denied** (403 errors)
- **Geographic restrictions**

**Solution**: Automatic proxy rotation switches your IP address when blocks are detected.

## 🚀 Quick Start

### Option 1: Using Proxy File

1. Create a file `proxies.txt` with one proxy per line:
```
http://proxy1.example.com:8080
http://proxy2.example.com:8080
http://username:password@proxy3.com:8080
socks5://proxy4.example.com:1080
```

2. Run the scraper:
```bash
python main_with_auto_proxy.py --proxy-file proxies.txt
```

### Option 2: Command Line Proxies

```bash
python main_with_auto_proxy.py --proxy-list http://proxy1:8080 http://proxy2:8080
```

### Option 3: Programmatic Usage

```python
from scraper_with_auto_proxy import SmartRetailScraper
from price_analyzer import PriceAnalyzer

# Your proxy list
proxies = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    'http://user:pass@proxy3.com:8080'
]

# Initialize with automatic IP rotation
scraper = SmartRetailScraper(
    proxy_list=proxies,
    use_cloudscraper=True,
    auto_rotate_on_block=True
)

# Scrape (IP switches automatically on block)
products = scraper.scrape_5ka_catalog(max_pages=10)
scraper.close()

# Analyze
analyzer = PriceAnalyzer()
analysis = analyzer.analyze_products(products, '5ka')
analyzer.save_results(products, analysis, '5ka')
```

## 🔄 How Automatic IP Rotation Works

1. **Request is made** through current proxy
2. **Block detection** checks response for:
   - Status codes: 403, 429, 503
   - Content patterns: "access denied", "captcha", "blocked", etc.
3. **Automatic switch** to new proxy from pool
4. **Retry** request with new IP
5. **Success tracking** - working proxies are preferred
6. **Failure tracking** - bad proxies get cooldown period

## 📊 Block Detection

The system automatically detects blocks by checking:

### Status Codes
- **403** - Forbidden (access denied)
- **429** - Too Many Requests (rate limited)
- **503** - Service Unavailable (temporarily blocked)

### Content Patterns
- "access denied"
- "blocked"
- "captcha"
- "security check"
- "rate limit"
- "bot detection"
- "suspicious activity"

When detected, the scraper:
1. ⚠️  Logs the block
2. 🔄 Switches to a new proxy
3. ⏳ Waits before retry
4. ✅ Continues scraping

## 🌐 Where to Get Proxies

### Free Proxy Lists (Lower Quality)
- [Free-Proxy-List.net](https://free-proxy-list.net/)
- [ProxyScrape](https://proxyscrape.com/)
- [PubProxy](http://pubproxy.com/)
- [Geonode](https://geonode.com/free-proxy-list)

⚠️ **Note**: Free proxies are often slow, unreliable, and may be blacklisted.

### Paid Proxy Services (Recommended)

#### Residential Proxies (Best for Scraping)
- **[BrightData](https://brightdata.com/)** (formerly Luminati) - Industry leader
- **[Oxylabs](https://oxylabs.io/)** - High quality, residential IPs
- **[Smartproxy](https://smartproxy.com/)** - Good balance of price/quality
- **[IPRoyal](https://iproyal.com/)** - Affordable residential proxies
- **[NetNut](https://netnut.io/)** - Fast residential network

#### Datacenter Proxies (Cheaper, but easier to detect)
- **[ProxyMesh](https://proxymesh.com/)** - Reliable datacenter proxies
- **[Webshare](https://www.webshare.io/)** - Affordable proxy service
- **[Proxy-Cheap](https://www.proxy-cheap.com/)** - Budget-friendly

#### Specialized Scraping Services (All-in-One)
- **[ScraperAPI](https://www.scraperapi.com/)** - Proxy + Cloudflare bypass
- **[Zyte](https://www.zyte.com/)** (formerly Scrapinghub) - Full scraping platform
- **[Crawlbase](https://crawlbase.com/)** - Proxy + JS rendering

### Residential vs Datacenter Proxies

| Feature | Residential | Datacenter |
|---------|-------------|------------|
| **Detection Risk** | Low | High |
| **Speed** | Moderate | Fast |
| **Price** | High ($5-15/GB) | Low ($1-3/GB) |
| **Best For** | E-commerce, social media | APIs, less protected sites |
| **Recommendation** | ✅ Use for retail scraping | ⚠️ May get blocked faster |

## 📝 Proxy Format Examples

### HTTP Proxy
```
http://123.45.67.89:8080
```

### HTTPS Proxy
```
https://123.45.67.89:8080
```

### Authenticated Proxy
```
http://username:password@proxy.example.com:8080
```

### SOCKS5 Proxy
```
socks5://123.45.67.89:1080
```

## 🔧 Advanced Configuration

### Customize Proxy Manager

Edit `proxy_manager.py` to adjust:

```python
manager = ProxyRotationManager(
    proxy_list=proxies,
    max_failures=3,          # Max failures before marking proxy as bad
    cooldown_time=300,       # Seconds to wait before retrying failed proxy
    test_on_init=True        # Test all proxies on startup
)
```

### Custom Block Detection

Add your own patterns in `scraper_with_auto_proxy.py`:

```python
block_indicators = [
    'access denied',
    'blocked',
    'your custom pattern here',
    # Add site-specific patterns
]
```

## 📈 Monitoring Proxy Performance

The scraper tracks statistics automatically:

```
SCRAPING STATISTICS
======================================================================
Total Requests:       50
Successful:           45
Failed:               5
Blocks Detected:      3
IP Switches:          3
Success Rate:         90.0%

PROXY POOL STATISTICS
======================================================================
Total Proxies:        5
Working Proxies:      4
Failed Proxies:       1
Avg Response Time:    1.23s
Current Proxy:        http://proxy2.example.com:8080
```

## 🎓 Best Practices

### 1. Use Enough Proxies
- **Minimum**: 5-10 proxies
- **Recommended**: 20+ proxies for continuous scraping
- **Large scale**: 100+ proxies

### 2. Mix Proxy Types
```python
proxies = [
    # Fast datacenter for testing
    'http://datacenter1.com:8080',
    # Reliable residential for actual scraping
    'http://residential1.com:8080',
    'http://residential2.com:8080',
    # Backup proxies
    'http://backup1.com:8080',
]
```

### 3. Monitor and Replace
- Check statistics regularly
- Replace consistently failing proxies
- Test new proxies before adding to production

### 4. Adjust Delays
```python
# In config.py
MIN_DELAY = 3  # Increase with proxies to be extra safe
MAX_DELAY = 7
```

### 5. Geographic Considerations
- Use proxies from the target country
- For 5ka.ru (Russia), use Russian or nearby IPs
- Avoid suspiciously distant locations

## 🛠️ Troubleshooting

### All Proxies Failing
**Solution**:
1. Test proxies manually: `python proxy_manager.py`
2. Check proxy credentials
3. Verify proxy format (http://, port, etc.)
4. Try different proxy provider

### Still Getting Blocked
**Solution**:
1. Increase delays between requests
2. Use residential proxies instead of datacenter
3. Reduce concurrent requests
4. Add more variety to user agents
5. Consider using Selenium for more realistic behavior

### Slow Performance
**Solution**:
1. Use faster proxy service
2. Filter out slow proxies (set timeout lower)
3. Use geographically closer proxies
4. Reduce proxy pool to only fastest ones

### Proxy Authentication Issues
**Solution**:
```python
# Correct format:
'http://username:password@proxy.com:8080'

# Not:
'http://proxy.com:8080' with separate auth
```

## 💡 Cost-Effective Strategy

### For Learning/Small Scale
1. Start with free proxies (test only)
2. Use direct connection with high delays
3. Scrape during off-peak hours

### For Production/Medium Scale  
1. Purchase residential proxy plan (~$50-100/month)
2. 5-10 GB should handle moderate scraping
3. Rotate IPs automatically

### For Large Scale
1. Consider ScraperAPI or similar service
2. They handle proxies, blocks, CAPTCHAs
3. Pay per successful request
4. No infrastructure management

## 📞 Support

If you encounter issues:
1. Check logs in `scraper.log`
2. Run `test_connection.py` to verify setup
3. Test individual proxies
4. Review proxy provider documentation

## Example: Complete Setup

```bash
# 1. Create proxy file
cat > proxies.txt << EOF
http://user:pass@proxy1.provider.com:8080
http://user:pass@proxy2.provider.com:8080
http://user:pass@proxy3.provider.com:8080
EOF

# 2. Test proxies
python -c "
from proxy_manager import ProxyRotationManager
manager = ProxyRotationManager(['http://user:pass@proxy1.provider.com:8080'])
manager.test_all_proxies()
"

# 3. Run scraper with auto IP rotation
python main_with_auto_proxy.py \
    --proxy-file proxies.txt \
    --max-pages 10 \
    --output-format all

# 4. Check results
ls -lh output/
```

## 🎉 Success Indicators

You'll know it's working when you see:
- ✅ "Working proxies: X/Y"
- ✅ "Switched from proxy1 to proxy2"
- ✅ "Successfully fetched" messages
- ✅ Blocks detected but scraping continues
- ✅ Success rate > 80%

---

**Remember**: Always respect website Terms of Service and scrape responsibly!

