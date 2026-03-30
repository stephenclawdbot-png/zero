# Zero - Multi-Chain Crypto Trading Terminal & Alpha Scanner

> **From 0 to hero** — The open-source trading terminal for Solana, BSC, Ethereum, and more.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)

**Zero** is a free, open-source crypto trading terminal and meme coin scanner supporting **6 blockchains** with integrated Telegram bot, vanity wallet generator, and Pump.fun deployment tools.

🔍 **Alpha Scanner** | 🤖 **Telegram Bot** | 💎 **Vanity Generator** | 🚀 **Pump.fun Deployer**

## ✨ Features

### 🌐 Multi-Chain Support
- ☀️ **Solana (SOL)** — Native Solana integration with JSON-RPC
- 🟡 **BSC (Binance Smart Chain)** — Low-fee trading, high volume
- 💎 **Ethereum (ETH)** — Full EVM compatibility
- 🟣 **Polygon (MATIC)** — Fast, cheap transactions
- 🔵 **Arbitrum (ARB)** — Layer 2 scaling
- 🔷 **Base** — Coinbase's L2 network

### 🤖 Telegram Bot Commands
```
/start      — Welcome & chain selection
/chains     — Select active blockchain (buttons)
/scan       — Scan for new meme coin launches
/multiscan  — Scan ALL chains simultaneously
/track      — Track token price movements
/wallet     — Wallet analysis & monitoring
/alpha      — Get AI-picked alpha tokens
/vanity     — Generate custom vanity addresses 🎨
/pumpfun    — Create token deployment config 🚀
/status     — Check RPC connection status
/help       — Show all commands
```

### 🎯 Alpha Scanner
- **Market Cap Filtering**: Focus on $30K-$150K sweet spot
- **Volume Analysis**: Detect unusual trading activity
- **Multi-Source**: Aggregates from Pump.fun, DexScreener, Birdeye
- **Alpha Score**: 0-100 rating for gem detection
- **Auto-Alerts**: Get notified when alpha opportunities arise

### 🎨 Vanity Wallet Generator
Generate Solana wallet addresses with custom patterns:

```bash
/vanity DOGE      → Address starting with "DOGE"
/vanity 0000      → Address with "0000" prefix
/vanity 1337      → Custom pattern anywhere
```

**Difficulty tiers:**
- 3 chars = ~1 minute
- 4 chars = ~1 hour  
- 5+ chars = Days (EXTREME)

### 🚀 Pump.fun Token Deployer
Create token launch configurations with optional vanity mint addresses:

```bash
/pumpfun DogCoin DOGE           — Standard deployment
/pumpfun MoonShot MOON LAMBO    — With vanity mint
```

**Features:**
- Cost estimation (~0.02 SOL)
- Vanity mint address option
- Auto-generated deployment scripts
- Template for Pump.fun integration

### 🎮 Extreme Flappy Bird Bonus Game
Play with placeholder graphics **or your own photos**:

```bash
cd flappy-extreme/
python3 flappy_extreme.py

# With custom photos:
python3 flappy_extreme.py --custom
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

**Dependencies:**
- `python-telegram-bot` — Telegram bot framework
- `requests` — HTTP requests
- `web3` — Ethereum/BSC/Polygon interaction
- `solders` — Solana keypair generation
- `pygame` — For Flappy Bird game

### Configuration

**Set environment variables (optional - has defaults):**

```bash
# Optional: Custom RPCs (public RPCs included)
export SOLANA_RPC_URL="https://your-helius-endpoint.com"
export BSC_RPC_URL="https://your-bsc-rpc.com"

# Required for Telegram Bot
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

