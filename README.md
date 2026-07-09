# Fair Value Gap Trading Bot for Bybit Perpetuals

**Version:** 1.0.0  
**License:** CC BY-NC-SA 4.0 (Attribution-NonCommercial-ShareAlike 4.0 International)  
**© beaver and raylaraykapre - 2024**

Based on the LuxAlgo Fair Value Gap Strategy, this bot trades Bybit perpetual contracts using pure Python with no external dependencies.

---

## Features

✅ **Pure Python** - No pip requirements, runs on Termux and Linux distros  
✅ **Demo Mode** - Practice with real Bybit chart data without risking capital  
✅ **Trailing Stops** - Both trailing stop loss and trailing take profit  
✅ **ROI-Based Calculations** - TP/SL calculated using Bybit's ROI methodology  
✅ **Dynamic Leverage** - Leverage calculated as percentage of max pair leverage  
✅ **Smart Scanning** - Scans all Bybit perpetuals with volume filtering  
✅ **Position Management** - Configurable wallet percentage per position  
✅ **Multi-Timeframe** - Trade on any timeframe (1m, 5m, 15m, 1h, etc.)  
✅ **Real-Time Logging** - Always shows current open positions

---

## Installation

### Linux/Ubuntu
```bash
cd /path/to/bot
chmod +x fvg_bot.py
python3 fvg_bot.py
```

### Termux (Android)
```bash
pkg install python git
git clone https://github.com/raylaraykapre/test2.git
cd test2
python3 fvg_bot.py
```

**No pip install required!** The bot uses only Python standard library.

### Verify Setup
```bash
python3 diagnose.py
```

This will check your configuration and ensure everything is working correctly.

---

## Configuration

Edit `config.json` to customize the bot:

### API Settings
```json
{
    "api_key": "YOUR_API_KEY_HERE",
    "api_secret": "YOUR_API_SECRET_HERE",
    "testnet": false
}
```

### Trading Mode
```json
{
    "demo_mode": true,
    "demo_initial_balance": 10000.0
}
```
- `demo_mode: true` - Practice with simulated trades using real charts
- `demo_mode: false` - Trade with real money (requires API keys)

### Timeframe & Scanning
```json
{
    "timeframe": "5",
    "scan_interval_seconds": 60
}
```
- **timeframe**: 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M
- **scan_interval_seconds**: How often to scan for new signals

### Position Management
```json
{
    "wallet_percent_per_position": 80,
    "max_open_positions": 3
}
```
- **wallet_percent_per_position**: Use 80% means each position uses 80% of available balance
- **max_open_positions**: Maximum number of concurrent positions

### Leverage Calculation
```json
{
    "leverage_percent": 30
}
```
**How it works:**
- If max leverage for pair is 100x and config is 30% → Bot uses 30x
- If max leverage for pair is 12x and config is 50% → Bot uses 6x
- Formula: `actual_leverage = max_leverage * (leverage_percent / 100)`

### Take Profit & Stop Loss (ROI-Based)
```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0
}
```
**ROI Calculation:**
- These percentages represent ROI (Return on Investment)
- Actual price movement = ROI / leverage
- Example: 2% TP with 10x leverage = 0.2% price movement
- This matches Bybit's TP/SL calculation methodology

### Trailing Stops
```json
{
    "trailing_stop_percent": 0.5,
    "trailing_tp_percent": 0.5
}
```
- **trailing_stop_percent**: Trail stop loss by 0.5% as price moves favorably
- **trailing_tp_percent**: Trail take profit by 0.5% to capture more profit

### Volume Filtering
```json
{
    "min_volume_usdt": 1000000,
    "excluded_symbols": ["BTCDOMUSDT", "DEFIUSDT"]
}
```
- **min_volume_usdt**: Only scan pairs with 24h volume > $1M
- **excluded_symbols**: Manually exclude specific pairs

### FVG Detection
```json
{
    "fvg_threshold_percent": 0.0,
    "auto_threshold": false
}
```
- **fvg_threshold_percent**: Minimum gap size percentage
- **auto_threshold**: Auto-calculate threshold based on average gap sizes

