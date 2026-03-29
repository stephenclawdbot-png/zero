#!/usr/bin/env python3
"""
Multi-Chain Telegram Bot for Alpha Terminal
Supports: Solana, BSC, Ethereum, Polygon, Arbitrum, Base
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Import multi-chain terminal
from alpha_terminal import MultiChainAlphaTerminal, TokenConfig, Chain, PUBLIC_RPCS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Chain emojis
CHAIN_EMOJIS = {
    Chain.SOLANA: "☀️",
    Chain.BSC: "🟡",
    Chain.ETHEREUM: "💎",
    Chain.POLYGON: "🟣",
    Chain.ARBITRUM: "🔵",
    Chain.BASE: "🔷",
}

class MultiChainAlphaBot:
    """Telegram bot for multi-chain alpha terminal"""
    
    def __init__(self):
        self.terminal = MultiChainAlphaTerminal()
        self.user_chains: Dict[int, Chain] = {}  # User's preferred chain
        
    def get_chain_emoji(self, chain: Chain) -> str:
        """Get emoji for chain"""
        return CHAIN_EMOJIS.get(chain, "🔗")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        # Set default chain
        if user_id not in self.user_chains:
            self.user_chains[user_id] = Chain.SOLANA
        
        # Build chain status
        chain_status = ""
        for chain, config in self.terminal.chains.items():
            status = "🟢" if config.connected else "🔴"
            chain_status += f"{status} {self.get_chain_emoji(chain)} {chain.value.upper()}\n"
        
        welcome_message = f"""
🚀 *Multi-Chain Alpha Terminal*

*Supported Networks:*
{chain_status}

*Commands:*
/scan - Scan for launches
/track - Track a token
/chains - Select chain
/multiscan - Scan ALL chains
/wallet - Wallet analysis
/alpha - Get alpha picks
/status - Check RPC status
/help - Show help

*Current Chain:* {self.get_chain_emoji(self.user_chains.get(user_id, Chain.SOLANA))} {self.user_chains.get(user_id, Chain.SOLANA).value.upper()}

