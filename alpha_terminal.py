#!/usr/bin/env python3
"""
Multi-Chain Alpha Trading Terminal
Supports: Solana, BSC (Binance Smart Chain), EVM (Ethereum/Polygon/Arbitrum)
Multi-interface: CLI, Telegram Bot, Web Dashboard
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import requests
from web3 import Web3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Chain(Enum):
    """Supported blockchain networks"""
    SOLANA = "solana"
    BSC = "bsc"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    BASE = "base"

# Public RPC Endpoints (free, rate-limited)
PUBLIC_RPCS = {
    Chain.SOLANA: [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com",
        "https://rpc.ankr.com/solana",
    ],
    Chain.BSC: [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io",
        "https://bsc-dataseed1.ninicoin.io",
        "https://rpc.ankr.com/bsc",
    ],
    Chain.ETHEREUM: [
        "https://eth.llamarpc.com",
        "https://rpc.ankr.com/eth",
        "https://ethereum.publicnode.com",
    ],
    Chain.POLYGON: [
        "https://polygon.llamarpc.com",
        "https://rpc.ankr.com/polygon",
        "https://polygon-rpc.com",
    ],
    Chain.ARBITRUM: [
        "https://arbitrum.llamarpc.com",
        "https://rpc.ankr.com/arbitrum",
        "https://arb1.arbitrum.io/rpc",
    ],
    Chain.BASE: [
        "https://base.llamarpc.com",
        "https://rpc.ankr.com/base",
        "https://mainnet.base.org",
    ],
}

# Chain explorers
EXPLORERS = {
    Chain.SOLANA: "https://solscan.io/token/",
    Chain.BSC: "https://bscscan.com/token/",
    Chain.ETHEREUM: "https://etherscan.io/token/",
    Chain.POLYGON: "https://polygonscan.com/token/",
    Chain.ARBITRUM: "https://arbiscan.io/token/",
    Chain.BASE: "https://basescan.org/token/",
}

@dataclass
class TokenConfig:
    """Token configuration"""
    address: str
    symbol: str
    name: str
    chain: Chain
    min_mcap: float = 30000
    max_mcap: float = 150000
    min_volume: float = 5000

@dataclass  
class ChainConfig:
    """Chain configuration"""
    chain: Chain
    rpc_url: str
    web3: Optional[Web3] = field(default=None, repr=False)
    connected: bool = False
    block_time: float = 3.0  # seconds
    
    def __post_init__(self):
        if self.chain in [Chain.BSC, Chain.ETHEREUM, Chain.POLYGON, Chain.ARBITRUM, Chain.BASE]:
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

class MultiChainAlphaTerminal:
    """Multi-chain alpha trading terminal"""
    
    def __init__(self):
        self.chains: Dict[Chain, ChainConfig] = {}
        self.tracked_tokens: List[TokenConfig] = []
        self.alerts_enabled = True
        self.session = requests.Session()
        self.active_chain: Chain = Chain.SOLANA
        
        # Initialize all chains with public RPCs
        self._init_chains()
        
    def _init_chains(self):
        """Initialize all supported chains with public RPCs"""
        for chain, rpc_urls in PUBLIC_RPCS.items():
            # Try each RPC until one works
            for rpc in rpc_urls:
                try:
                    config = ChainConfig(chain=chain, rpc_url=rpc)
                    
                    # Test connection
                    if self._test_chain_connection(config):
                        self.chains[chain] = config
                        logger.info(f"✅ {chain.value.upper()}: Connected to {rpc}")
                        break
                except Exception as e:
                    logger.warning(f"⚠️ {chain.value}: Failed {rpc} - {e}")
                    continue
            else:
                logger.error(f"❌ {chain.value}: No working RPC found")
    
    def _test_chain_connection(self, config: ChainConfig) -> bool:
        """Test if chain RPC is working"""
        try:
            if config.chain == Chain.SOLANA:
                # Solana JSON-RPC test
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getHealth"
                }
                response = self.session.post(config.rpc_url, json=payload, timeout=5)
                return response.status_code == 200
            else:
                # EVM chains via Web3
                return config.web3.is_connected()
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False
    
    def get_chain_status(self) -> Dict[Chain, bool]:
        """Get connection status for all chains"""
        return {chain: config.connected for chain, config in self.chains.items()}
    
    def switch_chain(self, chain: Chain) -> bool:
        """Switch active chain"""
        if chain in self.chains:
            self.active_chain = chain
            logger.info(f"📡 Switched to {chain.value.upper()}")
            return True
        else:
            logger.error(f"❌ Chain {chain.value} not available")
            return False
    
    def get_solana_slot(self) -> Optional[int]:
        """Get current Solana slot"""
        if Chain.SOLANA not in self.chains:
            return None
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSlot"
            }
            response = self.session.post(
                self.chains[Chain.SOLANA].rpc_url, 
                json=payload, 
                timeout=10
            )
            data = response.json()
            return data.get('result')
        except Exception as e:
            logger.error(f"Failed to get slot: {e}")
            return None
    
    def get_evm_block_number(self, chain: Chain) -> Optional[int]:
        """Get current block number for EVM chain"""
        if chain not in self.chains or not self.chains[chain].web3:
            return None
        
        try:
            return self.chains[chain].web3.eth.block_number
        except Exception as e:
            logger.error(f"Failed to get block number for {chain.value}: {e}")
            return None
    
    def get_token_info_evm(self, token_address: str, chain: Chain) -> Optional[Dict]:
        """Get token info for EVM token (using ERC20 standard)"""
        if chain not in self.chains or not self.chains[chain].web3:
            return None
        
        try:
            # Minimal ERC20 ABI
            erc20_abi = [
                {"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},
                {"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
                {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},
                {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},
            ]
            
            web3 = self.chains[chain].web3
            checksum = Web3.to_checksum_address(token_address)
            contract = web3.eth.contract(address=checksum, abi=erc20_abi)
            
            # Call functions
            symbol = contract.functions.symbol().call()
            name = contract.functions.name().call()
            decimals = contract.functions.decimals().call()
            total_supply = contract.functions.totalSupply().call()
            
            return {
                'address': token_address,
                'symbol': symbol,
                'name': name,
                'decimals': decimals,
                'total_supply': total_supply / (10 ** decimals),
                'chain': chain.value,
                'explorer': f"{EXPLORERS[chain]}{token_address}"
            }
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return None
    
    def scan_new_launches(self, chain: Optional[Chain] = None) -> List[Dict]:
        """Scan for new token launches across chains"""
        target_chain = chain or self.active_chain
        
        # Placeholder - integrate with real APIs
        sample_launches = [
            {
                'address': '0x1234567890abcdef' * 4,
                'symbol': 'ALPHA1',
                'name': f'Alpha Token 1 ({target_chain.value.upper()})',
                'mcap': 50000,
                'volume': 15000,
                'timestamp': datetime.now().isoformat(),
                'source': 'dexscreener',
                'chain': target_chain.value,
                'explorer': f"{EXPLORERS.get(target_chain, '')}0x1234567890abcdef"
            },
            {
                'address': '0xabcdef1234567890' * 4,
                'symbol': 'GEM2',
                'name': f'Gem Token 2 ({target_chain.value.upper()})',
                'mcap': 75000,
                'volume': 22000,
                'timestamp': datetime.now().isoformat(),
                'source': 'pump.fun' if target_chain == Chain.SOLANA else 'dexscreener',
                'chain': target_chain.value,
                'explorer': f"{EXPLORERS.get(target_chain, '')}0xabcdef1234567890"
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
        
        # Chain multipliers
        chain = token_data.get('chain', '').lower()
        if chain == 'solana':
            score += 10  # Meme coin hotbed
        elif chain == 'bsc':
            score += 10  # Low fees, high volume
        elif chain in ['ethereum', 'arbitrum', 'base']:
            score += 5
        
        # Time since launch
        score += 5
        
        return min(score, 100)
    
    def display_welcome(self):
        """Display welcome screen"""
        welcome = """
