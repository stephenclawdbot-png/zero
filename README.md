# 🚀 Multi-Chain Alpha Trading Terminal

A comprehensive trading terminal for meme coins across **6 blockchains** with multi-interface support.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 🌐 Supported Chains

| Chain | Symbol | Status | Public RPC |
|-------|--------|--------|------------|
| ☀️ Solana | SOL | ✅ Active | `api.mainnet-beta.solana.com` |
| 🟡 BSC | BNB | ✅ Active | `bsc-dataseed.binance.org` |
| 💎 Ethereum | ETH | ✅ Active | `eth.llamarpc.com` |
| 🟣 Polygon | MATIC | ✅ Active | `polygon-rpc.com` |
| 🔵 Arbitrum | ARB | ✅ Active | `arb1.arbitrum.io/rpc` |
| 🔷 Base | BASE | ✅ Active | `mainnet.base.org` |

## ✨ Features

- 🔍 **Multi-Chain Scanner** - Scan one or ALL chains simultaneously
- 🎯 **Alpha Scoring** - ML-inspired algorithm (0-100) for gem detection
- 📊 **Market Cap Filtering** - Focus on $30K-$150K sweet spot
- 📱 **Multi-Interface** - CLI, Telegram Bot, Web Dashboard (coming)
- 🔔 **Smart Alerts** - Get notified when alpha opportunities arise
- 💼 **Wallet Tracking** - Monitor whale wallets across chains
- ⛓️ **EVM + Solana** - Native support for both ecosystems
- 🌐 **Public RPCs** - Works out of the box with free endpoints

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Configuration (Optional)

**Public RPCs are pre-configured** - no setup needed! But you can use custom RPCs:

```bash
# Optional: Custom RPCs for better performance
export SOLANA_RPC_URL="https://your-helius-endpoint.com"
export BSC_RPC_URL="https://your-bsc-endpoint.com"
export ETH_RPC_URL="https://your-eth-endpoint.com"

# Required for Telegram mode
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

**Get free custom RPCs:**
- [Helius](https://helius.dev) - Best for Solana
- [QuickNode](https://quicknode.com) - Multi-chain
- [Ankr](https://ankr.com/rpc) - Free tier available

## 📱 Usage

### Option 1: CLI Mode

```bash
# Interactive terminal (default: Solana)
python3 alpha_terminal.py

# Specific chain
python3 alpha_terminal.py --chain bsc
python3 alpha_terminal.py --chain ethereum
python3 alpha_terminal.py --chain arbitrum

# Scan all chains at once
python3 alpha_terminal.py --scan-all
```

**CLI Commands:**
```
1. Scan New Launches          - Scan current chain
2. Track Token               - Add token to watchlist
3. View Tracked Tokens       - See your watchlist
4. Multi-Chain Scanner       - Scan ALL chains
5. Switch Chain              - Change active chain
6. Token Info (EVM)          - Get ERC20 token details
7. Alpha Scanner Settings    - Configure filters
8. Exit
```

### Option 2: Telegram Bot Mode

```bash
# Requires TELEGRAM_BOT_TOKEN env var
export TELEGRAM_BOT_TOKEN="your_token_from_botfather"
python3 telegram_bot.py
```

**Bot Commands:**

| Command | Description |
|---------|-------------|
| `/start` | Welcome + chain status |
| `/chains` | Select active chain |
| `/scan` | Scan current chain |
| `/multiscan` | Scan ALL chains simultaneously |
| `/track <addr> <sym>` | Track a token |
| `/wallet <addr>` | Wallet analysis |
| `/alpha` | Get alpha picks |
| `/status` | Check all RPC statuses |
| `/help` | Show help |

**Example Telegram usage:**
```
/chains          → Select BSC
/scan            → Find BSC launches
/multiscan       → Find gems on ALL chains
/track 0xabc... CAKE "PancakeSwap"
```

### Option 3: Python Script

```python
from alpha_terminal import MultiChainAlphaTerminal, Chain

# Initialize terminal
terminal = MultiChainAlphaTerminal()

# Check all chain connections
for chain, config in terminal.chains.items():
    status = "✅" if config.connected else "❌"
    print(f"{status} {chain.value.upper()}")

# Switch to BSC
terminal.switch_chain(Chain.BSC)

# Scan for launches
launches = terminal.scan_new_launches()

# Calculate alpha scores
for token in launches:
    score = terminal.calculate_alpha_score(token)
    if score > 70:
        print(f"🔥 HIGH ALPHA: {token['symbol']} (Score: {score})")

# Multi-chain scan
for chain in [Chain.SOLANA, Chain.BSC, Chain.ETHEREUM]:
    launches = terminal.scan_new_launches(chain)
    print(f"Found {len(launches)} on {chain.value}")
