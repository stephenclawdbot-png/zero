#!/usr/bin/env python3
"""
Vanity Address Generator for Solana
Generate wallets and token contracts with custom prefixes/suffixes
"""

import os
import time
import json
import base58
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
import itertools

# Solana imports
try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    logging.warning("solders not installed. Install with: pip install solders")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VanityResult:
    """Result of vanity address generation"""
    address: str
    private_key: str  # Base58 encoded
    mnemonic: Optional[str]
    attempts: int
    time_taken: float
    pattern: str


class VanityAddressGenerator:
    """Generate Solana vanity addresses"""
    
    def __init__(self):
        self.attempts = 0
        self.start_time = None
        
    def _generate_keypair(self) -> Tuple[str, str]:
        """Generate a random keypair and return (address, private_key)"""
        if not SOLANA_AVAILABLE:
            raise ImportError("solders library required. Install: pip install solders")
        
        keypair = Keypair()
        address = str(keypair.pubkey())
        private_key = base58.b58encode(bytes(keypair.secret())).decode('ascii')
        
        return address, private_key
    
    def _matches_pattern(self, address: str, pattern: str, 
                         is_prefix: bool = True, is_suffix: bool = False,
                         case_sensitive: bool = False) -> bool:
        """Check if address matches pattern"""
        check_addr = address if case_sensitive else address.lower()
        check_pattern = pattern if case_sensitive else pattern.lower()
        
        if is_prefix and check_addr.startswith(check_pattern):
            return True
        if is_suffix and check_addr.endswith(check_pattern):
            return True
        if pattern in check_addr:
            return True
        
        return False
    
    def generate_vanity_wallet(self, pattern: str, 
                               is_prefix: bool = True,
                               is_suffix: bool = False,
                               case_sensitive: bool = False,
                               max_attempts: int = 1000000) -> Optional[VanityResult]:
        """
        Generate vanity wallet address
        
        Args:
            pattern: Pattern to match (e.g., "DOGE", "0000")
            is_prefix: Match at start of address
            is_suffix: Match at end of address
            case_sensitive: Case sensitive matching
            max_attempts: Maximum attempts before giving up
        
        Returns:
            VanityResult with address and keys, or None if max attempts reached
        """
        if not SOLANA_AVAILABLE:
            logger.error("solders library not installed")
            return None
        
        self.start_time = time.time()
        self.attempts = 0
        
        logger.info(f"🎯 Searching for address with pattern: '{pattern}'")
        logger.info(f"   Prefix: {is_prefix}, Suffix: {is_suffix}, Case-sensitive: {case_sensitive}")
        
        while self.attempts < max_attempts:
            address, private_key = self._generate_keypair()
            self.attempts += 1
            
            if self.attempts % 10000 == 0:
                elapsed = time.time() - self.start_time
                rate = self.attempts / elapsed if elapsed > 0 else 0
                logger.info(f"⏳ Attempts: {self.attempts:,} | Rate: {rate:,.0f}/s")
            
            if self._matches_pattern(address, pattern, is_prefix, is_suffix, case_sensitive):
                elapsed = time.time() - self.start_time
                
                logger.info(f"✅ FOUND! Address: {address}")
                logger.info(f"   Attempts: {self.attempts:,}")
                logger.info(f"   Time: {elapsed:.2f}s")
                
                return VanityResult(
                    address=address,
                    private_key=private_key,
                    mnemonic=None,  # Would need separate mnemonic generation
                    attempts=self.attempts,
                    time_taken=elapsed,
                    pattern=pattern
                )
        
        logger.warning(f"❌ Max attempts ({max_attempts:,}) reached without finding match")
        return None
    
    def estimate_difficulty(self, pattern: str) -> dict:
        """Estimate difficulty/time to find pattern"""
        length = len(pattern)
        
        # Base58 charset has 58 characters
        combinations = 58 ** length
        
        # Estimated attempts needed (50% probability)
        estimated_attempts = combinations / 2
        
        # Assuming ~50,000 attempts/second on average CPU
        estimated_seconds = estimated_attempts / 50000
        
        difficulty_level = "EASY" if length <= 3 else \
                          "MEDIUM" if length <= 4 else \
                          "HARD" if length <= 5 else \
                          "EXTREME"
        
        return {
            'pattern_length': length,
            'combinations': combinations,
            'estimated_attempts': int(estimated_attempts),
            'estimated_time_seconds': estimated_seconds,
            'estimated_time_formatted': self._format_time(estimated_seconds),
            'difficulty': difficulty_level
        }
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds into readable time"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}h"
        else:
            return f"{seconds/86400:.1f}d"
    
    def save_wallet(self, result: VanityResult, filename: Optional[str] = None):
        """Save wallet to file"""
        if filename is None:
            filename = f"vanity_wallet_{result.pattern}.json"
        
        wallet_data = {
            'address': result.address,
            'private_key': result.private_key,
            'pattern': result.pattern,
            'attempts': result.attempts,
            'time_taken': result.time_taken,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        logger.info(f"💾 Wallet saved to: {filename}")
        
        # Also save as importable format
        with open(f"{filename}.key", 'w') as f:
            f.write(result.private_key)
        
        logger.info(f"🔑 Private key saved to: {filename}.key")


class PumpFunDeployer:
    """
    Helper for Pump.fun token deployment
    Includes vanity address generation for token contracts
    """
    
    def __init__(self):
        self.vanity_gen = VanityAddressGenerator()
    
    def create_token_config(self, 
                          name: str,
                          symbol: str,
                          description: str,
                          image_url: str,
                          vanity_pattern: Optional[str] = None) -> dict:
        """
        Create token deployment configuration
        
        Args:
            name: Token name
            symbol: Token symbol
            description: Token description
            image_url: Token image URL
            vanity_pattern: Optional vanity pattern for mint address
        """
        config = {
            'name': name,
            'symbol': symbol,
            'description': description,
            'image': image_url,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Generate vanity mint address if requested
        if vanity_pattern:
            logger.info(f"🎨 Generating vanity mint address with pattern: {vanity_pattern}")
            vanity_result = self.vanity_gen.generate_vanity_wallet(
                pattern=vanity_pattern,
                is_prefix=True,
                max_attempts=500000
            )
            
            if vanity_result:
                config['vanity_mint'] = {
                    'address': vanity_result.address,
                    'private_key': vanity_result.private_key,
                    'pattern': vanity_pattern,
                    'attempts': vanity_result.attempts
                }
                logger.info(f"✅ Vanity mint generated: {vanity_result.address}")
            else:
                logger.warning("❌ Could not generate vanity mint in time limit")
        
        return config
    
    def generate_deploy_script(self, token_config: dict, output_file: str = "deploy_token.py"):
        """
        Generate Python deployment script for Pump.fun
        
        This creates a script that can be run to deploy the token
        """
        script = f'''#!/usr/bin/env python3
"""
Pump.fun Token Deployment Script
Generated by Zero Vanity Generator
"""

import requests
import json
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

# Token Configuration
TOKEN_CONFIG = {json.dumps(token_config, indent=2)}

# Pump.fun API endpoint (placeholder)
PUMP_FUN_API = "https://pump.fun/api"

def deploy_token():
    """
    Deploy token to Pump.fun
    
    NOTE: This is a template/placeholder. Actual Pump.fun deployment
    requires specific smart contract interactions via Solana web3.
    
    For real deployment:
    1. Use Pump.fun website directly
    2. Or use solana-py + Pump.fun SDK
    3. Pay deployment fee (~0.02 SOL)
    """
    
    print("🚀 Pump.fun Token Deployment")
    print(f"Name: {{TOKEN_CONFIG['name']}}")
    print(f"Symbol: {{TOKEN_CONFIG['symbol']}}")
    print(f"Description: {{TOKEN_CONFIG['description']}}")
    
    if 'vanity_mint' in TOKEN_CONFIG:
        print(f"🏆 Vanity Mint: {{TOKEN_CONFIG['vanity_mint']['address']}}")
        print(f"   Pattern: {{TOKEN_CONFIG['vanity_mint']['pattern']}}")
    
    print("\\n⚠️  This is a template script.")
    print("   For real deployment, use:")
    print("   1. Pump.fun website (pump.fun)")
    print("   2. Solana CLI with Pump.fun program")
    print("   3. Custom script using solana-py")
    
    # Save config
    with open('token_config.json', 'w') as f:
        json.dump(TOKEN_CONFIG, f, indent=2)
    
    print("\\n💾 Configuration saved to token_config.json")

if __name__ == '__main__':
    deploy_token()
'''
        
        with open(output_file, 'w') as f:
            f.write(script)
        
        os.chmod(output_file, 0o755)
        
        logger.info(f"🚀 Deployment script generated: {output_file}")
        logger.info("   Run: python3 " + output_file)
    
    def estimate_deployment_cost(self) -> dict:
        """Estimate costs for Pump.fun deployment"""
        return {
            'pump_fun_fee': 0.02,  # SOL
            'rent_exempt': 0.002,  # SOL for mint account
            'total_sol': 0.022,    # SOL
            'recommendation': 'Keep 0.05 SOL minimum for fees'
        }


def run_vanity_cli():
    """Run vanity address generator CLI"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║              🎨 ZERO Vanity Address Generator 🎨                ║
║                                                                  ║
║         Generate custom wallet addresses for Solana             ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    generator = VanityAddressGenerator()
    
    print("Enter pattern to search for (e.g., 'DOGE', '0000', '1337')")
    print("Note: Longer patterns = exponentially harder to find\n")
    
    pattern = input("Pattern: ").strip()
    
    if len(pattern) < 1:
        print("❌ Pattern required")
        return
    
    # Estimate difficulty
    estimate = generator.estimate_difficulty(pattern)
    
    print(f"\n📊 Difficulty Estimate:")
    print(f"   Pattern length: {estimate['pattern_length']}")
    print(f"   Combinations: {estimate['combinations']:,}")
    print(f"   Estimated time: {estimate['estimated_time_formatted']}")
    print(f"   Difficulty: {estimate['difficulty']}")
    
    confirm = input("\n⚡ Start generation? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Generate
    result = generator.generate_vanity_wallet(
        pattern=pattern,
        is_prefix=True,
        max_attempts=10000000  # 10 million attempts
    )
    
    if result:
        print(f"\n✅ VANITY ADDRESS FOUND!")
        print(f"   Address: {result.address}")
        print(f"   Private Key: {result.private_key[:20]}...")
        print(f"   Attempts: {result.attempts:,}")
        print(f"   Time: {result.time_taken:.2f}s")
        
        save = input("\n💾 Save to file? (y/n): ").strip().lower()
        if save == 'y':
            generator.save_wallet(result)
    else:
        print("\n❌ Could not find matching address in time limit")


if __name__ == '__main__':
    run_vanity_cli()
