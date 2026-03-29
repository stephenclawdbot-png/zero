#!/usr/bin/env python3
"""Update handlers in telegram_bot.py"""

with open('/Users/clawdbot/.openclaw/workspace/ZERO/telegram_bot.py', 'r') as f:
    content = f.read()

# Find and replace the handlers section
old_handlers = """        # Add handlers
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('chains', self.chains))
        application.add_handler(CommandHandler('scan', self.scan))
        application.add_handler(CommandHandler('multiscan', self.multiscan))
        application.add_handler(CommandHandler('track', self.track))
        application.add_handler(CommandHandler('wallet', self.wallet))
        application.add_handler(CommandHandler('alpha', self.alpha))
        application.add_handler(CommandHandler('status', self.status))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CallbackQueryHandler(self.button_handler))"""

new_handlers = """        # Add handlers
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('chains', self.chains))
        application.add_handler(CommandHandler('scan', self.scan))
        application.add_handler(CommandHandler('multiscan', self.multiscan))
        application.add_handler(CommandHandler('track', self.track))
        application.add_handler(CommandHandler('wallet', self.wallet))
        application.add_handler(CommandHandler('alpha', self.alpha))
        application.add_handler(CommandHandler('vanity', self.vanity))
        application.add_handler(CommandHandler('pumpfun', self.pumpfun))
        application.add_handler(CommandHandler('status', self.status))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CallbackQueryHandler(self.button_handler))"""

content = content.replace(old_handlers, new_handlers)

with open('/Users/clawdbot/.openclaw/workspace/ZERO/telegram_bot.py', 'w') as f:
    f.write(content)

print("✅ Added vanity and pumpfun command handlers")
