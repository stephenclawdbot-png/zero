"""
Multi-Chain Configuration for Alpha Terminal
Supports: Solana, BSC, Ethereum, Polygon, Arbitrum, Base
"""

import os
from enum import Enum

class Chain(Enum):
    """Supported blockchain networks"""
    SOLANA = "solana"
    BSC = "bsc"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    BASE = "base"

# Public RPC Endpoints (free, rate-limited)
# These work out of the box but have rate limits
# For production, use custom RPCs from Helius, QuickNode, Ankr, etc.
PUBLIC_RPCS = {
    Chain.SOLANA: [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com",
        "https://rpc.ankr.com/solana",
    ],
    Chain.BSC: [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io",
        "https://bsc-dataseed1.ninicoin.io",
        "https://rpc.ankr.com/bsc",
    ],
    Chain.ETHEREUM: [
        "https://eth.llamarpc.com",
        "https://rpc.ankr.com/eth",
        "https://ethereum.publicnode.com",
    ],
    Chain.POLYGON: [
        "https://polygon.llamarpc.com",
        "https://rpc.ankr.com/polygon",
        "https://polygon-rpc.com",
    ],
    Chain.ARBITRUM: [
        "https://arbitrum.llamarpc.com",
        "https://rpc.ankr.com/arbitrum",
        "https://arb1.arbitrum.io/rpc",
    ],
    Chain.BASE: [
        "https://base.llamarpc.com",
        "https://rpc.ankr.com/base",
        "https://mainnet.base.org",
    ],
}

# Chain explorers
EXPLORERS = {
    Chain.SOLANA: "https://solscan.io/token/",
    Chain.BSC: "https://bscscan.com/token/",
    Chain.ETHEREUM: "https://etherscan.io/token/",
    Chain.POLYGON: "https://polygonscan.com/token/",
    Chain.ARBITRUM: "https://arbiscan.io/token/",
    Chain.BASE: "https://basescan.org/token/",
}

# Chain IDs (for EVM chains)
CHAIN_IDS = {
    Chain.SOLANA: None,  # Solana doesn't use EVM chain ID
    Chain.BSC: 56,
    Chain.ETHEREUM: 1,
    Chain.POLYGON: 137,
    Chain.ARBITRUM: 42161,
    Chain.BASE: 8453,
}

# Chain native symbols
NATIVE_SYMBOLS = {
    Chain.SOLANA: "SOL",
    Chain.BSC: "BNB",
    Chain.ETHEREUM: "ETH",
    Chain.POLYGON: "MATIC",
    Chain.ARBITRUM: "ETH",
    Chain.BASE: "ETH",
}

# Custom RPC Configuration (override public RPCs)
# Set via environment variables or edit below
CUSTOM_RPCS = {
    Chain.SOLANA: os.getenv('SOLANA_RPC_URL'),
    Chain.BSC: os.getenv('BSC_RPC_URL'),
    Chain.ETHEREUM: os.getenv('ETH_RPC_URL', os.getenv('ETHEREUM_RPC_URL')),
    Chain.POLYGON: os.getenv('POLYGON_RPC_URL'),
    Chain.ARBITRUM: os.getenv('ARBITRUM_RPC_URL'),
    Chain.BASE: os.getenv('BASE_RPC_URL'),
}

# Telegram Bot Configuration  
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Alpha Scanner Settings
ALPHA_CONFIG = {
    'min_market_cap': 30000,      # $30K
    'max_market_cap': 150000,     # $150K
    'min_volume': 5000,           # $5K
    'alert_threshold': 70,        # Alpha score to alert
    'scan_interval': 300,         # 5 minutes
}

# API Endpoints (placeholders - implement real integrations)
API_ENDPOINTS = {
    'dexscreener': 'https://api.dexscreener.com/latest/dex/search',
    'birdeye': 'https://public-api.birdeye.so/public/tokenlist',
    'helius': 'https://api.helius.xyz/v0',  # Requires API key
    'moralis': 'https://deep-index.moralis.io/api/v2',  # Requires API key
}

# Get active RPC for chain
def get_rpc_for_chain(chain: Chain) -> str:
    """Get RPC URL for chain (custom or public fallback)"""
    # Check custom RPC first
    custom = CUSTOM_RPCS.get(chain)
    if custom:
        return custom
    
    # Return first public RPC
    public = PUBLIC_RPCS.get(chain, [])
    return public[0] if public else None

# Chain display info
def get_chain_info(chain: Chain) -> dict:
    """Get display info for chain"""
    return {
        'name': chain.value.upper(),
        'symbol': NATIVE_SYMBOLS.get(chain, 'UNKNOWN'),
        'chain_id': CHAIN_IDS.get(chain),
        'explorer': EXPLORERS.get(chain, ''),
        'rpc': get_rpc_for_chain(chain),
    }
