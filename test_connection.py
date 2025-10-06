#!/usr/bin/env python3
"""
Test script to verify connectivity and basic setup.
Run this before attempting full scraping.
"""

import sys
import requests
import cloudscraper

import config


def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    try:
        import requests
        import bs4
        import lxml
        import fake_useragent
        import selenium
        import pandas
        import cloudscraper
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {str(e)}")
        print("Run: pip install -r requirements.txt")
        return False


def test_basic_request():
    """Test basic HTTP request."""
    print("\nTesting basic HTTP request...")
    try:
        response = requests.get('https://httpbin.org/user-agent', timeout=10)
        if response.status_code == 200:
            print(f"✓ Basic HTTP request works")
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Request failed: {str(e)}")
        return False


def test_cloudscraper():
    """Test cloudscraper."""
    print("\nTesting cloudscraper...")
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get('https://httpbin.org/user-agent', timeout=10)
        if response.status_code == 200:
            print("✓ Cloudscraper works")
            return True
        else:
            print(f"✗ Cloudscraper failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cloudscraper failed: {str(e)}")
        return False


def test_target_website():
    """Test connection to target website."""
    print("\nTesting connection to 5ka.ru...")
    try:
        scraper = cloudscraper.create_scraper()
        headers = config.DEFAULT_HEADERS.copy()
        headers['User-Agent'] = config.USER_AGENTS[0]
        
        response = scraper.get(
            'https://5ka.ru',
            headers=headers,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            print("✓ Successfully connected to 5ka.ru")
            print(f"  Response length: {len(response.text)} bytes")
            return True
        elif response.status_code == 403:
            print("✗ Access forbidden (403) - may need better headers or proxy")
            return False
        elif response.status_code == 503:
            print("✗ Service unavailable (503) - Cloudflare may be blocking")
            print("  Cloudscraper should handle this, but it might need updates")
            return False
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Connection timeout - website may be slow or blocking")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - check internet connection")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False


def test_output_directory():
    """Test output directory."""
    print("\nTesting output directory...")
    import os
    
    if os.path.exists(config.OUTPUT_DIR):
        print(f"✓ Output directory exists: {config.OUTPUT_DIR}")
        return True
    else:
        try:
            os.makedirs(config.OUTPUT_DIR)
            print(f"✓ Created output directory: {config.OUTPUT_DIR}")
            return True
        except Exception as e:
            print(f"✗ Failed to create output directory: {str(e)}")
            return False


def test_selenium_driver():
    """Test Selenium WebDriver setup."""
    print("\nTesting Selenium WebDriver (optional)...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("  Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get('https://httpbin.org/user-agent')
        driver.quit()
        
        print("✓ Selenium WebDriver works")
        return True
    except Exception as e:
        print(f"⚠ Selenium setup failed: {str(e)}")
        print("  This is optional - basic scraper will still work")
        return None  # Not critical


def main():
    """Run all tests."""
    print("=" * 70)
    print("RETAIL PRICE SCRAPER - CONNECTION TEST")
    print("=" * 70)
    print()
    
    results = []
    
    # Run tests
    results.append(("Package imports", test_imports()))
    results.append(("Basic HTTP request", test_basic_request()))
    results.append(("Cloudscraper", test_cloudscraper()))
    results.append(("Output directory", test_output_directory()))
    results.append(("Target website (5ka.ru)", test_target_website()))
    results.append(("Selenium (optional)", test_selenium_driver()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    optional = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP (optional)"
        print(f"{status:20} {test_name}")
    
    print()
    print(f"Passed:  {passed}")
    print(f"Failed:  {failed}")
    print(f"Skipped: {optional}")
    print()
    
    if failed == 0:
        print("✓ All critical tests passed! You're ready to scrape.")
        print("\nNext steps:")
        print("  python main.py              # Run the scraper")
        print("  python example_usage.py     # Try examples")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues above before scraping.")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)

