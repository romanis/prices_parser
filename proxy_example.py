"""
Example of using proxies for additional anonymity.
This is an advanced feature for large-scale scraping.
"""

import random
from typing import List, Dict, Optional

import requests
import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config


class ProxyManager:
    """Manage proxy rotation for scraping."""
    
    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize proxy manager.
        
        Args:
            proxy_list: List of proxy URLs in format "http://ip:port" or "http://user:pass@ip:port"
        """
        self.proxy_list = proxy_list or []
        self.current_proxy = None
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the list."""
        if not self.proxy_list:
            return None
        return random.choice(self.proxy_list)
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """Get proxy dictionary for requests."""
        proxy = self.get_random_proxy()
        if proxy:
            return {
                'http': proxy,
                'https': proxy
            }
        return None


def create_session_with_proxy(proxy: Optional[str] = None) -> requests.Session:
    """
    Create a requests session with proxy support.
    
    Args:
        proxy: Proxy URL
        
    Returns:
        Configured session
    """
    session = cloudscraper.create_scraper()
    
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
    
    return session


def create_selenium_driver_with_proxy(proxy: Optional[str] = None, headless: bool = True) -> webdriver.Chrome:
    """
    Create Selenium driver with proxy support.
    
    Args:
        proxy: Proxy URL (format: ip:port or user:pass@ip:port)
        headless: Run in headless mode
        
    Returns:
        Chrome WebDriver with proxy
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    # Add proxy
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    # Anti-detection options
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Random user agent
    user_agent = random.choice(config.USER_AGENTS)
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


# Example proxy lists (these are placeholders - you need real proxies)
FREE_PROXY_EXAMPLES = [
    # Format: "http://ip:port"
    "http://45.67.89.123:8080",
    "http://123.45.67.89:3128",
]

AUTHENTICATED_PROXY_EXAMPLES = [
    # Format: "http://username:password@ip:port"
    "http://user:pass@proxy.example.com:8080",
]


def example_usage_requests():
    """Example: Using proxies with requests."""
    proxy_manager = ProxyManager(FREE_PROXY_EXAMPLES)
    
    session = requests.Session()
    session.proxies = proxy_manager.get_proxy_dict()
    
    # Make request through proxy
    response = session.get('https://5ka.ru')
    print(f"Status: {response.status_code}")


def example_usage_selenium():
    """Example: Using proxies with Selenium."""
    proxy = "45.67.89.123:8080"  # Replace with real proxy
    
    driver = create_selenium_driver_with_proxy(proxy=proxy, headless=True)
    driver.get('https://5ka.ru')
    print(f"Title: {driver.title}")
    driver.quit()


# Popular proxy services (not free, but reliable):
# - BrightData (formerly Luminati)
# - Oxylabs
# - Smartproxy
# - ProxyMesh
# - ScraperAPI (includes proxy + Cloudflare bypass)

# Free proxy sources (quality varies):
# - Free-proxy-list.net
# - ProxyScrape
# - PubProxy
# - Note: Free proxies are often slow and unreliable

"""
Tips for using proxies:

1. Residential proxies are better than datacenter proxies for avoiding detection
2. Rotate proxies frequently to avoid IP bans
3. Test proxies before using them
4. Keep a pool of working proxies
5. Handle proxy failures gracefully (retry with different proxy)
6. Consider using proxy services that handle rotation automatically
7. Some proxy services offer built-in Cloudflare bypass

Example of testing a proxy:
"""

def test_proxy(proxy: str, test_url: str = 'https://httpbin.org/ip') -> bool:
    """
    Test if a proxy is working.
    
    Args:
        proxy: Proxy URL
        test_url: URL to test with
        
    Returns:
        True if proxy works, False otherwise
    """
    try:
        proxies = {
            'http': proxy,
            'https': proxy
        }
        response = requests.get(test_url, proxies=proxies, timeout=10)
        return response.status_code == 200
    except:
        return False


if __name__ == '__main__':
    print("Proxy configuration examples loaded.")
    print("\nTo use proxies:")
    print("1. Get proxies from a reliable service")
    print("2. Add them to the proxy_list in ProxyManager")
    print("3. Modify scraper.py to use ProxyManager")
    print("\nNote: This is an advanced feature for users who need it.")

