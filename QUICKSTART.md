# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Edit Configuration
```bash
nano config.json
```

**For Demo Trading (Recommended First):**
```json
{
    "demo_mode": true,
    "demo_initial_balance": 10000.0,
    "timeframe": "5",
    "scan_interval_seconds": 60,
    "wallet_percent_per_position": 80,
    "max_open_positions": 3,
    "leverage_percent": 30,
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0
}
```

**For Live Trading:**
1. Get Bybit API keys from https://www.bybit.com/app/user/api-management
2. Set permissions: Read & Write for "Contract"
3. Update config:
```json
{
    "api_key": "YOUR_ACTUAL_API_KEY",
    "api_secret": "YOUR_ACTUAL_API_SECRET",
    "demo_mode": false
}
```

### Step 2: Run the Bot
```bash
python3 fvg_bot.py
```

### Step 3: Monitor
- Watch the terminal for signals and position updates
- Press `Ctrl+C` to stop gracefully

---

## 📊 Understanding the Config

### Timeframe Options
- `"1"` - 1 minute
- `"5"` - 5 minutes (recommended)
- `"15"` - 15 minutes
- `"60"` - 1 hour
- `"240"` - 4 hours
- `"D"` - Daily

### Leverage Example
If you set `leverage_percent: 30`:
- BTCUSDT (max 100x) → Bot uses 30x
- ETHUSDT (max 50x) → Bot uses 15x  
- SOLUSDT (max 25x) → Bot uses 7x

### Wallet Usage Example
If you have $10,000 and set `wallet_percent_per_position: 80`:
- Each position will use $8,000
- With 30x leverage, position size = $240,000
- With `max_open_positions: 3`, you can have 3 concurrent positions

### TP/SL with Leverage
`take_profit_percent: 2.0` means 2% ROI:
- With 10x leverage: Price moves 0.2% to hit TP
- With 20x leverage: Price moves 0.1% to hit TP
- With 50x leverage: Price moves 0.04% to hit TP

---

## 🎯 Recommended Settings

### Conservative (Lower Risk)
```json
{
    "leverage_percent": 10,
    "take_profit_percent": 1.5,
    "stop_loss_percent": 1.0,
    "wallet_percent_per_position": 50,
    "max_open_positions": 2
}
```

### Moderate (Balanced)
```json
{
    "leverage_percent": 30,
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0,
    "wallet_percent_per_position": 80,
    "max_open_positions": 3
}
```

### Aggressive (Higher Risk)
```json
{
    "leverage_percent": 50,
    "take_profit_percent": 3.0,
    "stop_loss_percent": 1.5,
    "wallet_percent_per_position": 90,
    "max_open_positions": 5
}
```

---

## 🔧 Troubleshooting

### Bot won't start
- Check Python version: `python3 --version` (needs 3.6+)
- Verify config.json is valid JSON

### No signals found
- Lower `min_volume_usdt` in config
- Try different timeframe (5m or 15m recommended)
- Check `fvg_threshold_percent` (try 0.0)

### API errors in live mode
- Verify API keys are correct
- Check API permissions include "Contract" trading
- Ensure IP whitelist includes your IP (if set)

### Position not opening
- Check wallet balance is sufficient
- Verify symbol has enough volume
- Check max_open_positions not reached

---

## 📱 Running on Termux (Android)

```bash
# Install Python
pkg install python

# Navigate to bot directory
cd /storage/emulated/0/Download/fvg_bot

# Run bot
python fvg_bot.py
```

**Keep screen on:** Settings → Display → Screen timeout → Never

---

## 🛑 Stopping the Bot

**Always use Ctrl+C** to stop the bot gracefully. This will:
1. Stop scanning for new signals
2. Close all open positions
3. Save final state
4. Exit cleanly

**Never kill the process** or you may leave positions open!

---

## 💡 Tips

1. **Start with Demo Mode** - Practice with $10,000 demo balance first
2. **Test Different Timeframes** - 5m and 15m work well for FVG strategy
3. **Monitor First Hour** - Watch bot behavior before leaving it unattended
4. **Use Trailing Stops** - Set at least 0.5% for both trailing_stop and trailing_tp
5. **Filter by Volume** - Keep min_volume_usdt at least 1,000,000
6. **Conservative Leverage** - Start with 10-20% leverage, increase gradually
7. **Risk Management** - Never use more than 80% of wallet per position

---

## 📈 Monitoring Performance

The bot logs every action:
- ✓ Position opened
- ✓ Position closed with ROI
- ✓ Trailing stops updated
- ✓ Balance and total value (demo mode)

**Example Log:**
```
[2024-01-15 10:30:53] ✓ DEMO OPENED: BTCUSDT Buy | Entry: 45230.50 | Qty: 0.531 | Leverage: 30x
[2024-01-15 10:45:12] ✓ DEMO CLOSED: BTCUSDT | Entry: 45230.50 | Exit: 45533.20 | ROI: 2.01% | PnL: $160.72
```

---

## 🎓 Learning Resources

- **Bybit Trading Guide**: https://learn.bybit.com
- **Fair Value Gap Strategy**: Research LuxAlgo FVG indicators
- **Risk Management**: Never risk more than 1-2% per trade
- **Leverage Education**: Understand how leverage amplifies both gains and losses

---

**Happy Trading! 🚀**

*Remember: This is educational software. Trade responsibly and only with money you can afford to lose.*
