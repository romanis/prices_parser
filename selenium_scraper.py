#!/usr/bin/env python3
"""
Advanced scraper using Selenium for JavaScript-heavy websites.
Use this when the regular scraper doesn't work due to dynamic content.
"""

import time
import random
import logging
import argparse
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import config
from price_analyzer import PriceAnalyzer


class SeleniumScraper:
    """Scraper using Selenium for JavaScript-rendered content."""
    
    def __init__(self, headless: bool = True):
        """
        Initialize Selenium scraper.
        
        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.logger = self._setup_logger()
        self.driver = self._setup_driver(headless)
        
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
    
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """
        Setup Chrome WebDriver with anti-detection options.
        
        Args:
            headless: Run in headless mode
            
        Returns:
            Chrome WebDriver instance
        """
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Anti-detection options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agent = random.choice(config.USER_AGENTS)
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Additional options
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--proxy-server="direct://"')
        chrome_options.add_argument('--proxy-bypass-list=*')
        
        # Set preferences to appear more human-like
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute CDP commands to mask automation
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": user_agent
        })
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        self.logger.info("Chrome WebDriver initialized")
        return driver
    
    def _random_delay(self):
        """Add random human-like delay."""
        delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
        time.sleep(delay)
    
    def _scroll_page(self, scroll_pause_time: float = 0.5):
        """
        Scroll page to load dynamic content.
        
        Args:
            scroll_pause_time: Time to wait between scrolls
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # Calculate new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            last_height = new_height
    
    def fetch_page(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Fetch page using Selenium.
        
        Args:
            url: URL to fetch
            wait_for_selector: CSS selector to wait for before returning
            
        Returns:
            Page HTML
        """
        try:
            self.logger.info(f"Fetching: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            if wait_for_selector:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
            else:
                time.sleep(3)  # Default wait
            
            # Scroll to load lazy-loaded content
            self._scroll_page()
            
            html = self.driver.page_source
            self._random_delay()
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    def scrape_5ka_catalog(self, category_url: Optional[str] = None, max_pages: int = 5) -> List[Dict]:
        """
        Scrape 5ka.ru catalog using Selenium.
        
        Args:
            category_url: Specific category URL
            max_pages: Maximum pages to scrape
            
        Returns:
            List of products
        """
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
            
            # Parse HTML
            soup = BeautifulSoup(html, 'lxml')
            products = self._parse_products(soup)
            
            if not products:
                self.logger.info(f"No products found on page {page}, stopping")
                break
            
            all_products.extend(products)
            self.logger.info(f"Collected {len(products)} products from page {page}")
        
        self.logger.info(f"Total products collected: {len(all_products)}")
        return all_products
    
    def _parse_products(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse products from BeautifulSoup object."""
        products = []
        
        # Try multiple selectors
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
        
        # Product name
        name_selectors = ['h3', 'h4', '.product-name', '.product-title', '[class*="name"]']
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem:
                product['name'] = name_elem.get_text(strip=True)
                break
        
        # Price
        price_selectors = ['.price', '[class*="price"]', '.product-price']
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_numeric = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                if price_numeric:
                    product['price'] = float(price_numeric)
                    product['price_text'] = price_text
                    break
        
        # Old price
        old_price_selectors = ['.old-price', '.original-price', '[class*="old-price"]']
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
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")


def main():
    """Main function for Selenium scraper."""
    parser = argparse.ArgumentParser(description='Selenium-based price scraper')
    parser.add_argument('--max-pages', type=int, default=3, help='Max pages to scrape')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    parser.add_argument('--url', help='Specific URL to scrape')
    
    args = parser.parse_args()
    
    scraper = None
    try:
        scraper = SeleniumScraper(headless=args.headless)
        products = scraper.scrape_5ka_catalog(
            category_url=args.url,
            max_pages=args.max_pages
        )
        
        if products:
            analyzer = PriceAnalyzer()
            analysis = analyzer.analyze_products(products, '5ka')
            analyzer.save_results(products, analysis, '5ka')
            print(f"\n✓ Successfully scraped and analyzed {len(products)} products")
        else:
            print("\n⚠ No products found. Check website structure.")
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    finally:
        if scraper:
            scraper.close()


if __name__ == '__main__':
    main()

