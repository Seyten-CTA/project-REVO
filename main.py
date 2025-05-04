#!/usr/bin/env python3
"""
Pocket Option Trading Bot - Main Script
A simple trading bot for Pocket Option platform
"""

import os
import sys
import logging
import argparse
from config import BotConfig
from pocket_option_bot import PocketOptionBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PocketOptionBot.Main")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Pocket Option Trading Bot')
    
    parser.add_argument('--configure', action='store_true', 
                        help='Configure the bot before starting')
    
    parser.add_argument('--duration', type=int, default=None,
                        help='Trading session duration in minutes')
    
    parser.add_argument('--interval', type=int, default=None,
                        help='Interval between trades in minutes')
    
    parser.add_argument('--asset', type=str, default=None,
                        help='Asset to trade (e.g., EUR/USD)')
    
    parser.add_argument('--amount', type=float, default=None,
                        help='Trade amount in dollars')
    
    parser.add_argument('--strategy', type=str, choices=['trend_following', 'rsi', 'random'], 
                        default=None, help='Trading strategy to use')
    
    parser.add_argument('--martingale', action='store_true',
                        help='Enable Martingale strategy')
    
    parser.add_argument('--no-martingale', action='store_true',
                        help='Disable Martingale strategy')
    
    return parser.parse_args()

def main():
    """Main function to run the bot"""
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Load configuration
        config = BotConfig()
        
        # Configure the bot if requested
        if args.configure:
            config.setup_interactive()
        else:
            # Apply command line overrides to configuration
            cfg = config.get_config()
            
            if args.asset:
                cfg["trading"]["asset"] = args.asset
                
            if args.amount:
                cfg["trading"]["trade_amount"] = args.amount
                
            if args.duration:
                cfg["trading"]["session_duration_minutes"] = args.duration
                
            if args.interval:
                cfg["trading"]["trade_interval_minutes"] = args.interval
                
            if args.strategy:
                cfg["strategy"]["type"] = args.strategy
                
            if args.martingale:
                cfg["risk_management"]["martingale_enabled"] = True
                
            if args.no_martingale:
                cfg["risk_management"]["martingale_enabled"] = False
                
            config.update_config(cfg)
        
        # Create and configure the bot
        bot = PocketOptionBot(config.get_config())
        
        # Display configuration
        print("\n===== Pocket Option Trading Bot =====")
        print(f"Asset: {bot.current_asset}")
        print(f"Trade amount: ${bot.trade_amount}")
        print(f"Strategy: {bot.strategy_type}")
        print(f"Martingale enabled: {bot.martingale_enabled}")
        print(f"Session duration: {bot.config['trading']['session_duration_minutes']} minutes")
        print(f"Trade interval: {bot.config['trading']['trade_interval_minutes']} minutes")
        print("=====================================\n")
        
        # Confirm start
        confirm = input("Start trading session? (y/n): ").lower()
        if confirm != 'y':
            print("Trading session cancelled.")
            return
        
        # Run a trading session
        bot.run_trading_session()
        
    except KeyboardInterrupt:
        logger.info("Trading session interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
    finally:
        # Make sure to close the WebDriver
        if 'bot' in locals() and hasattr(bot, 'driver') and bot.driver:
            bot.close()

if __name__ == "__main__":
    main()