╔═══════════════════════════════════════════════════════════════════╗
║        🔥 MULTI-CHAIN ALPHA TRADING TERMINAL v2.0 🔥               ║
║                                                                   ║
║       Solana • BSC • Ethereum • Polygon • Arbitrum • Base         ║
║                                                                   ║
║           CLI • Telegram Bot • Web Dashboard                     ║
╚═══════════════════════════════════════════════════════════════════╝

🌐 Supported Chains:
   ● Solana (SOL)      ● BSC (Binance Smart Chain)
   ● Ethereum (ETH)    ● Polygon (MATIC)
   ● Arbitrum (ARB)    ● Base

💡 Set custom RPC via environment variables:
   SOLANA_RPC_URL, BSC_RPC_URL, ETH_RPC_URL, etc.
        """
        print(welcome)
    
    def run_cli(self):
        """Run interactive CLI mode"""
        self.display_welcome()
        
        print("\n📊 Chain Status:")
        for chain, config in self.chains.items():
            status = "🟢" if config.connected else "🔴"
            print(f"   {status} {chain.value.upper()}: {config.rpc_url[:40]}...")
        print(f"\n🎯 Active Chain: {self.active_chain.value.upper()}")
        print()
        
        while True:
            print("\n┌─ Commands ─────────────────────────────────────┐")
            print("│ 1. Scan New Launches                           │")
            print("│ 2. Track Token                                 │")
            print("│ 3. View Tracked Tokens                         │")
            print("│ 4. Multi-Chain Scanner                         │")
            print("│ 5. Switch Chain                                │")
            print("│ 6. Token Info (EVM)                            │")
            print("│ 7. Vanity Wallet Generator 🎨                  │")
            print("│ 8. Pump.fun Deployer 🚀                        │")
            print("│ 9. Alpha Scanner Settings                      │")
            print("│ 10. Exit                                       │")
            print("└────────────────────────────────────────────────┘")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.cmd_scan_launches()
            elif choice == '2':
                self.cmd_track_token()
            elif choice == '3':
                self.cmd_view_tracked()
            elif choice == '4':
                self.cmd_multi_chain_scan()
            elif choice == '5':
                self.cmd_switch_chain()
            elif choice == '6':
                self.cmd_token_info()
            elif choice == '7':
                self.cmd_vanity_wallet()
            elif choice == '8':
                self.cmd_pump_fun_deploy()
            elif choice == '9':
                self.cmd_scanner_settings()
            elif choice == '10':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option")
    
    def cmd_scan_launches(self):
        """Scan for new launches on active chain"""
        print(f"\n🔍 Scanning {self.active_chain.value.upper()} for new launches...")
        launches = self.scan_new_launches()
        
        if not launches:
            print("No new launches found.")
            return
        
        print(f"\n🚀 Found {len(launches)} new launches:\n")
        print("-" * 80)
        
        for token in launches:
            alpha_score = self.calculate_alpha_score(token)
            
            print(f"\n🪙 {token['name']} (${token['symbol']})")
            print(f"   Chain: {token['chain'].upper()}")
            print(f"   Address: {token['address'][:30]}...")
            print(f"   Market Cap: ${token['mcap']:,.0f}")
            print(f"   Volume: ${token['volume']:,.0f}")
            print(f"   Source: {token['source']}")
            print(f"   🎯 Alpha Score: {alpha_score:.1f}/100 {'🔥' if alpha_score > 70 else ''}")
            
            if alpha_score > 70:
                print("   ⚠️ HIGH ALPHA POTENTIAL!")
        
        print("\n" + "-" * 80)
    
    def cmd_multi_chain_scan(self):
        """Scan all chains simultaneously"""
        print("\n🌐 Multi-Chain Scan Started...")
        print("Scanning all connected chains for new launches...\n")
        
        all_launches = []
        for chain in self.chains.keys():
            launches = self.scan_new_launches(chain)
            for launch in launches:
                launch['alpha_score'] = self.calculate_alpha_score(launch)
            all_launches.extend(launches)
        
        # Sort by alpha score
        all_launches.sort(key=lambda x: x['alpha_score'], reverse=True)
        
        print(f"\n🔥 Top Alpha Picks Across All Chains:\n")
        print("-" * 90)
        
        for i, token in enumerate(all_launches[:5], 1):
            print(f"\n{i}. �️ {token['name']} (${token['symbol']})")
            print(f"   Chain: {token['chain'].upper()}")
            print(f"   MCAP: ${token['mcap']:,.0f} | Vol: ${token['volume']:,.0f}")
            print(f"   ⭐ Alpha Score: {token['alpha_score']:.1f}/100")
            print(f"   🔗 {token.get('explorer', 'N/A')}")
        
        print("\n" + "-" * 90)
    
    def cmd_switch_chain(self):
        """Switch active chain"""
        print("\n🌐 Available chains:")
        chains = list(self.chains.keys())
        
        for i, chain in enumerate(chains, 1):
            print(f"   {i}. {chain.value.upper()}")
        
        try:
            choice = int(input("\nSelect chain: ")) - 1
            if 0 <= choice < len(chains):
                self.switch_chain(chains[choice])
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    def cmd_token_info(self):
        """Get token info for EVM chains"""
        if self.active_chain == Chain.SOLANA:
            print("❌ Token info command only available for EVM chains")
            print("💡 Switch to BSC, Ethereum, Polygon, or Arbitrum")
            return
        
        address = input("Enter token contract address: ").strip()
        
        print(f"\n🔍 Fetching token info from {self.active_chain.value.upper()}...")
        info = self.get_token_info_evm(address, self.active_chain)
        
        if info:
            print(f"\n🪙 Token: {info['name']} (${info['symbol']})")
            print(f"   Address: {info['address']}")
            print(f"   Decimals: {info['decimals']}")
            print(f"   Total Supply: {info['total_supply']:,.4f}")
            print(f"   Explorer: {info['explorer']}")
        else:
            print("❌ Failed to fetch token info")
    
    def cmd_track_token(self):
        """Add token to tracking list"""
        print(f"\n🎯 Add token to tracking on {self.active_chain.value.upper()}")
        address = input("Enter token address: ").strip()
        symbol = input("Enter symbol: ").strip()
        name = input("Enter name: ").strip()
        
        token = TokenConfig(
            address=address, 
            symbol=symbol, 
            name=name, 
            chain=self.active_chain
        )
        self.tracked_tokens.append(token)
        
        print(f"✅ Now tracking {name} (${symbol}) on {self.active_chain.value.upper()}")
    
    def cmd_view_tracked(self):
        """View tracked tokens"""
        if not self.tracked_tokens:
            print("No tokens being tracked.")
            return
        
        print(f"\n📊 Tracking {len(self.tracked_tokens)} tokens:\n")
        for token in self.tracked_tokens:
            print(f"  • {token.name} (${token.symbol}) - {token.chain.value.upper()}")
            print(f"    {token.address[:40]}...")
    
    def cmd_scanner_settings(self):
        """Configure scanner settings"""
        print("\n⚙️ Alpha Scanner Settings")
        print(f"  Min Market Cap: $30,000")
        print(f"  Max Market Cap: $150,000")
        print(f"  Min Volume: $5,000")
        print(f"  Alerts: {'ON' if self.alerts_enabled else 'OFF'}")
        print(f"  Active Chain: {self.active_chain.value.upper()}")
        
        toggle = input("\nToggle alerts? (y/n): ").strip().lower()
        if toggle == 'y':
            self.alerts_enabled = not self.alerts_enabled
            print(f"Alerts: {'ON' if self.alerts_enabled else 'OFF'}")
    
    def cmd_vanity_wallet(self):
        """Generate vanity wallet address"""
        try:
            from vanity_generator import VanityAddressGenerator
            
            print("""
