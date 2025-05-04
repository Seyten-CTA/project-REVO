# Pocket Option Trading Bot

A simple trading bot for automating trades on the Pocket Option platform.

## Disclaimer

This bot is provided for educational purposes only. Trading binary options involves significant risk and can result in the loss of your invested capital. Use this bot at your own risk. The authors are not responsible for any financial losses incurred from using this software.

## Features

- Automated trading on Pocket Option platform
- Multiple trading strategies (trend following, RSI, random)
- Risk management with Martingale option
- Configurable trade parameters
- Session statistics and logging

## Requirements

- Python 3.7+
- Chrome browser
- Pocket Option account

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/pocket-option-bot.git
cd pocket-option-bot
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure your credentials:
Edit the `.env` file and add your Pocket Option login credentials:
```
POCKET_OPTION_EMAIL=your_email@example.com
POCKET_OPTION_PASSWORD=your_password
```

## Usage

### Basic Usage

Run the bot with default settings:
```
python main.py
```

### Interactive Configuration

Configure the bot before starting:
```
python main.py --configure
```

### Command Line Options

The bot supports various command line options:

- `--configure`: Run interactive configuration before starting
- `--duration MINUTES`: Set trading session duration in minutes
- `--interval MINUTES`: Set interval between trades in minutes
- `--asset ASSET`: Set the asset to trade (e.g., EUR/USD)
- `--amount DOLLARS`: Set trade amount in dollars
- `--strategy STRATEGY`: Set trading strategy (trend_following, rsi, random)
- `--martingale`: Enable Martingale strategy
- `--no-martingale`: Disable Martingale strategy

Example:
```
python main.py --asset EUR/USD --amount 1 --strategy rsi --duration 60 --interval 5 --martingale
```

## Trading Strategies

### Trend Following

Uses moving average crossover to determine trade direction. When the short-term moving average crosses above the long-term moving average, it generates a "call" signal. When it crosses below, it generates a "put" signal.

### RSI (Relative Strength Index)

Uses the RSI indicator to identify overbought and oversold conditions. When RSI falls below the oversold threshold, it generates a "call" signal. When it rises above the overbought threshold, it generates a "put" signal.

### Random

Generates random trading signals for testing purposes.

## Risk Management

The bot includes several risk management features:

- **Maximum Daily Loss**: Stop trading when a specified loss limit is reached
- **Maximum Daily Trades**: Limit the number of trades per day
- **Martingale Strategy**: Increase trade amount after losses to recover previous losses

## Customization

You can customize the bot by editing the `config.json` file or using the interactive configuration.

## Limitations

- The bot uses browser automation with Selenium, which may break if Pocket Option changes their website structure
- The current implementation simulates market data retrieval and trade result checking
- No real-time data feed integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# Pocket-Option-trading-bot-beta--v.0-
# Pocket-Option-trading-bot-beta--v.0-
# Pocket-Option-trading-bot-beta--v.0-
# PO-project-scarlet
# PO-project-scarlet
