import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BotConfig:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config file: {str(e)}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration"""
        return {
            "trading": {
                "asset": "EUR/USD",
                "trade_amount": 1,
                "expiry_minutes": 1,
                "trade_interval_minutes": 5,
                "session_duration_minutes": 60
            },
            "strategy": {
                "type": "trend_following",  # Options: trend_following, rsi, random
                "parameters": {
                    "short_period": 5,
                    "long_period": 10,
                    "rsi_period": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30
                }
            },
            "risk_management": {
                "martingale_enabled": False,
                "martingale_coefficient": 2.1,
                "max_martingale_level": 5,
                "max_daily_loss": 20,  # in dollars
                "max_daily_trades": 20
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving config file: {str(e)}")
            return False
    
    def update_config(self, new_config):
        """Update configuration with new values"""
        self.config.update(new_config)
        return self.save_config()
    
    def get_config(self):
        """Get current configuration"""
        return self.config
    
    def setup_interactive(self):
        """Interactive configuration setup"""
        print("\n===== Pocket Option Trading Bot Configuration =====\n")
        
        # Trading settings
        print("\n--- Trading Settings ---")
        self.config["trading"]["asset"] = input(f"Asset to trade [{self.config['trading']['asset']}]: ") or self.config["trading"]["asset"]
        
        try:
            self.config["trading"]["trade_amount"] = float(input(f"Trade amount in $ [{self.config['trading']['trade_amount']}]: ") or self.config["trading"]["trade_amount"])
        except ValueError:
            print("Invalid input. Using default value.")
        
        try:
            self.config["trading"]["expiry_minutes"] = int(input(f"Expiry time in minutes [{self.config['trading']['expiry_minutes']}]: ") or self.config["trading"]["expiry_minutes"])
        except ValueError:
            print("Invalid input. Using default value.")
        
        try:
            self.config["trading"]["trade_interval_minutes"] = int(input(f"Interval between trades in minutes [{self.config['trading']['trade_interval_minutes']}]: ") or self.config["trading"]["trade_interval_minutes"])
        except ValueError:
            print("Invalid input. Using default value.")
        
        try:
            self.config["trading"]["session_duration_minutes"] = int(input(f"Trading session duration in minutes [{self.config['trading']['session_duration_minutes']}]: ") or self.config["trading"]["session_duration_minutes"])
        except ValueError:
            print("Invalid input. Using default value.")
        
        # Strategy settings
        print("\n--- Strategy Settings ---")
        strategy_types = ["trend_following", "rsi", "random"]
        print("Available strategies:")
        for i, strategy in enumerate(strategy_types):
            print(f"{i+1}. {strategy}")
        
        try:
            strategy_choice = int(input(f"Select strategy (1-{len(strategy_types)}): ")) - 1
            if 0 <= strategy_choice < len(strategy_types):
                self.config["strategy"]["type"] = strategy_types[strategy_choice]
            else:
                print("Invalid choice. Using default strategy.")
        except ValueError:
            print("Invalid input. Using default strategy.")
        
        if self.config["strategy"]["type"] == "trend_following":
            try:
                self.config["strategy"]["parameters"]["short_period"] = int(input(f"Short period [{self.config['strategy']['parameters']['short_period']}]: ") or self.config["strategy"]["parameters"]["short_period"])
                self.config["strategy"]["parameters"]["long_period"] = int(input(f"Long period [{self.config['strategy']['parameters']['long_period']}]: ") or self.config["strategy"]["parameters"]["long_period"])
            except ValueError:
                print("Invalid input. Using default values.")
        
        elif self.config["strategy"]["type"] == "rsi":
            try:
                self.config["strategy"]["parameters"]["rsi_period"] = int(input(f"RSI period [{self.config['strategy']['parameters']['rsi_period']}]: ") or self.config["strategy"]["parameters"]["rsi_period"])
                self.config["strategy"]["parameters"]["rsi_overbought"] = int(input(f"RSI overbought level [{self.config['strategy']['parameters']['rsi_overbought']}]: ") or self.config["strategy"]["parameters"]["rsi_overbought"])
                self.config["strategy"]["parameters"]["rsi_oversold"] = int(input(f"RSI oversold level [{self.config['strategy']['parameters']['rsi_oversold']}]: ") or self.config["strategy"]["parameters"]["rsi_oversold"])
            except ValueError:
                print("Invalid input. Using default values.")
        
        # Risk management settings
        print("\n--- Risk Management Settings ---")
        martingale_choice = input(f"Enable Martingale strategy? (y/n) [{('y' if self.config['risk_management']['martingale_enabled'] else 'n')}]: ").lower() or ('y' if self.config['risk_management']['martingale_enabled'] else 'n')
        self.config["risk_management"]["martingale_enabled"] = martingale_choice == 'y'
        
        if self.config["risk_management"]["martingale_enabled"]:
            try:
                self.config["risk_management"]["martingale_coefficient"] = float(input(f"Martingale coefficient [{self.config['risk_management']['martingale_coefficient']}]: ") or self.config["risk_management"]["martingale_coefficient"])
                self.config["risk_management"]["max_martingale_level"] = int(input(f"Max Martingale level [{self.config['risk_management']['max_martingale_level']}]: ") or self.config["risk_management"]["max_martingale_level"])
            except ValueError:
                print("Invalid input. Using default values.")
        
        try:
            self.config["risk_management"]["max_daily_loss"] = float(input(f"Max daily loss in $ [{self.config['risk_management']['max_daily_loss']}]: ") or self.config["risk_management"]["max_daily_loss"])
            self.config["risk_management"]["max_daily_trades"] = int(input(f"Max daily trades [{self.config['risk_management']['max_daily_trades']}]: ") or self.config["risk_management"]["max_daily_trades"])
        except ValueError:
            print("Invalid input. Using default values.")
        
        # Save configuration
        self.save_config()
        print("\nConfiguration completed successfully!")


if __name__ == "__main__":
    config = BotConfig()
    config.setup_interactive()
