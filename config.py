import os
from pathlib import Path

# Load .env file if exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Algolia Configuration
ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID', 'your-ID')
ALGOLIA_ADMIN_KEY = os.getenv('ALGOLIA_API_KEY', 'your-key')
ALGOLIA_INDEX_NAME = os.getenv('ALGOLIA_INDEX_NAME', 'index-name')

# Stock thresholds
LOW_STOCK_LIMIT = int(os.getenv('LOW_STOCK_LIMIT', '10'))
DEAD_STOCK_LIMIT = int(os.getenv('DEAD_STOCK_LIMIT', '0'))
CRITICAL_STOCK_LIMIT = int(os.getenv('CRITICAL_STOCK_LIMIT', '5'))