╔══════════════════════════════════════════════════════════════════╗
║              🎨 ZERO Vanity Address Generator 🎨                ║
╚══════════════════════════════════════════════════════════════════╝
            """)
            
            generator = VanityAddressGenerator()
            
            pattern = input("Enter pattern to search (e.g., 'DOGE', '0000'): ").strip()
            
            if len(pattern) < 1:
                print("❌ Pattern required")
                return
            
            # Estimate difficulty
            estimate = generator.estimate_difficulty(pattern)
            
            print(f"\n📊 Difficulty:")
            print(f"   Pattern: {pattern}")
            print(f"   Estimated time: {estimate['estimated_time_formatted']}")
            print(f"   Difficulty: {estimate['difficulty']}")
            
            confirm = input("\n⚡ Start generation? (y/n): ").strip().lower()
            if confirm != 'y':
                return
            
            result = generator.generate_vanity_wallet(
                pattern=pattern,
                is_prefix=True,
                max_attempts=5000000
            )
            
            if result:
                print(f"\n✅ VANITY ADDRESS FOUND!")
                print(f"   Address: {result.address}")
                print(f"   Private Key: {result.private_key[:30]}...")
                print(f"   Attempts: {result.attempts:,}")
                print(f"   Time: {result.time_taken:.2f}s")
                
                save = input("\n💾 Save to file? (y/n): ").strip().lower()
                if save == 'y':
                    generator.save_wallet(result)
                    print("✅ Wallet saved!")
            else:
                print("❌ Pattern not found. Try a shorter pattern.")
                
        except ImportError:
            print("❌ Vanity generator requires 'solders' library")
            print("💡 Install: pip install solders")
    
    def cmd_pump_fun_deploy(self):
        """Create Pump.fun token deployment"""
        try:
            from vanity_generator import PumpFunDeployer
            
            print("""
