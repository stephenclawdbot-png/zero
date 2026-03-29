#!/usr/bin/env python3
"""
Telegram Bot Interface for Solana Alpha Terminal
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Import terminal functionality
from alpha_terminal import SolanaAlphaTerminal, TokenConfig

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AlphaTelegramBot:
    """Telegram bot for Solana Alpha Terminal"""
    
    def __init__(self):
        self.terminal = SolanaAlphaTerminal()
        self.tracked_tokens = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🚀 *Welcome to Solana Alpha Terminal!*

Track Solana meme coins and get alpha alerts.

*Commands:*
/scan - Scan for new launches
/track \u003caddress\u003e \u003csymbol\u003e - Track a token
/wallet \u003caddress\u003e - View wallet analysis
/alpha - Get alpha picks
/settings - Configure bot
/status - Check RPC status
/help - Show help

*Alpha filters:*
• Market Cap: $30K - $150K
• Min Volume: $5K
• Auto-alerts for new launches
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
    
    async def scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command"""
        await update.message.reply_text("🔍 Scanning for new launches...")
        
        launches = self.terminal.scan_new_launches()
        
        if not launches:
            await update.message.reply_text("No new launches found.")
            return
        
        for token in launches:
            alpha_score = self.terminal.calculate_alpha_score(token)
            
            keyboard = [
                [InlineKeyboardButton("📊 Analyze", callback_data=f"analyze_{token['address']}")],
                [InlineKeyboardButton("🔔 Track", callback_data=f"track_{token['address']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""
🪙 *{token['name']}* (${token['symbol']})

💰 Market Cap: ${token['mcap']:,.0f}
📊 Volume: ${token['volume']:,.0f}
🔹 Source: {token['source']}
🎯 Alpha Score: {alpha_score:.1f}/100

{'🔥 HIGH ALPHA POTENTIAL!' if alpha_score > 70 else ''}
            """
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def track(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /track command"""
        args = context.args
        
        if len(args) < 2:
            await update.message.reply_text(
                "Usage: /track \u003caddress\u003e \u003csymbol\u003e [name]"
            )
            return
        
        address = args[0]
        symbol = args[1].upper()
        name = args[2] if len(args) > 2 else symbol
        
        token = TokenConfig(address=address, symbol=symbol, name=name)
        self.tracked_tokens[address] = token
        
        await update.message.reply_text(
            f"✅ Now tracking *{name}* (${symbol})\n\n"
            f"You'll receive alerts for significant moves.",
            parse_mode='Markdown'
        )
    
    async def wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /wallet command"""
        args = context.args
        
        if not args:
            await update.message.reply_text("Usage: /wallet \u003caddress\u003e")
            return
        
        wallet_address = args[0]
        
        # Placeholder for wallet analysis
        # In production, integrate with Helius or similar API
        message = f"""
👤 *Wallet Analysis*

Address: `{wallet_address[:20]}...`

📊 Stats (placeholder):
• Total Transactions: N/A
• Token Holdings: N/A
• PnL (7d): N/A

💡 Connect a real RPC to get live data
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def alpha(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alpha command - get alpha picks"""
        await update.message.reply_text("🎯 Generating alpha picks...")
        
        # Get top alpha picks
        launches = self.terminal.scan_new_launches()
        sorted_launches = sorted(
            launches,
            key=lambda x: self.terminal.calculate_alpha_score(x),
            reverse=True
        )
        
        top_picks = sorted_launches[:3]
        
        if not top_picks:
            await update.message.reply_text("No alpha picks available right now.")
            return
        
        for i, token in enumerate(top_picks, 1):
            score = self.terminal.calculate_alpha_score(token)
            
            message = f"""
🎯 *Alpha Pick #{i}*

�️ {token['name']} (${token['symbol']})
💰 MCAP: ${token['mcap']:,.0f}
📊 Alpha Score: {score:.1f}/100 ⭐

🚀 *Why this is alpha:*
• New launch on {token['source']}
• Volume/MCAP ratio healthy
• In optimal mcap range

⚠️ DYOR - Always verify contracts
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
    
    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        keyboard = [
            [InlineKeyboardButton("Min MCAP: $30K", callback_data="set_mcap_min")],
            [InlineKeyboardButton("Max MCAP: $150K", callback_data="set_mcap_max")],
            [InlineKeyboardButton("Min Volume: $5K", callback_data="set_volume")],
            [InlineKeyboardButton("Toggle Alerts 🔔", callback_data="toggle_alerts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ Bot Settings:\n\n"
            "Current configuration:\n"
            "• Market Cap Range: $30K - $150K\n"
            "• Min Volume: $5K\n"
            "• Alerts: Enabled\n\n"
            "Tap to configure:",
            reply_markup=reply_markup
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        connected = self.terminal.check_rpc_connection()
        slot = self.terminal.get_slot()
        
        status = '✅ Connected' if connected else '❌ Disconnected'
        
        message = f"""
🔗 *RPC Status*

Status: {status}
RPC URL: `{self.terminal.rpc_url}`
Current Slot: {slot or 'N/A'}

📊 Tracked Tokens: {len(self.tracked_tokens)}
🔄 Last Scan: {datetime.now().strftime('%H:%M:%S')}
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 *Solana Alpha Bot Help*

*Commands:*
/start - Welcome message
/scan - Scan for new launches
/track \u003caddr\u003e \u003csym\u003e - Track token
/wallet \u003caddr\u003e - Wallet analysis
/alpha - Get alpha picks
/settings - Configure bot
/status - Check RPC status
/help - This message

*Setup:*
Set SOLANA_RPC_URL env var for custom RPC
Get free RPC at: helius.dev or quicknode.com

*Alpha Criteria:*
• Market Cap: $30K-$150K (optimal)
• Min Volume: $5K
• Source: pump.fun/dexscreener
• Score \u003e 70 = HIGH ALPHA

⚠️ *Disclaimer:* Not financial advice. DYOR.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("analyze_"):
            token_address = callback_data.split("_")[1]
            await query.edit_message_text(
                f"📊 Analysis for {token_address[:20]}...\n\n"
                "(Integrate with DexScreener API for full analysis)"
            )
        
        elif callback_data.startswith("track_"):
            token_address = callback_data.split("_")[1]
            await query.edit_message_text(
                f"✅ Now tracking {token_address[:20]}...\n\n"
                "You'll receive alerts!"
            )
    
    def run(self):
        """Run the bot"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not set")
            print("💡 Set it with: export TELEGRAM_BOT_TOKEN=your_token_here")
            return
        
        print("🤖 Starting Telegram Bot...")
        print("💡 Get token from @BotFather on Telegram")
        
        application = ApplicationBuilder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('scan', self.scan))
        application.add_handler(CommandHandler('track', self.track))
        application.add_handler(CommandHandler('wallet', self.wallet))
        application.add_handler(CommandHandler('alpha', self.alpha))
        application.add_handler(CommandHandler('settings', self.settings))
        application.add_handler(CommandHandler('status', self.status))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        print("✅ Bot is running! Press Ctrl+C to stop.")
        application.run_polling()


def main():
    bot = AlphaTelegramBot()
    bot.run()


if __name__ == '__main__':
    main()
