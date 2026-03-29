#!/usr/bin/env python3
"""Script to add vanity commands to telegram_bot.py"""

# Read the file
with open('/Users/clawdbot/.openclaw/workspace/ZERO/telegram_bot.py', 'r') as f:
    content = f.read()

# The new commands to add
vanity_commands = '''
    async def vanity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /vanity command - Generate vanity wallet"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "🎨 *Vanity Wallet Generator*\\n\\n"
                "Generate Solana wallet with custom address pattern.\\n\\n"
                "Usage: `/vanity <pattern>`\\n"
                "Example: `/vanity DOGE`\\n"
                "Example: `/vanity 0000`\\n\\n"
                "⚡ Longer patterns = exponentially harder to find",
                parse_mode='Markdown'
            )
            return
        
        pattern = args[0]
        
        try:
            from vanity_generator import VanityAddressGenerator
            
            await update.message.reply_text(
                f"🎨 Generating vanity address with pattern: `{pattern}`\\n"
                f"⏳ This may take a while...",
                parse_mode='Markdown'
            )
            
            generator = VanityAddressGenerator()
            
            result = generator.generate_vanity_wallet(
                pattern=pattern,
                is_prefix=True,
                max_attempts=1000000
            )
            
            if result:
                message = f"""
✅ *VANITY ADDRESS FOUND!*

🎯 Pattern: `{pattern}`
📍 Address: `{result.address}`
🔑 Private Key: `{result.private_key[:25]}...`

📊 Stats:
• Attempts: {result.attempts:,}
• Time: {result.time_taken:.2f}s

⚠️ *SAVE THIS IMMEDIATELY!*
The private key is shown only once.

💡 Import to Phantom/Solflare:
• Save private key to file
• Import via "Import Private Key"

🔒 *Keep private key secret!*
                """
                
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    f"❌ Pattern `{pattern}` not found in time limit.\\n"
                    f"💡 Try a shorter pattern (3-4 characters)",
                    parse_mode='Markdown'
                )
                
        except ImportError:
            await update.message.reply_text(
                "❌ Vanity generator requires 'solders' library\\n"
                "💡 Install: pip install solders"
            )

    async def pumpfun(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pumpfun command - Create token deployment config"""
        args = context.args
        
        if len(args) < 2:
            await update.message.reply_text(
                "🚀 *Pump.fun Deployer*\\n\\n"
                "Create token deployment configuration.\\n\\n"
                "Usage: `/pumpfun <name> <symbol> [vanity_pattern]`\\n"
                "Example: `/pumpfun DogCoin DOGE`\\n"
                "Example: `/pumpfun MoonShot MOON LAMBO`\\n\\n"
                "Optional: Add vanity pattern for custom mint address",
                parse_mode='Markdown'
            )
            return
        
        name = args[0]
        symbol = args[1].upper()
        vanity_pattern = args[2] if len(args) > 2 else None
        
        try:
            from vanity_generator import PumpFunDeployer
            
            await update.message.reply_text(
                f"🚀 Creating Pump.fun deployment config...\\n"
                f"   Name: {name}\\n"
                f"   Symbol: {symbol}"
            )
            
            deployer = PumpFunDeployer()
            
            if vanity_pattern:
                await update.message.reply_text(
                    f"🎨 Generating vanity mint: `{vanity_pattern}`...",
                    parse_mode='Markdown'
                )
            
            config = deployer.create_token_config(
                name=name,
                symbol=symbol,
                description=f"{name} is the next moonshot token",
                image_url="https://example.com/token.png",
                vanity_pattern=vanity_pattern
            )
            
            costs = deployer.estimate_deployment_cost()
            
            message = f"""
🚀 *Pump.fun Deployment Config*

📝 Token Info:
• Name: {config['name']}
• Symbol: {config['symbol']}
• Created: {config['created_at']}
            """
            
            if 'vanity_mint' in config:
                message += f"""
🏆 *Vanity Mint Address:*
• Address: `{config['vanity_mint']['address']}`
• Pattern: {config['vanity_mint']['pattern']}
• Attempts: {config['vanity_mint']['attempts']:,}
                """
            
            message += f"""
💰 *Estimated Costs:*
• Pump.fun Fee: {costs['pump_fun_fee']} SOL
• Rent Exempt: {costs['rent_exempt']} SOL
• Total: ~{costs['total_sol']} SOL

⚠️ *IMPORTANT:*
This creates a TEMPLATE script.
For actual deployment:
1. Visit pump.fun and connect wallet
2. Or use Solana CLI
3. Pay deployment fee (~0.02 SOL)

📄 Deployment script generated!
Check your server files.
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
            # Generate script
            deployer.generate_deploy_script(config)
            
        except ImportError:
            await update.message.reply_text(
                "❌ Deployer requires 'solders' library\\n"
                "💡 Install: pip install solders"
            )

'''

# Find the help function and insert before it
help_pos = content.find('    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):')

if help_pos != -1:
    # Insert vanity commands before help
    new_content = content[:help_pos] + vanity_commands + content[help_pos:]
    
    # Write back
    with open('/Users/clawdbot/.openclaw/workspace/ZERO/telegram_bot.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added vanity and pumpfun commands")
else:
    print("❌ Could not find help function")

# Now update the help text
help_text_old = '''*Commands:*
/start - Welcome & chain status
/chains - Select active chain
/scan - Scan current chain
/multiscan - Scan ALL chains
/track <addr> <sym> [name] - Track token
/wallet <addr> - Wallet analysis
/alpha - Get alpha picks
/status - Check RPC status
/help - This message'''

help_text_new = '''*Commands:*
/start - Welcome & chain status
/chains - Select active chain
/scan - Scan current chain
/multiscan - Scan ALL chains
/track <addr> <sym> [name] - Track token
/wallet <addr> - Wallet analysis
/alpha - Get alpha picks
/vanity <pattern> - Generate vanity wallet 🎨
/pumpfun <name> <sym> [pattern] - Create token 🚀
/status - Check RPC status
/help - This message

*Wallet Tools:*
/vanity DOGE - Find address starting with DOGE
/pumpfun MyToken MYT - Create deployment config'''

content = open('/Users/clawdbot/.openclaw/workspace/ZERO/telegram_bot.py', 'r').read()
content = content.replace(help_text_old, help_text_new)

with open('/Users/clawdbot/.openclaw/workspace/ZERO/telegram_bot.py', 'w') as f:
    f.write(content)

print("✅ Updated help text")
