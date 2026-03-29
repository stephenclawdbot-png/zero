#!/usr/bin/env python3
"""
Solana Alpha Trading Terminal
Multi-interface: CLI, Telegram Bot, Web Dashboard
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TokenConfig:
    """Token configuration"""
    address: str
    symbol: str
    name: str
    min_mcap: float = 30000
    max_mcap: float = 150000
    min_volume: float = 5000

class SolanaAlphaTerminal:
    """Main terminal class with Solana integration"""
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.session = requests.Session()
        self.tracked_tokens: List[TokenConfig] = []
        self.alerts_enabled = True
        
    def check_rpc_connection(self) -> bool:
        """Check if RPC is reachable"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getHealth"
            }
            response = self.session.post(
                self.rpc_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"RPC connection failed: {e}")
            return False
    
    def get_slot(self) -> Optional[int]:
        """Get current Solana slot"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSlot"
            }
            response = self.session.post(self.rpc_url, json=payload, timeout=10)
            data = response.json()
            return data.get('result')
        except Exception as e:
            logger.error(f"Failed to get slot: {e}")
            return None
    
    def scan_new_launches(self) -> List[Dict]:
        """Scan for new token launches (placeholder - integrate with DexScreener/Pump.fun API)"""
        # This is where you'd integrate with actual APIs
        # Placeholder for demo purposes
        sample_launches = [
            {
                'address': 'sample_token_1',
                'symbol': 'DEMO1',
                'name': 'Demo Token 1',
                'mcap': 50000,
                'volume': 15000,
                'timestamp': datetime.now().isoformat(),
                'source': 'pump.fun'
            },
            {
                'address': 'sample_token_2', 
                'symbol': 'DEMO2',
                'name': 'Demo Token 2',
                'mcap': 75000,
                'volume': 22000,
                'timestamp': datetime.now().isoformat(),
                'source': 'dexscreener'
            }
        ]
        return sample_launches
    
    def calculate_alpha_score(self, token_data: Dict) -> float:
        """Calculate alpha potential score (0-100)"""
        score = 0.0
        
        # Market cap in range (30K - 150K optimal)
        mcap = token_data.get('mcap', 0)
        if 30000 <= mcap <= 150000:
            score += 30
        elif 150000 < mcap <= 500000:
            score += 20
        
        # Volume ratio
        volume = token_data.get('volume', 0)
        if mcap > 0:
            vol_ratio = volume / mcap
            if vol_ratio > 0.5:
                score += 25
            elif vol_ratio > 0.3:
                score += 15
        
        # Source credibility
        source = token_data.get('source', '')
        if 'pump.fun' in source:
            score += 20
        elif 'dexscreener' in source:
            score += 15
        
        # Time since launch (newer = higher score)
        score += 10  # Base freshness
        
        return min(score, 100)
    
    def display_welcome(self):
        """Display welcome screen"""
        welcome = """