---

## Usage

### Start the Bot
```bash
python3 fvg_bot.py
```

### With Custom Config
```bash
python3 fvg_bot.py my_config.json
```

### Stop the Bot
Press `Ctrl+C` to gracefully shut down and close all positions.

---

## Strategy Explanation

### Fair Value Gap (FVG)

**Bullish FVG:**
- Current candle's LOW > 2 candles ago HIGH
- Previous candle's CLOSE > 2 candles ago HIGH
- Gap size exceeds threshold

**Bearish FVG:**
- Current candle's HIGH < 2 candles ago LOW
- Previous candle's CLOSE < 2 candles ago LOW
- Gap size exceeds threshold

### Trading Logic

1. **Scan Phase**: Bot scans all perpetuals on configured timeframe
2. **Signal Detection**: Identifies bullish/bearish FVG patterns
3. **Position Opening**: Opens position with calculated TP/SL
4. **Trailing Management**: Updates trailing stops as price moves favorably
5. **Position Closing**: Closes when TP/SL hit or on manual shutdown

---

## Example Output

```
================================================================================
Fair Value Gap Trading Bot v1.0.0
Based on LuxAlgo Fair Value Gap Strategy
© beaver and raylaraykapre - 2024
Licensed under CC BY-NC-SA 4.0
================================================================================
Mode: DEMO
Timeframe: 5
Scan Interval: 60s
Max Open Positions: 3
Wallet Usage per Position: 80%
================================================================================

[2024-01-15 10:30:45] Bot started!
[2024-01-15 10:30:46] Scanning for tradable perpetuals...
[2024-01-15 10:30:48] Found 245 tradable symbols
[2024-01-15 10:30:49] Scanning 245 symbols for FVG signals...
[2024-01-15 10:30:52] Signal found: BTCUSDT - BULL
[2024-01-15 10:30:53] ✓ DEMO OPENED: BTCUSDT Buy | Entry: 45230.50 | Qty: 0.531 | Leverage: 30x | SL: 45079.24 | TP: 45533.21

================================================================================
OPEN POSITIONS:
================================================================================
BTCUSDT Buy | Entry: 45230.50 | Qty: 0.531 | Leverage: 30x | SL: 45079.24 | TP: 45533.21 | Current: 45280.30 | ROI: 0.33%

Demo Balance: $2000.00 | Total Value: $10079.70
================================================================================

[2024-01-15 10:31:53] Sleeping for 60 seconds...
```

---

## License

This work is licensed under **Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

https://creativecommons.org/licenses/by-nc-sa/4.0/

**You are free to:**
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

**Under the following terms:**
- Attribution — You must give appropriate credit to beaver and raylaraykapre
- NonCommercial — You may not use this for commercial purposes
- ShareAlike — If you remix or adapt, you must distribute under the same license

**© beaver and raylaraykapre - 2024**  
Original strategy concept by LuxAlgo

---

## Disclaimer

**TRADING CRYPTOCURRENCIES INVOLVES SUBSTANTIAL RISK OF LOSS.**

- This bot is provided for educational purposes only
- Past performance does not guarantee future results
- Always test in demo mode before live trading
- Never invest more than you can afford to lose
- The authors are not responsible for any financial losses

**USE AT YOUR OWN RISK**

---

## Support

For issues, questions, or contributions, please contact the bot owners:
- beaver
- raylaraykapre

---

## Changelog

### v1.0.1 (2024-07-10)
- **FIXED:** Bybit API v5 authentication (positions now open correctly)
- **IMPROVED:** Error handling with detailed error messages
- **ADDED:** Diagnostic tool (`diagnose.py`) to test setup
- **ADDED:** Comprehensive troubleshooting guide
- **ENHANCED:** Quantity validation and formatting
- **ENHANCED:** Better balance checking

### v1.0.0 (2024)
- Initial release
- FVG strategy implementation
- Demo mode with live charts
- Trailing TP/SL
- ROI-based calculations
- Dynamic leverage
- Volume filtering
- Pure Python (no dependencies)