```

## 🎯 Alpha Scoring Algorithm

The alpha score (0-100) considers:

| Factor | Weight | Description |
|--------|--------|-------------|
| Market Cap Range | 30% | $30K-$150K = optimal |
| Volume Ratio | 25% | Volume/MCAP > 0.5 = strong |
| Source Credibility | 20% | pump.fun / dexscreener |
| Chain Multiplier | 10% | SOL/BSC = +10, ETH/ARB = +5 |
| Time Freshness | 15% | Newer = higher |

**Alpha Tiers:**
- 🔥 **80-100:** Extreme alpha (rare)
- ⭐ **70-79:** High potential
- 📊 **50-69:** Medium potential
- ⚠️ **0-49:** Low potential / Risky

## 🔌 RPC Endpoints

### Default Public RPCs (Pre-configured)

These work out of the box but are rate-limited:

**Solana:**
- `https://api.mainnet-beta.solana.com`
- `https://rpc.ankr.com/solana`

**BSC:**
- `https://bsc-dataseed.binance.org`
- `https://bsc-dataseed1.defibit.io`
- `https://rpc.ankr.com/bsc`

**Ethereum:**
- `https://eth.llamarpc.com`
- `https://rpc.ankr.com/eth`

**Polygon:**
- `https://polygon-rpc.com`
- `https://rpc.ankr.com/polygon`

**Arbitrum:**
- `https://arb1.arbitrum.io/rpc`
- `https://rpc.ankr.com/arbitrum`

**Base:**
- `https://mainnet.base.org`
- `https://rpc.ankr.com/base`

### Custom RPCs (Recommended)

For production use, get dedicated RPCs:

| Provider | Chains | Free Tier |
|----------|--------|-----------|
| Helius | Solana | ✅ Yes |
| QuickNode | All | ✅ Yes |
| Ankr | All | ✅ Yes |
| Alchemy | All | ✅ Yes |

## 🛠️ Development

### Project Structure

```
SOLANA-ALPHA-TERMINAL/
├── alpha_terminal.py      # Main CLI + Multi-chain logic
├── telegram_bot.py         # Telegram Bot interface
├── config.py              # Chain configurations
├── requirements.txt       # Dependencies
├── README.md              # This file
└── PROJECT_SUMMARY.md     # Detailed docs
```

### Adding New Chains

To add a new EVM chain:

1. Edit `alpha_terminal.py`:

```python
class Chain(Enum):
    # ... existing chains ...
    AVALANCHE = "avalanche"  # Add new chain

PUBLIC_RPCS = {
    # ... existing RPCs ...
    Chain.AVALANCHE: [
        "https://api.avax.network/ext/bc/C/rpc",
        "https://rpc.ankr.com/avalanche",
    ],
}

EXPLORERS = {
    # ... existing explorers ...
    Chain.AVALANCHE: "https://snowtrace.io/token/",
}
```

2. Add chain emoji in `telegram_bot.py`:

```python
CHAIN_EMOJIS = {
    # ... existing ...
    Chain.AVALANCHE: "❄️",
}
```

### Integrating Real APIs

The codebase has placeholder methods for demo. To add real data:

**Edit `alpha_terminal.py`:**

```python
def scan_new_launches(self, chain: Optional[Chain] = None):
    """Your implementation"""
    
    # Example: DexScreener API
    if chain == Chain.SOLANA:
        response = requests.get(
            "https://api.dexscreener.com/latest/dex/search",
            params={"q": "solana"}
        )
    elif chain == Chain.BSC:
        response = requests.get(
            "https://api.dexscreener.com/latest/dex/search",
            params={"q": "bsc"}
        )
    
    data = response.json()
    launches = []
    
    for pair in data['pairs'][:50]:
        if self.is_new_launch(pair):
            launches.append({
                'address': pair['baseToken']['address'],
                'symbol': pair['baseToken']['symbol'],
                'name': pair['baseToken']['name'],
                'mcap': float(pair['marketCap']),
                'volume': float(pair['volume24h']),
                'chain': chain.value,
            })
    
    return launches
```

## 🔐 Security

- ⚠️ **Never commit private keys or API tokens**
- 🔑 Use environment variables for sensitive data
- 🛡️ This is a scanning/analytics tool, not a trading bot
- ⚠️ Always DYOR (Do Your Own Research)

## 📝 Roadmap

- [x] Multi-chain support (Solana, BSC, ETH, Polygon, Arbitrum, Base)
- [x] Public RPC auto-fallback
- [x] CLI interface
- [x] Telegram Bot
- [x] Alpha scoring algorithm
- [ ] Real-time WebSocket feeds
- [ ] Web Dashboard (Flask/FastAPI)
- [ ] Automated trading integration
- [ ] Holder analysis
- [ ] Whale wallet tracking

## 🤝 Contributing

Contributions welcome! Priority areas:

1. Real API integrations (DexScreener, Birdeye, Helius, Moralis)
2. WebSocket implementation for real-time data
3. Machine learning alpha prediction
4. Additional chain integrations (Avalanche, Fantom, etc.)

## ⚠️ Disclaimer

**NOT FINANCIAL ADVICE.** This tool is for educational purposes only.

- Meme coins are highly volatile
- Never risk more than you can afford to lose
- Always verify contract addresses
- Check for honeypots before buying
- Public RPCs have rate limits

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

**Built with ❤️ for the degen community**

⭐ Star this repo if you find it useful!

**GitHub:** https://github.com/stephenclawdbot-png/solana-alpha-terminal