╔══════════════════════════════════════════════════════════════════╗
║              🚀 Pump.fun Token Deployer 🚀                      ║
╚══════════════════════════════════════════════════════════════════╝
            """)
            
            name = input("Token Name: ").strip()
            symbol = input("Token Symbol: ").strip().upper()
            description = input("Description: ").strip()
            image_url = input("Image URL (or leave blank): ").strip()
            
            print("\n🎨 Vanity Mint Address (optional)")
            print("   Leave blank to skip (saves time)")
            vanity_pattern = input("Pattern (e.g., 'DOGE', 'Lambo'): ").strip()
            
            deployer = PumpFunDeployer()
            
            config = deployer.create_token_config(
                name=name,
                symbol=symbol,
                description=description,
                image_url=image_url or "https://example.com/image.png",
                vanity_pattern=vanity_pattern if vanity_pattern else None
            )
            
            # Show deployment info
            costs = deployer.estimate_deployment_cost()
            
            print(f"\n📋 Token Configuration:")
            print(f"   Name: {config['name']}")
            print(f"   Symbol: {config['symbol']}")
            print(f"   Description: {config['description']}")
            
            if 'vanity_mint' in config:
                print(f"\n🏆 Vanity Mint:")
                print(f"   Address: {config['vanity_mint']['address']}")
                print(f"   Pattern: {config['vanity_mint']['pattern']}")
                print(f"   Attempts: {config['vanity_mint']['attempts']:,}")
            
            print(f"\n💰 Estimated Costs:")
            print(f"   Pump.fun Fee: {costs['pump_fun_fee']} SOL")
            print(f"   Rent Exempt: {costs['rent_exempt']} SOL")
            print(f"   Total: ~{costs['total_sol']} SOL")
            print(f"   Recommendation: {costs['recommendation']}")
            
            # Generate script
            deployer.generate_deploy_script(config)
            
            print("\n⚠️  IMPORTANT:")
            print("   This creates a TEMPLATE deployment script.")
            print("   For actual deployment:")
            print("   1. Visit pump.fun and connect your wallet")
            print("   2. Use the Solana CLI with Pump.fun program")
            print("   3. Or modify the generated script with real solana-py")
            
        except ImportError:
            print("❌ Deployer requires 'solders' library")
            print("💡 Install: pip install solders")


def main():
    parser = argparse.ArgumentParser(description='Multi-Chain Alpha Trading Terminal')
    parser.add_argument('--chain', choices=['solana', 'bsc', 'ethereum', 'polygon', 'arbitrum', 'base'],
                       default='solana', help='Active chain (default: solana)')
    parser.add_argument('--telegram', action='store_true', help='Run Telegram bot mode')
    parser.add_argument('--scan-all', action='store_true', help='Scan all chains')
    
    args = parser.parse_args()
    
    terminal = MultiChainAlphaTerminal()
    
    # Set initial chain
    chain_map = {
        'solana': Chain.SOLANA,
        'bsc': Chain.BSC,
        'ethereum': Chain.ETHEREUM,
        'polygon': Chain.POLYGON,
        'arbitrum': Chain.ARBITRUM,
        'base': Chain.BASE,
    }
    terminal.switch_chain(chain_map.get(args.chain, Chain.SOLANA))
    
    if args.telegram:
        print("🤖 Starting Telegram bot mode...")
        print("💡 To run Telegram bot: python3 telegram_bot.py")
    elif args.scan_all:
        print("🌐 Multi-chain scan mode...")
        terminal.cmd_multi_chain_scan()
    else:
        terminal.run_cli()


if __name__ == '__main__':
    main()
