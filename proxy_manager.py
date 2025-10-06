"""
Automatic proxy rotation manager with block detection and IP switching.
"""

import random
import logging
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests


@dataclass
class ProxyInfo:
    """Information about a proxy."""
    url: str
    protocol: str = 'http'  # http, https, socks5
    failures: int = 0
    last_used: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    response_time: float = 0.0
    is_working: bool = True
    blocked_until: Optional[datetime] = None
    
    def __post_init__(self):
        # Parse proxy URL to determine protocol
        if self.url.startswith('socks5://'):
            self.protocol = 'socks5'
        elif self.url.startswith('https://'):
            self.protocol = 'https'
        else:
            self.protocol = 'http'


class ProxyRotationManager:
    """
    Manages automatic proxy rotation with block detection.
    Automatically switches IP when parser is blocked.
    """
    
    def __init__(
        self,
        proxy_list: Optional[List[str]] = None,
        max_failures: int = 3,
        cooldown_time: int = 300,  # 5 minutes
        test_on_init: bool = True
    ):
        """
        Initialize proxy manager.
        
        Args:
            proxy_list: List of proxy URLs
            max_failures: Max failures before marking proxy as bad
            cooldown_time: Seconds to wait before retrying failed proxy
            test_on_init: Test proxies on initialization
        """
        self.logger = logging.getLogger(__name__)
        self.max_failures = max_failures
        self.cooldown_time = cooldown_time
        
        # Initialize proxies
        self.proxies: List[ProxyInfo] = []
        if proxy_list:
            for proxy_url in proxy_list:
                self.proxies.append(ProxyInfo(url=proxy_url))
        
        self.current_proxy: Optional[ProxyInfo] = None
        self.block_detected = False
        
        if test_on_init and self.proxies:
            self.logger.info("Testing proxies on initialization...")
            self.test_all_proxies()
    
    def add_proxy(self, proxy_url: str):
        """Add a new proxy to the pool."""
        proxy_info = ProxyInfo(url=proxy_url)
        self.proxies.append(proxy_info)
        self.logger.info(f"Added proxy: {proxy_url}")
    
    def add_proxies_from_file(self, filepath: str):
        """Load proxies from a text file (one per line)."""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    proxy_url = line.strip()
                    if proxy_url and not proxy_url.startswith('#'):
                        self.add_proxy(proxy_url)
            self.logger.info(f"Loaded {len(self.proxies)} proxies from {filepath}")
        except FileNotFoundError:
            self.logger.error(f"Proxy file not found: {filepath}")
    
    def get_working_proxies(self) -> List[ProxyInfo]:
        """Get list of currently working proxies."""
        now = datetime.now()
        working = []
        
        for proxy in self.proxies:
            # Skip if too many failures
            if proxy.failures >= self.max_failures:
                continue
            
            # Skip if in cooldown period
            if proxy.blocked_until and proxy.blocked_until > now:
                continue
            
            if proxy.is_working:
                working.append(proxy)
        
        return working
    
    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """
        Get next proxy to use.
        Uses weighted random selection based on success rate.
        """
        working_proxies = self.get_working_proxies()
        
        if not working_proxies:
            self.logger.warning("No working proxies available!")
            return None
        
        # Weight by inverse of failures and response time
        weights = []
        for proxy in working_proxies:
            # Lower failures and faster response = higher weight
            weight = 1.0 / (1 + proxy.failures)
            if proxy.response_time > 0:
                weight *= 1.0 / (1 + proxy.response_time / 10)
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
            self.current_proxy = random.choices(working_proxies, weights=weights)[0]
        else:
            self.current_proxy = random.choice(working_proxies)
        
        self.current_proxy.last_used = datetime.now()
        return self.current_proxy
    
    def get_proxy_dict(self, proxy: Optional[ProxyInfo] = None) -> Optional[Dict[str, str]]:
        """
        Get proxy dictionary for requests.
        
        Args:
            proxy: Specific proxy to use, or None to get next proxy
            
        Returns:
            Dictionary with http/https proxy URLs
        """
        if proxy is None:
            proxy = self.get_next_proxy()
        
        if proxy is None:
            return None
        
        return {
            'http': proxy.url,
            'https': proxy.url
        }
    
    def test_proxy(self, proxy: ProxyInfo, test_url: str = 'https://httpbin.org/ip', timeout: int = 10) -> bool:
        """
        Test if a proxy is working.
        
        Args:
            proxy: Proxy to test
            test_url: URL to test with
            timeout: Request timeout
            
        Returns:
            True if proxy works
        """
        try:
            proxies = {
                'http': proxy.url,
                'https': proxy.url
            }
            
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                proxy.is_working = True
                proxy.response_time = response_time
                proxy.failures = 0
                self.logger.info(f"✓ Proxy working: {proxy.url} ({response_time:.2f}s)")
                return True
            else:
                self.logger.warning(f"✗ Proxy returned {response.status_code}: {proxy.url}")
                return False
                
        except Exception as e:
            self.logger.warning(f"✗ Proxy failed: {proxy.url} - {str(e)}")
            return False
    
    def test_all_proxies(self):
        """Test all proxies and update their status."""
        self.logger.info(f"Testing {len(self.proxies)} proxies...")
        
        working_count = 0
        for proxy in self.proxies:
            if self.test_proxy(proxy):
                working_count += 1
        
        self.logger.info(f"Working proxies: {working_count}/{len(self.proxies)}")
    
    def mark_proxy_failed(self, proxy: Optional[ProxyInfo] = None, cooldown: bool = True):
        """
        Mark a proxy as failed.
        
        Args:
            proxy: Proxy that failed, or None to use current
            cooldown: Whether to put proxy in cooldown
        """
        if proxy is None:
            proxy = self.current_proxy
        
        if proxy is None:
            return
        
        proxy.failures += 1
        proxy.last_failure = datetime.now()
        
        if cooldown:
            proxy.blocked_until = datetime.now() + timedelta(seconds=self.cooldown_time)
        
        if proxy.failures >= self.max_failures:
            proxy.is_working = False
            self.logger.warning(f"Proxy marked as not working after {proxy.failures} failures: {proxy.url}")
        else:
            self.logger.info(f"Proxy failure {proxy.failures}/{self.max_failures}: {proxy.url}")
    
    def mark_proxy_success(self, proxy: Optional[ProxyInfo] = None):
        """Mark a proxy as successful."""
        if proxy is None:
            proxy = self.current_proxy
        
        if proxy is None:
            return
        
        # Reduce failure count on success
        if proxy.failures > 0:
            proxy.failures = max(0, proxy.failures - 1)
        
        proxy.is_working = True
        proxy.blocked_until = None
    
    def detect_block(self, response: requests.Response) -> bool:
        """
        Detect if request was blocked.
        
        Args:
            response: Response object
            
        Returns:
            True if block detected
        """
        # Check status codes
        if response.status_code in [403, 429, 503]:
            self.logger.warning(f"Block detected: Status {response.status_code}")
            self.block_detected = True
            return True
        
        # Check for common block patterns in response
        content = response.text.lower()
        block_patterns = [
            'access denied',
            'blocked',
            'captcha',
            'cloudflare',
            'security check',
            'rate limit',
            'too many requests',
            'forbidden',
            'bot detection'
        ]
        
        for pattern in block_patterns:
            if pattern in content:
                self.logger.warning(f"Block detected: Pattern '{pattern}' found in response")
                self.block_detected = True
                return True
        
        self.block_detected = False
        return False
    
    def handle_block(self, response: Optional[requests.Response] = None) -> ProxyInfo:
        """
        Handle block detection and switch to new proxy.
        
        Args:
            response: Response that triggered block detection
            
        Returns:
            New proxy to use
        """
        self.logger.warning("🔄 BLOCK DETECTED - Switching IP address...")
        
        # Mark current proxy as failed
        if self.current_proxy:
            self.mark_proxy_failed(self.current_proxy, cooldown=True)
            old_ip = self.current_proxy.url
        else:
            old_ip = "direct connection"
        
        # Get new proxy
        new_proxy = self.get_next_proxy()
        
        if new_proxy:
            self.logger.info(f"✓ Switched from {old_ip} to {new_proxy.url}")
        else:
            self.logger.error("✗ No working proxies available!")
        
        return new_proxy
    
    def get_stats(self) -> Dict:
        """Get statistics about proxy pool."""
        total = len(self.proxies)
        working = len([p for p in self.proxies if p.is_working])
        failed = len([p for p in self.proxies if p.failures >= self.max_failures])
        
        avg_response_time = 0
        if working > 0:
            response_times = [p.response_time for p in self.proxies if p.is_working and p.response_time > 0]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            'total_proxies': total,
            'working_proxies': working,
            'failed_proxies': failed,
            'average_response_time': avg_response_time,
            'current_proxy': self.current_proxy.url if self.current_proxy else None
        }
    
    def print_stats(self):
        """Print proxy pool statistics."""
        stats = self.get_stats()
        print("\n" + "=" * 70)
        print("PROXY POOL STATISTICS")
        print("=" * 70)
        print(f"Total Proxies:        {stats['total_proxies']}")
        print(f"Working Proxies:      {stats['working_proxies']}")
        print(f"Failed Proxies:       {stats['failed_proxies']}")
        print(f"Avg Response Time:    {stats['average_response_time']:.2f}s")
        print(f"Current Proxy:        {stats['current_proxy']}")
        print("=" * 70)


