"""
Configuration for Solana Alpha Terminal
"""

import os

# Solana RPC Configuration
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
# For better performance, use:
# - Helius: https://helius.dev (free tier available)
# - QuickNode: https://quicknode.com
# - Alchemy: https://alchemy.com

# Telegram Bot Configuration  
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Alpha Scanner Settings
ALPHA_CONFIG = {
    'min_market_cap': 30000,      # $30K
    'max_market_cap': 150000,     # $150K
    'min_volume': 5000,           # $5K
    'alert_threshold': 70,          # Alpha score to alert
    'scan_interval': 300,           # 5 minutes
}

# API Endpoints (placeholders - implement real integrations)
API_ENDPOINTS = {
    'dexscreener': 'https://api.dexscreener.com/latest/dex/search',
    'birdeye': 'https://public-api.birdeye.so/public/tokenlist',
    'helius': 'https://api.helius.xyz/v0',  # Requires API key
}

