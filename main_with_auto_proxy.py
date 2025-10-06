#!/usr/bin/env python3
"""
Main script with automatic IP rotation on block detection.
"""

import argparse
import logging
import sys
import os

from scraper_with_auto_proxy import SmartRetailScraper
from price_analyzer import PriceAnalyzer
import config


def load_proxies_from_file(filepath: str) -> list:
    """
    Load proxies from a text file.
    
    Format (one per line):
        http://ip:port
        http://username:password@ip:port
        socks5://ip:port
    """
    proxies = []
    
    if not os.path.exists(filepath):
        print(f"⚠️  Proxy file not found: {filepath}")
        return proxies
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                proxies.append(line)
    
    return proxies


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )


def main():
    """Main function with automatic IP rotation."""
    parser = argparse.ArgumentParser(
        description='Scrape retail prices with automatic IP rotation on block detection'
    )
    parser.add_argument(
        '--competitor',
        default='5ka',
        choices=['5ka'],
        help='Competitor to scrape (default: 5ka)'
    )
    parser.add_argument(
        '--url',
        help='Specific URL to scrape (optional)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=5,
        help='Maximum number of pages to scrape (default: 5)'
    )
    parser.add_argument(
        '--proxy-file',
        help='Path to file containing proxy list (one per line)'
    )
    parser.add_argument(
        '--proxy-list',
        nargs='+',
        help='List of proxies directly (e.g., http://proxy1:8080 http://proxy2:8080)'
    )
    parser.add_argument(
        '--no-proxy',
        action='store_true',
        help='Disable proxy usage (direct connection only)'
    )
    parser.add_argument(
        '--use-cloudscraper',
        action='store_true',
        default=True,
        help='Use cloudscraper to bypass Cloudflare (default: True)'
    )
    parser.add_argument(
        '--output-format',
        choices=['csv', 'json', 'excel', 'all'],
        default='csv',
        help='Output format for results (default: csv)'
    )
    parser.add_argument(
        '--no-auto-rotate',
        action='store_true',
        help='Disable automatic IP rotation on block (manual retry only)'
    )
    
    args = parser.parse_args()
    
    # Override config
    config.OUTPUT_FORMAT = args.output_format
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Header
    print("\n" + "=" * 70)
    print("RETAIL PRICE SCRAPER - WITH AUTOMATIC IP ROTATION")
    print("=" * 70)
    print(f"Competitor:       {args.competitor}")
    print(f"Max pages:        {args.max_pages}")
    print(f"Output format:    {args.output_format}")
    print(f"Cloudscraper:     {args.use_cloudscraper}")
    print(f"Auto IP Rotate:   {not args.no_auto_rotate}")
    
    # Load proxies
    proxy_list = []
    
    if args.no_proxy:
        print(f"Proxy usage:      DISABLED (direct connection)")
        logger.warning("⚠️  Running without proxies - higher risk of being blocked!")
    else:
        # Load from file
        if args.proxy_file:
            proxy_list = load_proxies_from_file(args.proxy_file)
            print(f"Proxy file:       {args.proxy_file}")
            print(f"Proxies loaded:   {len(proxy_list)}")
        
        # Load from command line
        elif args.proxy_list:
            proxy_list = args.proxy_list
            print(f"Proxies loaded:   {len(proxy_list)} (from command line)")
        
        else:
            print(f"Proxy usage:      NONE (no proxies provided)")
            logger.warning("⚠️  No proxies provided. For better results, use --proxy-file or --proxy-list")
            logger.warning("⚠️  See PROXY_GUIDE.md for how to get proxies")
    
    print("=" * 70 + "\n")
    
    try:
        # Initialize scraper with automatic IP rotation
        scraper = SmartRetailScraper(
            proxy_list=proxy_list if proxy_list else None,
            use_cloudscraper=args.use_cloudscraper,
            auto_rotate_on_block=not args.no_auto_rotate
        )
        
        # Scrape products
        logger.info("Starting to scrape...")
        if args.competitor == '5ka':
            products = scraper.scrape_5ka_catalog(
                category_url=args.url,
                max_pages=args.max_pages
            )
        else:
            logger.error(f"Unsupported competitor: {args.competitor}")
            return 1
        
        # Close scraper and show stats
        scraper.close()
        
        if not products:
            logger.warning("No products were scraped.")
            logger.info("\nPossible reasons:")
            logger.info("  1. Website structure has changed - update CSS selectors")
            logger.info("  2. All proxies were blocked - try different proxies")
            logger.info("  3. Website requires JavaScript - use selenium_scraper.py")
            logger.info("  4. Strong bot protection - may need residential proxies")
            return 1
        
        logger.info(f"\n✓ Successfully scraped {len(products)} products")
        
        # Analyze products
        logger.info("\nAnalyzing product prices...")
        analyzer = PriceAnalyzer()
        analysis = analyzer.analyze_products(products, args.competitor)
        
        # Find best deals
        best_deals = analyzer.find_best_deals(products, top_n=10)
        if best_deals:
            print("\n" + "=" * 70)
            print("TOP 10 BEST DEALS")
            print("=" * 70)
            for i, deal in enumerate(best_deals, 1):
                print(f"{i:2}. {deal.get('name', 'Unknown')[:50]}")
                print(f"    {deal['price']:.2f} ₽ (was {deal['old_price']:.2f} ₽, "
                      f"save {deal['discount_percent']:.1f}%)")
        
        # Save results
        logger.info("\nSaving results...")
        analyzer.save_results(products, analysis, args.competitor)
        
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\nAn error occurred: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