**Get free RPC endpoints:**
- [Helius](https://helius.dev) — Best for Solana
- [QuickNode](https://quicknode.com) — Multi-chain
- [Ankr](https://ankr.com/rpc) — Free tier available

## 📱 Usage

### 1. CLI Mode (Interactive Terminal)

```bash
./alpha_terminal.py

# Specific chain:
./alpha_terminal.py --chain bsc
./alpha_terminal.py --chain ethereum

# Scan all chains:
./alpha_terminal.py --scan-all
```

**Menu Options:**
1. Scan New Launches
2. Track Token
3. View Tracked Tokens
4. Multi-Chain Scanner
5. Switch Chain
6. Token Info (EVM)
7. **Vanity Wallet Generator** 🎨
8. **Pump.fun Deployer** 🚀

### 2. Telegram Bot Mode

```bash
python3 telegram_bot.py
```

**Interactive Features:**
- Chain selection with inline buttons
- Real-time alpha scoring
- Vanity wallet generation
- Token deployment configs

### 3. Python Script

```python
from alpha_terminal import MultiChainAlphaTerminal, Chain

# Initialize
terminal = MultiChainAlphaTerminal()

# Switch chains
terminal.switch_chain(Chain.SOLANA)

# Scan for launches
launches = terminal.scan_new_launches()

# Calculate alpha scores
for token in launches:
    score = terminal.calculate_alpha_score(token)
    if score > 70:
        print(f"🔥 HIGH ALPHA: {token['symbol']} (Score: {score})")
```

## 🎯 Alpha Scoring Algorithm

The proprietary alpha score (0-100) considers:

| Factor | Weight | Description |
|--------|--------|-------------|
| Market Cap | 30% | $30K-$150K optimal range |
| Volume Ratio | 25% | Volume/MCAP > 0.5 = strong |
| Source | 20% | pump.fun / dexscreener |
| Chain | 10% | SOL/BSC (+10), ETH/ARB (+5) |
| Freshness | 15% | Newer = higher score |

**Alpha Tiers:**
- 🔥 **80-100** — Extreme alpha (rare gems)
- ⭐ **70-79** — High potential
- 📊 **50-69** — Medium potential
- ⚠️ **<50** — Low potential / risky

## 🎮 Flappy Bird Game

**Play with placeholder art or your photos:**

```bash
cd flappy-extreme/

# Built-in graphics:
python3 flappy_extreme.py

# Your photos:
python3 flappy_extreme.py --custom

# Specific images:
python3 flappy_extreme.py --bird my_face.png --pipe tree.png --bg sunset.jpg
```

**Controls:**
- SPACE / UP / CLICK — Jump
- P — Pause
- R — Restart
- ESC — Quit

**Difficulties:**
- EASY — Slow pipes, large gaps
- NORMAL — Standard difficulty
- EXTREME — Fast pipes, power-ups, small gaps

## 🛠️ Development

### Project Structure

```
ZERO/
├── alpha_terminal.py         # Main trading terminal (500+ lines)
├── telegram_bot.py            # Telegram bot (600+ lines)
├── vanity_generator.py        # Vanity wallet + Pump.fun (450+ lines)
├── config.py                 # Chain configurations & RPCs
├── requirements.txt          # Dependencies
├── flappy-extreme/          # Bonus game
│   ├── flappy_extreme.py    # Full game implementation
│   ├── images/              # Custom photo folder
│   └── README.md            # Game documentation
└── README.md                # This file
```

### Public RPC Endpoints (Pre-configured)

**Works out of the box** — no API keys needed!

| Chain | Endpoints |
|-------|-----------|
| Solana | `api.mainnet-beta.solana.com`, `rpc.ankr.com/solana` |
| BSC | `bsc-dataseed.binance.org`, `rpc.ankr.com/bsc` |
| Ethereum | `eth.llamarpc.com`, `rpc.ankr.com/eth` |
| Polygon | `polygon-rpc.com`, `rpc.ankr.com/polygon` |
| Arbitrum | `arb1.arbitrum.io/rpc`, `rpc.ankr.com/arbitrum` |
| Base | `mainnet.base.org`, `rpc.ankr.com/base` |

## 🔐 Security

- ✅ **No hardcoded keys** — Uses environment variables
- ✅ **.gitignore** — Excludes logs, secrets, temp files
- ✅ **Token safety** — Never commit Telegram tokens
- ✅ **Wallet safety** — Vanity generator saves locally only

**Best practices:**
```bash
# Create .env file (not committed)
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# Load automatically
source .env && python3 telegram_bot.py
```

## 🤝 Contributing

Contributions welcome! Priority areas:

1. **Real API integrations** — DexScreener, Birdeye, Helius
2. **WebSocket feeds** — Real-time price data
3. **Machine learning** — ML-based alpha prediction
4. **Additional chains** — Avalanche, Fantom, Optimism

## 📜 License

MIT License — Free for personal and commercial use.

## 🔗 Links

- **GitHub**: https://github.com/stephenclawdbot-png/zero
- **Issues**: https://github.com/stephenclawdbot-png/zero/issues
- **Telegram**: Use `/help` in bot for support

## ⚠️ Disclaimer

**NOT FINANCIAL ADVICE.** This tool is for educational purposes only.

- Meme coins are highly volatile
- Never risk more than you can afford to lose
- Always verify contract addresses
- Check for honeypots before buying
- DYOR (Do Your Own Research)

---

**Built with ❤️ for the degen community**

⭐ Star this repo if you find it useful!

**Tags**: #solana #crypto #trading-bot #meme-coins #pumpfun #bsc #ethereum #telegram-bot #alpha-scanner #vanity-wallet #open-source