╔═══════════════════════════════════════════════════════════════╗
║          SOLANA ALPHA TRADING TERMINAL v1.0                   ║
║                                                               ║
║  Multi-Interface Trading Suite for Solana Meme Coins         ║
║  CLI • Telegram Bot • Web Dashboard                         ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(welcome)
    
    def run_cli(self):
        """Run interactive CLI mode"""
        self.display_welcome()
        
        print(f"RPC URL: {self.rpc_url}")
        print(f"RPC Status: {'✅ Connected' if self.check_rpc_connection() else '❌ Disconnected'}")
        print()
        
        while True:
            print("\n┌─ Commands ─────────────────────────────┐")
            print("│ 1. Scan New Launches                   │")
            print("│ 2. Track Token                         │")
            print("│ 3. View Tracked Tokens                 │")
            print("│ 4. Alpha Scanner Settings              │")
            print("│ 5. Check RPC Status                    │")
            print("│ 6. Exit                                │")
            print("└────────────────────────────────────────┘")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.cmd_scan_launches()
            elif choice == '2':
                self.cmd_track_token()
            elif choice == '3':
                self.cmd_view_tracked()
            elif choice == '4':
                self.cmd_scanner_settings()
            elif choice == '5':
                self.cmd_check_rpc()
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option")
    
    def cmd_scan_launches(self):
        """Scan for new launches"""
        print("\n🔍 Scanning for new token launches...")
        launches = self.scan_new_launches()
        
        if not launches:
            print("No new launches found.")
            return
        
        print(f"\n🚀 Found {len(launches)} new launches:\n")
        print("-" * 80)
        
        for token in launches:
            alpha_score = self.calculate_alpha_score(token)
            
            print(f"\n🪙 {token['name']} (${token['symbol']})")
            print(f"   Address: {token['address']}")
            print(f"   Market Cap: ${token['mcap']:,.0f}")
            print(f"   Volume: ${token['volume']:,.0f}")
            print(f"   Source: {token['source']}")
            print(f"   Alpha Score: {alpha_score:.1f}/100 {'🔥' if alpha_score > 70 else ''}")
            
            if alpha_score > 70:
                print("   ⚠️ HIGH ALPHA POTENTIAL!")
        
        print("\n" + "-" * 80)
    
    def cmd_track_token(self):
        """Add token to tracking list"""
        address = input("Enter token address: ").strip()
        symbol = input("Enter symbol: ").strip()
        name = input("Enter name: ").strip()
        
        token = TokenConfig(address=address, symbol=symbol, name=name)
        self.tracked_tokens.append(token)
        
        print(f"✅ Now tracking {name} (${symbol})")
    
    def cmd_view_tracked(self):
        """View tracked tokens"""
        if not self.tracked_tokens:
            print("No tokens being tracked.")
            return
        
        print(f"\n📊 Tracking {len(self.tracked_tokens)} tokens:\n")
        for token in self.tracked_tokens:
            print(f"  • {token.name} (${token.symbol}) - {token.address}")
    
    def cmd_scanner_settings(self):
        """Configure scanner settings"""
        print("\n⚙️ Scanner Settings")
        print(f"  Min Market Cap: $30,000")
        print(f"  Max Market Cap: $150,000")
        print(f"  Min Volume: $5,000")
        print(f"  Alerts: {'ON' if self.alerts_enabled else 'OFF'}")
        
        toggle = input("\nToggle alerts? (y/n): ").strip().lower()
        if toggle == 'y':
            self.alerts_enabled = not self.alerts_enabled
            print(f"Alerts: {'ON' if self.alerts_enabled else 'OFF'}")
    
    def cmd_check_rpc(self):
        """Check RPC connection status"""
        print(f"\n🔗 RPC URL: {self.rpc_url}")
        
        if self.check_rpc_connection():
            slot = self.get_slot()
            print(f"✅ Connected")
            print(f"📦 Current Slot: {slot}")
        else:
            print("❌ Connection failed")
            print("💡 Tip: Set SOLANA_RPC_URL environment variable for custom RPC")


def main():
    parser = argparse.ArgumentParser(description='Solana Alpha Trading Terminal')
    parser.add_argument('--rpc', help='Solana RPC URL (or set SOLANA_RPC_URL env var)')
    parser.add_argument('--telegram', action='store_true', help='Run Telegram bot mode')
    parser.add_argument('--web', action='store_true', help='Run web dashboard mode')
    
    args = parser.parse_args()
    
    terminal = SolanaAlphaTerminal(rpc_url=args.rpc)
    
    if args.telegram:
        print("🤖 Starting Telegram bot mode...")
        print("💡 Use: python3 telegram_bot.py")
    elif args.web:
        print("🌐 Starting web dashboard...")
        print("💡 Use: python3 web_dashboard.py")
    else:
        terminal.run_cli()


if __name__ == '__main__':
    main()
