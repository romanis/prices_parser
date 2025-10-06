"""
Enhanced web scraper with automatic IP rotation on block detection.
Automatically switches proxies when parser is blocked.
"""

import time
import random
import logging
from typing import Dict, List, Optional

import requests
import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import config
from proxy_manager import ProxyRotationManager


class SmartRetailScraper:
    """
    Retail scraper with automatic IP switching on block detection.
    """
    
    def __init__(
        self,
        proxy_list: Optional[List[str]] = None,
        use_cloudscraper: bool = True,
        auto_rotate_on_block: bool = True
    ):
        """
        Initialize the scraper with automatic IP rotation.
        
        Args:
            proxy_list: List of proxy URLs
            use_cloudscraper: Use cloudscraper for Cloudflare bypass
            auto_rotate_on_block: Automatically rotate IP when blocked
        """
        self.logger = self._setup_logger()
        self.ua = UserAgent()
        self.use_cloudscraper = use_cloudscraper
        self.auto_rotate = auto_rotate_on_block
        
        # Initialize proxy manager
        self.proxy_manager = None
        if proxy_list:
            self.logger.info(f"Initializing proxy manager with {len(proxy_list)} proxies...")
            self.proxy_manager = ProxyRotationManager(
                proxy_list=proxy_list,
                max_failures=3,
                cooldown_time=300,
                test_on_init=True
            )
            self.proxy_manager.print_stats()
        else:
            self.logger.warning("No proxies provided - using direct connection")
        
        # Create session
        self.session = self._create_session()
        
        # Statistics
        self.stats = {
            'requests': 0,
            'blocks_detected': 0,
            'ip_switches': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session."""
        if self.use_cloudscraper:
            session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
        else:
            session = requests.Session()
        
        return session
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection."""
        headers = config.DEFAULT_HEADERS.copy()
        headers['User-Agent'] = random.choice(config.USER_AGENTS)
        return headers
    
    def _random_delay(self):
        """Add random delay between requests."""
        delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
        self.logger.debug(f"Sleeping for {delay:.2f} seconds")
        time.sleep(delay)
    
    def fetch_page(self, url: str, max_retries: int = None) -> Optional[str]:
        """
        Fetch a page with automatic IP rotation on block detection.
        
        Args:
            url: URL to fetch
            max_retries: Maximum retry attempts (None = use config)
            
        Returns:
            HTML content or None if failed
        """
        if max_retries is None:
            max_retries = config.MAX_RETRIES
        
        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                # Get proxy if available
                proxies = None
                if self.proxy_manager:
                    proxy = self.proxy_manager.get_next_proxy()
                    if proxy:
                        proxies = self.proxy_manager.get_proxy_dict(proxy)
                        self.logger.info(f"Using proxy: {proxy.url}")
                
                # Prepare request
                headers = self._get_random_headers()
                self.stats['requests'] += 1
                
                self.logger.info(f"Fetching: {url} (attempt {retries + 1}/{max_retries + 1})")
                
                # Make request
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxies,
                    timeout=config.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                # Check for block
                is_blocked = self._check_if_blocked(response)
                
                if is_blocked:
                    self.stats['blocks_detected'] += 1
                    self.logger.warning(f"🚫 Block detected on attempt {retries + 1}")
                    
                    if self.auto_rotate and self.proxy_manager:
                        # Automatic IP switch
                        self.stats['ip_switches'] += 1
                        new_proxy = self.proxy_manager.handle_block(response)
                        
                        if new_proxy:
                            self.logger.info("⏳ Waiting before retry with new IP...")
                            time.sleep(config.RETRY_DELAY)
                            retries += 1
                            continue
                        else:
                            self.logger.error("No working proxies available!")
                            self.stats['failed_requests'] += 1
                            return None
                    else:
                        # No auto-rotation available
                        self.logger.warning("Block detected but no proxy rotation available")
                        time.sleep(config.RETRY_DELAY * (retries + 1))
                        retries += 1
                        continue
                
                # Success!
                if response.status_code == 200:
                    self.stats['successful_requests'] += 1
                    self.logger.info(f"✓ Successfully fetched {url}")
                    
                    # Mark proxy as successful
                    if self.proxy_manager:
                        self.proxy_manager.mark_proxy_success()
                    
                    self._random_delay()
                    return response.text
                
                # Other status codes
                elif response.status_code == 404:
                    self.logger.error(f"Page not found: {url}")
                    self.stats['failed_requests'] += 1
                    return None
                
                else:
                    self.logger.error(f"Failed with status {response.status_code}")
                    last_error = f"Status {response.status_code}"
                    
                    # Mark proxy as failed
                    if self.proxy_manager:
                        self.proxy_manager.mark_proxy_failed()
                    
                    retries += 1
                    time.sleep(config.RETRY_DELAY)
                    
            except requests.exceptions.Timeout:
                last_error = "Timeout"
                self.logger.error(f"Request timeout for {url}")
                
                if self.proxy_manager:
                    self.proxy_manager.mark_proxy_failed()
                
                retries += 1
                time.sleep(config.RETRY_DELAY)
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                self.logger.error(f"Connection error for {url}: {str(e)}")
                
                if self.proxy_manager:
                    self.proxy_manager.mark_proxy_failed()
                
                retries += 1
                time.sleep(config.RETRY_DELAY)
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Unexpected error for {url}: {str(e)}")
                
                if self.proxy_manager:
                    self.proxy_manager.mark_proxy_failed()
                
                retries += 1
                time.sleep(config.RETRY_DELAY)
        
        # All retries exhausted
        self.stats['failed_requests'] += 1
        self.logger.error(f"Failed to fetch {url} after {max_retries + 1} attempts. Last error: {last_error}")
        return None
    
    def _check_if_blocked(self, response: requests.Response) -> bool:
        """
        Check if response indicates we're blocked.
        
        Args:
            response: Response object
            
        Returns:
            True if blocked
        """
        # Check status codes indicating blocks
        if response.status_code in [403, 429, 503]:
            return True
        
        # Check response content for block indicators
        content = response.text.lower()
        
        block_indicators = [
            'access denied',
            'blocked',
            'captcha',
            'cloudflare',
            'security check',
            'rate limit',
            'too many requests',
            'bot detection',
            'suspicious activity',
            'unusual traffic',
            'please verify',
            'challenge-platform'
        ]
        
        for indicator in block_indicators:
            if indicator in content:
                self.logger.warning(f"Block indicator found: '{indicator}'")
                return True
        
        # Check content length (sometimes blocked pages are very short)
        if len(content) < 500 and response.status_code == 200:
            self.logger.warning(f"Suspicious short response: {len(content)} bytes")
            # Don't automatically mark as block, but log it
        
        return False
    
    def parse_5ka_products(self, html: str) -> List[Dict]:
        """Parse product information from 5ka.ru HTML."""
        soup = BeautifulSoup(html, 'lxml')
        products = []
        
        product_selectors = [
            'div.product-card',
            'div.product-item',
            'div[class*="product"]',
            'article.product',
        ]
        
        product_elements = []
        for selector in product_selectors:
            product_elements = soup.select(selector)
            if product_elements:
                self.logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                break
        
        if not product_elements:
            self.logger.warning("No products found on page")
            return products
        
        for element in product_elements:
            try:
                product = self._extract_product_data(element)
                if product:
                    products.append(product)
            except Exception as e:
                self.logger.error(f"Error parsing product: {str(e)}")
                continue
        
        return products
    
    def _extract_product_data(self, element) -> Optional[Dict]:
        """Extract product data from element."""
        product = {}
        
        # Try to find product name
        name_selectors = [
            'h3', 'h4', '.product-name', '.product-title',
            '[class*="name"]', '[class*="title"]'
        ]
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                product['name'] = name_elem.get_text(strip=True)
                break
        
        # Try to find price
        price_selectors = [
            '.price', '[class*="price"]', '.product-price',
            'span[class*="price"]', 'div[class*="price"]'
        ]
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_numeric = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                if price_numeric:
                    product['price'] = float(price_numeric)
                    product['price_text'] = price_text
                    break
        
        # Try to find old price
        old_price_selectors = [
            '.old-price', '.original-price', '[class*="old-price"]',
            '.price-old', 'del', 's'
        ]
        for selector in old_price_selectors:
            old_price_elem = element.select_one(selector)
            if old_price_elem:
                old_price_text = old_price_elem.get_text(strip=True)
                old_price_numeric = ''.join(filter(lambda x: x.isdigit() or x == '.', old_price_text))
                if old_price_numeric:
                    product['old_price'] = float(old_price_numeric)
                    break
        
        # Image
        img_elem = element.select_one('img')
        if img_elem:
            product['image_url'] = img_elem.get('src') or img_elem.get('data-src')
        
        # Link
        link_elem = element.select_one('a')
        if link_elem:
            product['url'] = link_elem.get('href')
        
        if 'name' in product and 'price' in product:
            return product
        
        return None
    
    def scrape_5ka_catalog(
        self,
        category_url: Optional[str] = None,
        max_pages: int = 5
    ) -> List[Dict]:
        """Scrape 5ka.ru catalog with automatic IP rotation."""
        base_url = category_url or config.COMPETITORS['5ka']['catalog_url']
        all_products = []
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"Scraping page {page}/{max_pages}")
            
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page}"
            
            html = self.fetch_page(url)
            if not html:
                self.logger.warning(f"Failed to fetch page {page}")
                break
            
            products = self.parse_5ka_products(html)
            if not products:
                self.logger.info(f"No products found on page {page}, stopping")
                break
            
            all_products.extend(products)
            self.logger.info(f"Collected {len(products)} products from page {page}")
        
        self.logger.info(f"Total products collected: {len(all_products)}")
        return all_products
    
    def print_stats(self):
        """Print scraping statistics."""
        print("\n" + "=" * 70)
        print("SCRAPING STATISTICS")
        print("=" * 70)
        print(f"Total Requests:       {self.stats['requests']}")
        print(f"Successful:           {self.stats['successful_requests']}")
        print(f"Failed:               {self.stats['failed_requests']}")
        print(f"Blocks Detected:      {self.stats['blocks_detected']}")
        print(f"IP Switches:          {self.stats['ip_switches']}")
        
        if self.stats['requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['requests']) * 100
            print(f"Success Rate:         {success_rate:.1f}%")
        
        print("=" * 70)
        
        if self.proxy_manager:
            self.proxy_manager.print_stats()
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.print_stats()

