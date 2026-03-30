# Zero + Hermes 🧠🤖

Clean AI assistant powered by Ollama local LLM.

## 🚀 What is this?

A Telegram bot that responds intelligently using **Ollama** (local LLM).

No external APIs needed - runs entirely on your machine.

## 🛠️ Requirements

- Python 3.8+
- Ollama (local LLM server)
- Telegram Bot Token

## 📦 Installation

```bash
# Install Ollama
https://ollama.com

# Install Python dependencies
pip install python-telegram-bot requests

# Pull a model
ollama pull llama3.2
```

## 🚀 Quick Start

```bash
# 1. Start Ollama
ollama serve

# 2. Set your Telegram bot token
export TELEGRAM_BOT_TOKEN="your_token_here"

# 3. Run the bot
python3 telegram_bot.py
```

## 💬 Commands

```
/start  - Welcome message
/ask    - Ask a specific question
/chat   - Start a conversation
/status - Check Ollama status
/help   - Show all commands
```

Just send a message for AI response!

## 🧠 How it Works

1. User sends message
2. Bot forwards to Ollama (local LLM)
3. Ollama generates response
4. Bot sends back to user

All processing happens locally - no cloud APIs!

## ⚙️ Configuration

Edit `telegram_bot.py` to customize:

```python
self.system_prompt = "Your custom system prompt here"
self.ollama = OllamaClient(model="llama3.2")  # Change model
```

## 📝 Notes

- Powered by [Ollama](https://ollama.com)
- Uses models like llama3.2, mistral, codellama
- Fully offline capable
- Privacy-focused (no data leaves your machine)

## 📄 License

MIT License
