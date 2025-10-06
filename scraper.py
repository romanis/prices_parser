"""
Web scraper with anti-detection measures for retail price collection.
"""

import time
import random
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import config


class RetailScraper:
    """Scraper with anti-detection measures for retail websites."""
    
    def __init__(self, use_cloudscraper: bool = True):
        """
        Initialize the scraper.
        
        Args:
            use_cloudscraper: If True, uses cloudscraper to bypass Cloudflare
        """
        self.logger = self._setup_logger()
        self.ua = UserAgent()
        self.session = self._create_session(use_cloudscraper)
        self.use_cloudscraper = use_cloudscraper
        
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
    
    def _create_session(self, use_cloudscraper: bool) -> requests.Session:
        """Create a requests session with anti-detection headers."""
        if use_cloudscraper:
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
    
    def fetch_page(self, url: str, retries: int = 0) -> Optional[str]:
        """
        Fetch a page with retry logic and anti-detection measures.
        
        Args:
            url: URL to fetch
            retries: Current retry count
            
        Returns:
            HTML content or None if failed
        """
        if retries > config.MAX_RETRIES:
            self.logger.error(f"Max retries reached for {url}")
            return None
        
        try:
            headers = self._get_random_headers()
            self.logger.info(f"Fetching: {url}")
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully fetched {url}")
                self._random_delay()
                return response.text
            elif response.status_code == 429:
                self.logger.warning(f"Rate limited on {url}, waiting longer...")
                time.sleep(config.RETRY_DELAY * (retries + 1))
                return self.fetch_page(url, retries + 1)
            else:
                self.logger.error(f"Failed to fetch {url}: Status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            if retries < config.MAX_RETRIES:
                time.sleep(config.RETRY_DELAY)
                return self.fetch_page(url, retries + 1)
            return None
    
    def parse_5ka_products(self, html: str) -> List[Dict]:
        """
        Parse product information from 5ka.ru HTML.
        
        Args:
            html: HTML content
            
        Returns:
            List of product dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        products = []
        
        # Note: This is a generic parser. The actual selectors need to be
        # adjusted based on 5ka.ru's current HTML structure
        
        # Try multiple possible selectors for products
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
        """
        Extract product data from a product element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Product dictionary or None
        """
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
                # Extract numeric value
                price_numeric = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                if price_numeric:
                    product['price'] = float(price_numeric)
                    product['price_text'] = price_text
                    break
        
        # Try to find old/original price
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
        
        # Try to find product image
        img_elem = element.select_one('img')
        if img_elem:
            product['image_url'] = img_elem.get('src') or img_elem.get('data-src')
        
        # Try to find product link
        link_elem = element.select_one('a')
        if link_elem:
            product['url'] = link_elem.get('href')
        
        # Only return if we have at least name and price
        if 'name' in product and 'price' in product:
            return product
        
        return None
    
    def scrape_5ka_catalog(self, category_url: Optional[str] = None, max_pages: int = 5) -> List[Dict]:
        """
        Scrape product catalog from 5ka.ru.
        
        Args:
            category_url: Specific category URL, or None for main catalog
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of all products found
        """
        base_url = category_url or config.COMPETITORS['5ka']['catalog_url']
        all_products = []
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"Scraping page {page}/{max_pages}")
            
            # Construct page URL (adjust based on actual pagination structure)
            if page == 1:
                url = base_url
            else:
                # Common pagination patterns
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
    
    def close(self):
        """Close the session."""
        self.session.close()

