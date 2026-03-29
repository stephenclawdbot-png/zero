# 🚀 Solana Alpha Trading Terminal

A comprehensive trading terminal for Solana meme coins with multi-interface support (CLI, Telegram Bot, Web Dashboard).

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## ✨ Features

- 🔍 **New Launch Scanner** - Auto-scan for new token launches on Pump.fun & DexScreener
- 🎯 **Alpha Scoring** - ML-inspired scoring algorithm for early gems
- 📊 **Market Cap Filtering** - Focus on $30K-$150K sweet spot
- 📱 **Multi-Interface** - CLI, Telegram Bot, Web Dashboard
- 🔔 **Smart Alerts** - Get notified when alpha opportunities arise
- 💼 **Wallet Tracking** - Monitor whale wallets and smart money
- ⛓️ **Solana Native** - Built specifically for SOL ecosystem

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set environment variables or edit `config.py`:

```bash
# Solana RPC ( REQUIRED )
# Get free RPC from helius.dev or quicknode.com
export SOLANA_RPC_URL="https://your-rpc-url.com"

# Telegram Bot Token (for Telegram mode)
# Get from @BotFather on Telegram
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

## 📱 Usage

### Option 1: CLI Mode

```bash
# Interactive terminal
python3 alpha_terminal.py

# With custom RPC
python3 alpha_terminal.py --rpc https://your-rpc.com
```

**Commands:**
- `1` - Scan for new launches
- `2` - Track a token
- `3` - View tracked tokens
- `4` - Alpha scanner settings
- `5` - Check RPC status
- `6` - Exit

### Option 2: Telegram Bot Mode

```bash
# Requires TELEGRAM_BOT_TOKEN env var
python3 telegram_bot.py
```

**Bot Commands:**
- `/start` - Welcome message
- `/scan` - Scan for new launches
- `/track <address> <symbol>` - Track a token
- `/wallet <address>` - Analyze wallet
- `/alpha` - Get alpha picks
- `/status` - Check RPC connection
- `/help` - Show help

### Option 3: Standalone Script Mode

```python
from alpha_terminal import SolanaAlphaTerminal

# Initialize terminal
terminal = SolanaAlphaTerminal(rpc_url="your-rpc-url")

# Check connection
if terminal.check_rpc_connection():
    print("✅ Connected to Solana")

# Scan for launches
launches = terminal.scan_new_launches()

# Calculate alpha score
for token in launches:
    score = terminal.calculate_alpha_score(token)
    if score > 70:
        print(f"🔥 HIGH ALPHA: {token['name']} (Score: {score})")
```

## 🎯 Alpha Scoring Algorithm

The alpha score (0-100) considers:

| Factor | Weight | Description |
|--------|--------|-------------|
| Market Cap Range | 30% | $30K-$150K = optimal |
| Volume Ratio | 25% | Volume/MCAP > 0.5 |
| Source Credibility | 20% | pump.fun / dexscreener |
| Time Freshness | 10% | Newer = higher |
| Base Score | 15% | Always applied |

**Alpha Tiers:**
- 🔥 **80-100:** Extreme alpha (rare)
- ⭐ **70-79:** High potential
- 📊 **50-69:** Medium potential
- ⚠️ **0-49:** Low potential / Risky

## 🔌 RPC Configuration

**Placeholder RPC:** `https://api.mainnet-beta.solana.com` (public, rate-limited)

**Recommended RPCs (Free Tiers):**

| Provider | URL | Free Tier |
|----------|-----|-----------|
| Helius | helius.dev | ✅ Free |
| QuickNode | quicknode.com | ✅ Free |
| Alchemy | alchemy.com | ✅ Free |

**Get Started:**
1. Sign up at helius.dev
2. Create new Solana endpoint
3. Copy HTTPS URL
4. Set as `SOLANA_RPC_URL`

## 🛠️ Development

### Project Structure

```
SOLANA-ALPHA-TERMINAL/
├── alpha_terminal.py      # Main terminal (CLI)
├── telegram_bot.py         # Telegram Bot interface
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── README.md              # This file
└── tests/                 # Unit tests (optional)
```

### Adding New Features

**To integrate real APIs:**

Edit `alpha_terminal.py` and replace placeholder methods:

```python
# In SolanaAlphaTerminal class

def scan_new_launches(self) -> List[Dict]:
    """Your implementation here"""
    
    # Example: DexScreener API
    response = requests.get(
        "https://api.dexscreener.com/latest/dex/search",
        params={"q": "solana"}
    )
    data = response.json()
    
    # Parse and filter results
    launches = []
    for pair in data['pairs'][:50]:
        if self.is_new_launch(pair):
            launches.append(pair)
    
    return launches

def get_holder_analysis(self, token_address: str):
    """Analyze holder distribution"""
    # Integrate with Helius API
    pass
```

## 🔐 Security

- ⚠️ **Never commit private keys or API tokens**
- 🔑 Use environment variables for sensitive data
- 🛡️ This is a scanning tool, not a trading bot
- ⚠️ Always DYOR (Do Your Own Research)

## 📝 Roadmap

- [x] Basic terminal structure
- [x] Telegram Bot interface
- [ ] Web Dashboard (Flask/FastAPI)
- [ ] Real-time WebSocket feeds
- [ ] Advanced TA indicators
- [ ] Holder analysis
- [ ] Whale wallet tracking
- [ ] Automated alerts
- [ ] Backtesting framework

## 🤝 Contributing

Contributions welcome! Areas needing help:

1. Real API integrations (DexScreener, Birdeye, Helius)
2. WebSocket implementation for real-time data
3. Machine learning alpha prediction
4. Additional exchange integrations

## ⚠️ Disclaimer

**NOT FINANCIAL ADVICE.** This tool is for educational purposes only.

- Meme coins are highly volatile
- Never risk more than you can afford to lose
- Always verify contract addresses
- Check for honeypots before buying

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

**Built with ❤️ for the Solana community**

Star ⭐ this repo if you find it useful!
