import pandas as pd
import numpy as np
import random
import logging

logger = logging.getLogger("PocketOptionBot.Strategies")

class TradingStrategy:
    """Base class for trading strategies"""
    def __init__(self, parameters=None):
        self.parameters = parameters or {}
    
    def analyze(self, data):
        """Analyze market data and return trading signal"""
        raise NotImplementedError("Subclasses must implement analyze method")


class TrendFollowingStrategy(TradingStrategy):
    """Simple trend following strategy using moving average crossover"""
    def __init__(self, parameters=None):
        super().__init__(parameters)
        self.short_period = self.parameters.get("short_period", 5)
        self.long_period = self.parameters.get("long_period", 10)
    
    def analyze(self, data):
        """Analyze using moving average crossover"""
        if len(data) < self.long_period:
            logger.warning(f"Not enough data for analysis. Need at least {self.long_period} candles.")
            return None
        
        # Calculate moving averages
        data['sma_short'] = data['close'].rolling(window=self.short_period).mean()
        data['sma_long'] = data['close'].rolling(window=self.long_period).mean()
        
        # Get the last complete row of data
        last_row = data.iloc[-1]
        
        # Check for NaN values
        if pd.isna(last_row['sma_short']) or pd.isna(last_row['sma_long']):
            logger.warning("Moving averages contain NaN values. Not enough data.")
            return None
        
        # Determine trade direction based on moving average crossover
        if last_row['sma_short'] > last_row['sma_long']:
            return "call"  # Bullish signal
        else:
            return "put"  # Bearish signal


class RSIStrategy(TradingStrategy):
    """Strategy based on Relative Strength Index (RSI)"""
    def __init__(self, parameters=None):
        super().__init__(parameters)
        self.rsi_period = self.parameters.get("rsi_period", 14)
        self.overbought = self.parameters.get("rsi_overbought", 70)
        self.oversold = self.parameters.get("rsi_oversold", 30)
    
    def calculate_rsi(self, data):
        """Calculate RSI indicator"""
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def analyze(self, data):
        """Analyze using RSI indicator"""
        if len(data) < self.rsi_period + 1:
            logger.warning(f"Not enough data for RSI analysis. Need at least {self.rsi_period + 1} candles.")
            return None
        
        # Calculate RSI
        data['rsi'] = self.calculate_rsi(data)
        
        # Get the last complete row of data
        last_row = data.iloc[-1]
        
        # Check for NaN values
        if pd.isna(last_row['rsi']):
            logger.warning("RSI contains NaN values. Not enough data.")
            return None
        
        # Determine trade direction based on RSI
        if last_row['rsi'] <= self.oversold:
            return "call"  # Oversold condition, expect price to rise
        elif last_row['rsi'] >= self.overbought:
            return "put"  # Overbought condition, expect price to fall
        else:
            return None  # No clear signal


class RandomStrategy(TradingStrategy):
    """Random strategy for testing purposes"""
    def __init__(self, parameters=None):
        super().__init__(parameters)
        self.win_probability = self.parameters.get("win_probability", 0.5)
    
    def analyze(self, data):
        """Generate random trading signal"""
        # Randomly choose direction with specified probability
        if random.random() < self.win_probability:
            return "call"
        else:
            return "put"


def get_strategy(strategy_type, parameters=None):
    """Factory function to create strategy instances"""
    strategies = {
        "trend_following": TrendFollowingStrategy,
        "rsi": RSIStrategy,
        "random": RandomStrategy
    }
    
    if strategy_type not in strategies:
        logger.warning(f"Unknown strategy type: {strategy_type}. Using trend_following instead.")
        strategy_type = "trend_following"
    
    return strategies[strategy_type](parameters)