# Example proxy sources for demonstration
EXAMPLE_FREE_PROXIES = [
    # These are examples - replace with real working proxies
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:3128",
]

EXAMPLE_AUTHENTICATED_PROXIES = [
    # Format: http://username:password@host:port
    "http://user:pass@premium-proxy1.com:8080",
    "http://user:pass@premium-proxy2.com:8080",
]


if __name__ == '__main__':
    """Test proxy manager functionality."""
    
    # Example usage
    manager = ProxyRotationManager(
        proxy_list=EXAMPLE_FREE_PROXIES,
        max_failures=3,
        cooldown_time=300,
        test_on_init=False  # Set to True to test real proxies
    )
    
    print("Proxy manager initialized")
    print(f"Loaded {len(manager.proxies)} proxies")
    
    # Get next proxy
    proxy = manager.get_next_proxy()
    if proxy:
        print(f"\nNext proxy: {proxy.url}")
        
        # Simulate successful request
        manager.mark_proxy_success(proxy)
        print("Marked as success")
        
        # Simulate failure
        manager.mark_proxy_failed(proxy)
        print("Marked as failed")
        
        # Get another proxy
        proxy2 = manager.get_next_proxy()
        print(f"Next proxy: {proxy2.url}")
    
    # Show stats
    manager.print_stats()

