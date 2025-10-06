"""Configuration settings for the retail price scraper."""

import os
from typing import Dict, List

# Anti-detection settings
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
]

# Request delays (in seconds)
MIN_DELAY = 2
MAX_DELAY = 5

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5

# Headers
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# Timeout settings
REQUEST_TIMEOUT = 30

# Competitor configurations
COMPETITORS = {
    '5ka': {
        'name': 'Пятёрочка',
        'url': 'https://5ka.ru',
        'catalog_url': 'https://5ka.ru/catalog',
        'enabled': True
    }
}

# Output settings
OUTPUT_DIR = 'output'
OUTPUT_FORMAT = 'csv'  # csv, json, excel

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'