💡 Use /chains to switch networks
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def chains(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chains command"""
        keyboard = []
        
        for chain in self.terminal.chains.keys():
            emoji = self.get_chain_emoji(chain)
            keyboard.append([
                InlineKeyboardButton(
                    f"{emoji} {chain.value.upper()}", 
                    callback_data=f"chain_{chain.value}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🌐 *Select Chain:*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def scan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command"""
        user_id = update.effective_user.id
        user_chain = self.user_chains.get(user_id, Chain.SOLANA)
        
        await update.message.reply_text(
            f"🔍 Scanning {self.get_chain_emoji(user_chain)} {user_chain.value.upper()} for launches..."
        )
        
        launches = self.terminal.scan_new_launches(user_chain)
        
        if not launches:
            await update.message.reply_text("No new launches found.")
            return
        
        for token in launches:
            alpha_score = self.terminal.calculate_alpha_score(token)
            
            keyboard = [
                [InlineKeyboardButton("📊 Analyze", callback_data=f"analyze_{token['address']}")],
                [InlineKeyboardButton("🔔 Track", callback_data=f"track_{token['address']}_{token['symbol']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            emoji = self.get_chain_emoji(user_chain)
            
            message = f"""
{emoji} *{token['name']}* (${token['symbol']})

💰 Market Cap: ${token['mcap']:,.0f}
📊 Volume: ${token['volume']:,.0f}
🔗 Chain: {token['chain'].upper()}
🎯 Alpha Score: {alpha_score:.1f}/100

{'🔥 HIGH ALPHA POTENTIAL!' if alpha_score > 70 else ''}
            """
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def multiscan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /multiscan command"""
        await update.message.reply_text("🌐 Scanning ALL chains...")
        
        all_launches = []
        for chain in self.terminal.chains.keys():
            launches = self.terminal.scan_new_launches(chain)
            for launch in launches:
                launch['alpha_score'] = self.terminal.calculate_alpha_score(launch)
            all_launches.extend(launches)
        
        all_launches.sort(key=lambda x: x['alpha_score'], reverse=True)
        
        if not all_launches:
            await update.message.reply_text("No launches found on any chain.")
            return
        
        await update.message.reply_text(f"🎯 *Top Alpha Picks Across All Chains:*\n", parse_mode='Markdown')
        
        for i, token in enumerate(all_launches[:3], 1):
            emoji = self.get_chain_emoji(Chain(token['chain']))
            
            message = f"""
{i}. {emoji} *{token['name']}* (${token['symbol']})

💰 MCAP: ${token['mcap']:,.0f}
📊 Volume: ${token['volume']:,.0f}
🔗 Chain: {token['chain'].upper()}
⭐ Alpha Score: {token['alpha_score']:.1f}/100

🔗 [View on Explorer]({token.get('explorer', '#')})
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
    
    async def track(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /track command"""
        user_id = update.effective_user.id
        user_chain = self.user_chains.get(user_id, Chain.SOLANA)
        args = context.args
        
        if len(args) < 2:
            current_chain = user_chain.value.upper()
            await update.message.reply_text(
                f"Usage: /track <address> <symbol> [name]\n\n"
                f"Example: /track 0xabc... PEPE 'Pepe Token'\n\n"
                f"Current chain: {current_chain}"
            )
            return
        
        address = args[0]
        symbol = args[1].upper()
        name = args[2] if len(args) > 2 else symbol
        
        token = TokenConfig(
            address=address, 
            symbol=symbol, 
            name=name, 
            chain=user_chain
        )
        self.terminal.tracked_tokens.append(token)
        
        emoji = self.get_chain_emoji(user_chain)
        
        await update.message.reply_text(
            f"✅ Now tracking *{name}* (${symbol})\n"
            f"{emoji} Chain: {user_chain.value.upper()}\n\n"
            f"You'll receive alerts for significant moves.",
            parse_mode='Markdown'
        )
    
    async def wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /wallet command"""
        args = context.args
        user_id = update.effective_user.id
        user_chain = self.user_chains.get(user_id, Chain.SOLANA)
        
        if not args:
            await update.message.reply_text("Usage: /wallet <address>")
            return
        
        wallet_address = args[0]
        emoji = self.get_chain_emoji(user_chain)
        
        # Placeholder for wallet analysis
        message = f"""
{emoji} *Wallet Analysis*

Address: `{wallet_address[:25]}...`
Chain: {user_chain.value.upper()}

📊 Stats (placeholder):
• Total Transactions: N/A
• Token Holdings: N/A
• PnL (7d): N/A

💡 Connect a real RPC to get live data
🔗 [View on Explorer]({self.terminal.explorers.get(user_chain, '#')}{wallet_address})
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def alpha(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alpha command"""
        user_id = update.effective_user.id
        user_chain = self.user_chains.get(user_id, Chain.SOLANA)
        
        await update.message.reply_text("🎯 Generating alpha picks...")
        
        # Get top alpha picks from current chain
        launches = self.terminal.scan_new_launches(user_chain)
        sorted_launches = sorted(
            launches,
            key=lambda x: self.terminal.calculate_alpha_score(x),
            reverse=True
        )
        
        top_picks = sorted_launches[:3]
        
        if not top_picks:
            await update.message.reply_text("No alpha picks available right now.")
            return
        
        emoji = self.get_chain_emoji(user_chain)
        
        for i, token in enumerate(top_picks, 1):
            score = self.terminal.calculate_alpha_score(token)
            
            message = f"""
{emoji} *Alpha Pick #{i}*

🪙 {token['name']} (${token['symbol']})
💰 MCAP: ${token['mcap']:,.0f}
🔗 Chain: {token['chain'].upper()}
⭐ Alpha Score: {score:.1f}/100 🚀

*Why this is alpha:*
• New launch on {token['source']}
• Optimal market cap range
• Healthy volume/Mcap ratio

⚠️ DYOR - Always verify contracts
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_lines = ["🔗 *Multi-Chain RPC Status*\n"]
        
        for chain, config in self.terminal.chains.items():
            emoji = self.get_chain_emoji(chain)
            status = "🟢 Online" if config.connected else "🔴 Offline"
            slot = ""
            
            if chain == Chain.SOLANA and config.connected:
                slot_num = self.terminal.get_solana_slot()
                if slot_num:
                    slot = f"| Slot: {slot_num}"
            elif config.connected and config.web3:
                try:
                    block_num = self.terminal.get_evm_block_number(chain)
                    if block_num:
                        slot = f"| Block: {block_num}"
                except:
                    pass
            
            status_lines.append(
                f"{emoji} *{chain.value.upper()}*: {status} {slot}"
            )
        
        status_lines.append(f"\n📊 Tracked Tokens: {len(self.terminal.tracked_tokens)}")
        
        await update.message.reply_text(
            "\n".join(status_lines),
            parse_mode='Markdown'
        )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 *Multi-Chain Alpha Bot Help*

*Commands:*
/start - Welcome & chain status
/chains - Select active chain
/scan - Scan current chain
/multiscan - Scan ALL chains
/track <addr> <sym> - Track token
/wallet <addr> - Wallet analysis
/alpha - Get alpha picks
/status - Check RPC status
/help - This message

*Supported Chains:*
☀️ Solana (SOL)
🟡 BSC (Binance Smart Chain)
💎 Ethereum (ETH)
🟣 Polygon (MATIC)
🔵 Arbitrum (ARB)
🔷 Base

*Setup:*
Set SOLANA_RPC_URL, BSC_RPC_URL, etc. for custom RPCs
Get free RPCs at: helius.dev, quicknode.com, ankr.com

*Alpha Criteria:*
• Market Cap: $30K-$150K
• Min Volume: $5K
• Score > 70 = HIGH ALPHA

⚠️ *Disclaimer:* Not financial advice. DYOR.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        user_id = update.effective_user.id
        
        if callback_data.startswith("chain_"):
            chain_name = callback_data.split("_")[1]
            chain = Chain(chain_name)
            self.user_chains[user_id] = chain
            
            emoji = self.get_chain_emoji(chain)
            await query.edit_message_text(
                f"✅ Switched to {emoji} *{chain.value.upper()}*\n\n"
                f"Use /scan to find launches on this chain.",
                parse_mode='Markdown'
            )
        
        elif callback_data.startswith("analyze_"):
            token_address = callback_data.split("_")[1]
            await query.edit_message_text(
                f"📊 Analysis for `{token_address[:20]}...`\n\n"
                f"(Integrate with real API for full analysis)"
            )
        
        elif callback_data.startswith("track_"):
            parts = callback_data.split("_")
            if len(parts) >= 3:
                token_address = parts[1]
                symbol = parts[2]
                await query.edit_message_text(
                    f"✅ Now tracking {symbol}\n"
                    f"Address: `{token_address[:20]}...`\n\n"
                    f"You'll receive alerts!"
                )
    
    def run(self):
        """Run the bot"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not token:
            print("❌ Error: TELEGRAM_BOT_TOKEN not set")
            print("💡 Set it with: export TELEGRAM_BOT_TOKEN=your_token_here")
            print("🤖 Get token from @BotFather on Telegram")
            return
        
        print("🤖 Starting Multi-Chain Telegram Bot...")
        print("🌐 Supported: Solana, BSC, Ethereum, Polygon, Arbitrum, Base")
        
        application = ApplicationBuilder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('chains', self.chains))
        application.add_handler(CommandHandler('scan', self.scan))
        application.add_handler(CommandHandler('multiscan', self.multiscan))
        application.add_handler(CommandHandler('track', self.track))
        application.add_handler(CommandHandler('wallet', self.wallet))
        application.add_handler(CommandHandler('alpha', self.alpha))
        application.add_handler(CommandHandler('status', self.status))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        print("✅ Bot is running! Press Ctrl+C to stop.")
        application.run_polling()


def main():
    bot = MultiChainAlphaBot()
    bot.run()


if __name__ == '__main__':
    main()
