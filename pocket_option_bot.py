import os
import time
import random
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Import custom modules
from config import BotConfig
from strategies import get_strategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PocketOptionBot")

# Load environment variables
load_dotenv()

class PocketOptionBot:
    def __init__(self, config=None):
        # Load configuration
        self.config = config or BotConfig().get_config()

        # Authentication
        self.email = os.getenv("POCKET_OPTION_EMAIL")
        self.password = os.getenv("POCKET_OPTION_PASSWORD")

        # Trading parameters
        self.driver = None
        self.balance = 0
        self.current_asset = self.config["trading"]["asset"]
        self.trade_amount = self.config["trading"]["trade_amount"]
        self.expiry_minutes = self.config["trading"]["expiry_minutes"]

        # Risk management
        self.martingale_enabled = self.config["risk_management"]["martingale_enabled"]
        self.martingale_coefficient = self.config["risk_management"]["martingale_coefficient"]
        self.martingale_stack = []
        self.max_martingale_level = self.config["risk_management"]["max_martingale_level"]
        self.max_daily_loss = self.config["risk_management"]["max_daily_loss"]
        self.max_daily_trades = self.config["risk_management"]["max_daily_trades"]

        # Strategy
        self.strategy_type = self.config["strategy"]["type"]
        self.strategy_params = self.config["strategy"]["parameters"]
        self.strategy = get_strategy(self.strategy_type, self.strategy_params)

        # Session data
        self.trade_history = []
        self.daily_loss = 0
        self.daily_trades = 0

        # Initialize WebDriver
        self.setup_driver()

    def setup_driver(self):
        """Initialize the WebDriver for browser automation"""
        logger.info("Setting up WebDriver...")
        chrome_options = Options()
        # Uncomment the line below to run in headless mode (no browser window)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def login(self):
        """Login to Pocket Option platform"""
        logger.info("Logging in to Pocket Option...")
        try:
            self.driver.get("https://pocketoption.com/en/login/")

            # Wait for the login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )

            # Enter login credentials
            self.driver.find_element(By.ID, "email").send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)

            # Click login button
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

            # Wait for the trading platform to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "trading-platform"))
            )

            logger.info("Successfully logged in")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def get_balance(self):
        """Get current account balance"""
        try:
            balance_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "balance-value"))
            )
            balance_text = balance_element.text.strip().replace("$", "").replace(",", "")
            self.balance = float(balance_text)
            logger.info(f"Current balance: ${self.balance}")
            return self.balance
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return None

    def select_asset(self, asset_name="EUR/USD"):
        """Select a trading asset"""
        try:
            logger.info(f"Selecting asset: {asset_name}")

            # Click on asset selector
            asset_selector = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "asset-selector"))
            )
            asset_selector.click()

            # Wait for asset list to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "asset-list"))
            )

            # Find and click on the specified asset
            asset_element = self.driver.find_element(
                By.XPATH, f"//div[contains(@class, 'asset-item') and contains(text(), '{asset_name}')]"
            )
            asset_element.click()

            self.current_asset = asset_name
            logger.info(f"Asset selected: {asset_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to select asset: {str(e)}")
            return False

    def get_market_data(self, timeframe="1m", num_candles=20):
        """Get market data for analysis"""
        try:
            logger.info(f"Getting market data for {self.current_asset}, timeframe: {timeframe}")

            # This is a placeholder - in a real implementation, you would extract
            # price data from the DOM or use WebSocket connections if possible

            # For now, we'll simulate getting candle data
            # In a real implementation, you would parse this from the chart
            candles = []
            for i in range(num_candles):
                # Simulate candle data (open, high, low, close)
                open_price = 1.1000 + random.uniform(-0.0050, 0.0050)
                high_price = open_price + random.uniform(0.0001, 0.0020)
                low_price = open_price - random.uniform(0.0001, 0.0020)
                close_price = open_price + random.uniform(-0.0015, 0.0015)

                candle = {
                    'timestamp': datetime.now().timestamp() - (num_candles - i) * 60,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': random.uniform(10, 100)
                }
                candles.append(candle)

            df = pd.DataFrame(candles)
            logger.info(f"Retrieved {len(df)} candles")
            return df
        except Exception as e:
            logger.error(f"Failed to get market data: {str(e)}")
            return None

    def analyze_market(self, data):
        """Analyze market data and decide on trade direction"""
        try:
            logger.info(f"Analyzing market data using {self.strategy_type} strategy...")

            # Use the configured strategy to analyze the market
            direction = self.strategy.analyze(data)

            if direction:
                logger.info(f"Analysis result: {direction.upper()} signal detected")
            else:
                logger.info("No clear trading signal detected")

            return direction
        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return None

    def place_trade(self, direction, amount, expiry_minutes=None):
        """Place a trade on Pocket Option"""
        if expiry_minutes is None:
            expiry_minutes = self.expiry_minutes

        try:
            # Check risk management limits
            if self.daily_trades >= self.max_daily_trades:
                logger.warning(f"Maximum daily trades limit reached ({self.max_daily_trades}). Skipping trade.")
                return False

            if self.daily_loss >= self.max_daily_loss:
                logger.warning(f"Maximum daily loss limit reached (${self.max_daily_loss}). Skipping trade.")
                return False

            logger.info(f"Placing {direction.upper()} trade for ${amount} with {expiry_minutes} minute(s) expiry")

            # Set trade amount
            amount_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "amount-input"))
            )
            amount_input.clear()
            amount_input.send_keys(str(amount))

            # Set expiry time
            expiry_selector = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "expiry-selector"))
            )
            expiry_selector.click()

            # Select the expiry time from dropdown
            expiry_option = self.driver.find_element(
                By.XPATH, f"//div[contains(@class, 'expiry-option') and contains(text(), '{expiry_minutes}m')]"
            )
            expiry_option.click()

            # Click on Call or Put button
            if direction.lower() == "call":
                call_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "call-button"))
                )
                call_button.click()
            else:
                put_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "put-button"))
                )
                put_button.click()

            # Record the trade
            trade = {
                'timestamp': datetime.now(),
                'asset': self.current_asset,
                'direction': direction,
                'amount': amount,
                'expiry_minutes': expiry_minutes,
                'status': 'pending',
                'martingale_level': len([t for t in self.trade_history if t['status'] == 'loss']) if self.martingale_enabled else 0
            }
            self.trade_history.append(trade)
            self.daily_trades += 1

            logger.info(f"Trade placed: {direction.upper()} ${amount}")
            return True
        except Exception as e:
            logger.error(f"Failed to place trade: {str(e)}")
            return False

    def check_trade_result(self, wait_time_seconds=70):
        """Check the result of the last trade"""
        try:
            logger.info(f"Waiting {wait_time_seconds} seconds for trade to complete...")
            time.sleep(wait_time_seconds)

            # In a real implementation, you would check the trade result from the DOM
            # For now, we'll simulate a random result
            result = random.choice(["win", "loss"])

            # Update the last trade record
            if self.trade_history:
                last_trade = self.trade_history[-1]
                last_trade['status'] = result

                # Update daily loss if the trade was a loss
                if result == "loss":
                    self.daily_loss += last_trade['amount']

            logger.info(f"Trade result: {result.upper()}")
            return result
        except Exception as e:
            logger.error(f"Failed to check trade result: {str(e)}")
            return None

    def calculate_martingale_amount(self, last_result):
        """Calculate the next trade amount using Martingale strategy"""
        if not self.martingale_enabled:
            return self.trade_amount

        if not self.martingale_stack:
            # Initialize the Martingale stack
            self.martingale_stack = [self.trade_amount]
            for i in range(1, self.max_martingale_level):
                next_amount = self.martingale_stack[i-1] * self.martingale_coefficient
                self.martingale_stack.append(round(next_amount, 2))

        if last_result == "win":
            # Reset to the initial amount after a win
            return self.martingale_stack[0]
        else:
            # Increase the amount after a loss
            current_level = self.trade_history[-1].get('martingale_level', 0)
            next_level = min(current_level + 1, self.max_martingale_level - 1)
            return self.martingale_stack[next_level]

    def run_trading_session(self, duration_minutes=None, trade_interval_minutes=None):
        """Run an automated trading session"""
        # Use configuration values if not provided
        if duration_minutes is None:
            duration_minutes = self.config["trading"]["session_duration_minutes"]

        if trade_interval_minutes is None:
            trade_interval_minutes = self.config["trading"]["trade_interval_minutes"]

        logger.info(f"Starting trading session for {duration_minutes} minutes")
        logger.info(f"Strategy: {self.strategy_type}")
        logger.info(f"Asset: {self.current_asset}")
        logger.info(f"Trade amount: ${self.trade_amount}")
        logger.info(f"Martingale enabled: {self.martingale_enabled}")

        # Reset session counters
        self.daily_trades = 0
        self.daily_loss = 0

        start_time = datetime.now()
        end_time = start_time + pd.Timedelta(minutes=duration_minutes)

        # Login to the platform
        if not self.login():
            logger.error("Failed to login. Aborting trading session.")
            return

        # Get initial balance
        initial_balance = self.get_balance()

        # Select asset
        if not self.select_asset(self.current_asset):
            logger.error("Failed to select asset. Aborting trading session.")
            return

        # Main trading loop
        while datetime.now() < end_time:
            try:
                # Check if we've reached daily limits
                if self.daily_trades >= self.max_daily_trades:
                    logger.warning(f"Maximum daily trades limit reached ({self.max_daily_trades}). Stopping session.")
                    break

                if self.daily_loss >= self.max_daily_loss:
                    logger.warning(f"Maximum daily loss limit reached (${self.max_daily_loss}). Stopping session.")
                    break

                # Get market data
                market_data = self.get_market_data()
                if market_data is None:
                    logger.warning("Failed to get market data. Skipping this trade.")
                    time.sleep(60)  # Wait a minute before trying again
                    continue

                # Analyze market and get trade direction
                direction = self.analyze_market(market_data)
                if direction is None:
                    logger.warning("No clear trading signal. Skipping this trade.")
                    time.sleep(60)
                    continue

                # Determine trade amount (using Martingale if enabled)
                if self.trade_history and self.martingale_enabled:
                    last_result = self.trade_history[-1]['status']
                    amount = self.calculate_martingale_amount(last_result)
                else:
                    amount = self.trade_amount

                # Place the trade
                if not self.place_trade(direction, amount):
                    logger.warning("Failed to place trade. Skipping this cycle.")
                    time.sleep(60)
                    continue

                # Check trade result and update statistics
                trade_result = self.check_trade_result()

                # Log current session statistics
                wins = sum(1 for trade in self.trade_history if trade['status'] == 'win')
                losses = sum(1 for trade in self.trade_history if trade['status'] == 'loss')
                win_rate = (wins / len(self.trade_history)) * 100 if self.trade_history else 0

                logger.info(f"Session stats - Trades: {len(self.trade_history)}, Wins: {wins}, Losses: {losses}, Win rate: {win_rate:.2f}%")
                logger.info(f"Daily loss: ${self.daily_loss}")

                # Wait until the next trade interval
                next_trade_time = datetime.now() + pd.Timedelta(minutes=trade_interval_minutes)
                wait_seconds = (next_trade_time - datetime.now()).total_seconds()
                if wait_seconds > 0:
                    logger.info(f"Waiting {wait_seconds:.0f} seconds until next trade")
                    time.sleep(wait_seconds)

            except Exception as e:
                logger.error(f"Error during trading cycle: {str(e)}")
                time.sleep(60)  # Wait a minute before continuing

        # Get final balance
        final_balance = self.get_balance()
        profit = final_balance - initial_balance if final_balance and initial_balance else None

        # Log session summary
        logger.info("Trading session completed")
        logger.info(f"Initial balance: ${initial_balance}")
        logger.info(f"Final balance: ${final_balance}")
        logger.info(f"Profit/Loss: ${profit}")

        # Generate trade statistics
        wins = sum(1 for trade in self.trade_history if trade['status'] == 'win')
        losses = sum(1 for trade in self.trade_history if trade['status'] == 'loss')
        total_trades = len(self.trade_history)
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

        logger.info(f"Total trades: {total_trades}")
        logger.info(f"Wins: {wins}, Losses: {losses}")
        logger.info(f"Win rate: {win_rate:.2f}%")

    def close(self):
        """Close the WebDriver and clean up"""
        if self.driver:
            logger.info("Closing WebDriver...")
            self.driver.quit()
            self.driver = None


if __name__ == "__main__":
    try:
        # Load configuration
        config = BotConfig()

        # Ask user if they want to configure the bot
        configure = input("Do you want to configure the bot before starting? (y/n): ").lower() == 'y'
        if configure:
            config.setup_interactive()

        # Create and configure the bot
        bot = PocketOptionBot(config.get_config())

        # Run a trading session
        bot.run_trading_session()

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
    finally:
        # Make sure to close the WebDriver
        if 'bot' in locals() and bot.driver:
            bot.close()
