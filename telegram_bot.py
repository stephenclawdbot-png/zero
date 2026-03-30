#!/usr/bin/env python3
"""
Zero + Hermes - Clean AI Assistant
Powered by Ollama LLM
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama LLM client"""
    
    def __init__(self, host="http://localhost:11434", model="llama3.2"):
        self.host = host
        self.model = model
        self.api_generate = f"{host}/api/generate"
        
    def generate(self, prompt: str, system: str = None) -> str:
        """Generate response from Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system:
                payload["system"] = system
                
            response = requests.post(self.api_generate, json=payload, timeout=60)
            data = response.json()
            return data.get("response", "No response")
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def is_running(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


class HermesBot:
    """Hermes AI Assistant Bot"""
    
    def __init__(self):
        self.ollama = OllamaClient(model="llama3.2")
        self.ollama_available = self.ollama.is_running()
        
        self.system_prompt = """You are Hermes, a helpful AI assistant running through Zero.
You are powered by Ollama (local LLM).

Capabilities:
- Answer questions
- Help with coding
- Explain concepts
- Have conversations
- Assist with research

Be helpful, concise, and knowledgeable."""
        
        if self.ollama_available:
            logger.info("✅ Ollama connected")
        else:
            logger.warning("⚠️ Ollama not running")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start"""
        welcome = """
🤖 *Welcome to Zero + Hermes*

I'm powered by Ollama (local LLM).

*Commands:*
/ask \- Ask me anything
/chat \- Have a conversation
/help \- Show all commands
/status \- Check Ollama status

Just send a message and I'll respond!
        """
        await update.message.reply_text(welcome, parse_mode="Markdown")
    
    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "💬 Usage: /ask <your question>\n\n"
                "Example: /ask Explain quantum computing"
            )
            return
        
        await self._process_ai_request(update, " ".join(args))
    
    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "💬 Usage: /chat <your message>\n\n"
                "Or just send me a message directly!"
            )
            return
        
        await self._process_ai_request(update, " ".join(args))
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle direct messages"""
        user_message = update.message.text
        await self._process_ai_request(update, user_message)
    
    async def _process_ai_request(self, update: Update, prompt: str):
        """Process AI request through Ollama"""
        
        if not self.ollama_available:
            await update.message.reply_text(
                "❌ Ollama is not running.\n\n"
                "Start it with: `ollama serve`"
            )
            return
        
        # Show typing
        await update.message.chat.send_action(action="typing")
        
        try:
            # Generate response
            response = self.ollama.generate(prompt, self.system_prompt)
            
            await update.message.reply_text(
                f"🤖 {response}\n\n"
                f"_Powered by Ollama llama3.2_",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)[:100]}"
            )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check Ollama status"""
        if self.ollama.is_running():
            await update.message.reply_text(
                "✅ *Ollama Status: Online*\n\n"
                f"Model: {self.ollama.model}\n"
                f"Host: {self.ollama.host}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ *Ollama Status: Offline*\n\n"
                "Start with: `ollama serve`"
            )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help"""
        help_text = """
🤖 *Hermes AI Bot Commands*

/ask \- Ask a specific question
/chat \- Start a conversation
/status \- Check Ollama status
/help \- Show this help

*How to use:*
Just send me any message and I'll respond using my AI brain!

*Examples:*
/ask What is machine learning?
/chat Tell me a story
Explain Python dictionaries

Powered by Ollama (local LLM)
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    def run(self):
        """Start the bot"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not set")
            return
        
        application = ApplicationBuilder().token(token).build()
        
        # Command handlers
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('ask', self.ask))
        application.add_handler(CommandHandler('chat', self.chat))
        application.add_handler(CommandHandler('status', self.status))
        application.add_handler(CommandHandler('help', self.help))
        
        # Direct message handler
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        print("=" * 50)
        print("🤖 Zero + Hermes Bot")
        print("=" * 50)
        if self.ollama_available:
            print("✅ Ollama: Connected")
            print(f"🧠 Model: {self.ollama.model}")
        else:
            print("⚠️ Ollama: Not running")
        print("=" * 50)
        print("\nPress Ctrl+C to stop")
        
        application.run_polling()


def main():
    bot = HermesBot()
    bot.run()


if __name__ == '__main__':
    main()
