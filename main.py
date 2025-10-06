#!/usr/bin/env python3
"""
Main script to run the retail price scraper and analyzer.
"""

import argparse
import logging
import sys

from scraper import RetailScraper
from price_analyzer import PriceAnalyzer
import config


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
    """Main function to orchestrate scraping and analysis."""
    parser = argparse.ArgumentParser(
        description='Scrape and analyze retail competitor prices'
    )
    parser.add_argument(
        '--competitor',
        default='5ka',
        choices=['5ka'],
        help='Competitor to scrape (default: 5ka)'
    )
    parser.add_argument(
        '--url',
        help='Specific URL to scrape (optional, uses default catalog if not provided)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=5,
        help='Maximum number of pages to scrape (default: 5)'
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
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    config.OUTPUT_FORMAT = args.output_format
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("RETAIL PRICE SCRAPER - STARTING")
    logger.info("=" * 70)
    logger.info(f"Competitor: {args.competitor}")
    logger.info(f"Max pages: {args.max_pages}")
    logger.info(f"Output format: {args.output_format}")
    logger.info(f"Using cloudscraper: {args.use_cloudscraper}")
    
    try:
        # Initialize scraper
        scraper = RetailScraper(use_cloudscraper=args.use_cloudscraper)
        
        # Scrape products
        if args.competitor == '5ka':
            logger.info("\nStarting to scrape 5ka.ru...")
            products = scraper.scrape_5ka_catalog(
                category_url=args.url,
                max_pages=args.max_pages
            )
        else:
            logger.error(f"Unsupported competitor: {args.competitor}")
            return 1
        
        # Close scraper session
        scraper.close()
        
        if not products:
            logger.warning("No products were scraped. Please check the website structure.")
            logger.info("\nTip: The website structure may have changed. You might need to:")
            logger.info("  1. Inspect the website HTML manually")
            logger.info("  2. Update the CSS selectors in scraper.py")
            logger.info("  3. Check if the website requires JavaScript (consider using Selenium)")
            return 1
        
        logger.info(f"\n✓ Successfully scraped {len(products)} products")
        
        # Analyze products
        logger.info("\nAnalyzing product prices...")
        analyzer = PriceAnalyzer()
        analysis = analyzer.analyze_products(products, args.competitor)
        
        # Find best deals
        best_deals = analyzer.find_best_deals(products, top_n=10)
        if best_deals:
            logger.info("\nTop 10 Best Deals:")
            for i, deal in enumerate(best_deals, 1):
                logger.info(
                    f"  {i}. {deal.get('name', 'Unknown')[:50]}: "
                    f"{deal['price']:.2f} ₽ (was {deal['old_price']:.2f} ₽, "
                    f"save {deal['discount_percent']:.1f}%)"
                )
        
        # Save results
        logger.info("\nSaving results...")
        analyzer.save_results(products, analysis, args.competitor)
        
        logger.info("\n" + "=" * 70)
        logger.info("SCRAPING COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\nAn error occurred: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

