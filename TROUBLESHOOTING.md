# Troubleshooting Guide

## Common Issues and Solutions

### ❌ "Failed to open position for [SYMBOL]"

**Symptoms:**
```
[2024-07-10 06:26:30] Signal found: AEROUSDT - BULL
[2024-07-10 06:26:31] ✗ Failed to open position for AEROUSDT
```

**Possible Causes & Solutions:**

#### 1. **API Authentication Issues** ✅ FIXED IN v1.0.1
- **Problem:** Old authentication method for Bybit API v2
- **Solution:** Updated to use v5 API authentication with X-BAPI headers
- **Action:** Update to latest version: `git pull origin main`

#### 2. **Insufficient Balance**
- **Problem:** Wallet balance too low for position size
- **Check:** Run bot and look for balance info in output
- **Solution:** 
  - Lower `wallet_percent_per_position` in config (try 50% instead of 80%)
  - Lower `leverage_percent` (try 10% instead of 30%)
  - Deposit more USDT to your account

#### 3. **API Keys Invalid or Missing Permissions**
- **Problem:** API key doesn't have required permissions
- **Solution:**
  1. Go to Bybit → API Management
  2. Create new API key with permissions:
     - ✅ Read
     - ✅ Contract - Write (for trading)
     - ✅ Position (for managing positions)
  3. Update `config.json` with new keys
  4. If using IP whitelist, add your IP address

#### 4. **Minimum Order Size**
- **Problem:** Calculated quantity below symbol's minimum
- **Check:** Look for `"Quantity X below minimum Y for SYMBOL"`
- **Solution:**
  - Increase `wallet_percent_per_position` (e.g., 90%)
  - Increase `demo_initial_balance` if using demo mode
  - Choose symbols with lower minimum order sizes

#### 5. **Demo Mode Not Enabled**
- **Problem:** Trying to trade live without proper setup
- **Solution:** Set `"demo_mode": true` in config.json to test safely first

---

## Testing Your Setup

### Step 1: Verify API Connection
```bash
cd /path/to/bot
python3 << 'EOF'
from fvg_bot import BybitAPI
import json

# Load your config
with open('config.json') as f:
    config = json.load(f)

# Test API
api = BybitAPI(
    api_key=config['api_key'],
    api_secret=config['api_secret'],
    testnet=config.get('testnet', False)
)

# Try to get balance
balance = api.get_wallet_balance()
if balance > 0:
    print(f"✓ API Working! Balance: ${balance:.2f}")
else:
    print("✗ API Failed or Zero Balance")
    
# Try to get tickers
tickers = api.get_tickers()
print(f"✓ Found {len(tickers)} perpetual pairs")
EOF
```

### Step 2: Run Tests
```bash
python3 test_bot.py
```
Should show: `Results: 5/5 tests passed`

### Step 3: Test Demo Mode
```bash
# Make sure demo_mode is true
nano config.json

# Run bot
python3 fvg_bot.py
```

---

## Error Messages Explained

### API Errors

#### "Order failed: ab not enough for new order"
- **Cause:** Insufficient balance in your account
- **Fix:** 
  1. Check balance: The bot now shows it on startup
  2. Deposit more USDT to your Bybit account
  3. Or reduce position size:
     - Lower `wallet_percent_per_position` (try 30-50%)
     - Lower `leverage_percent` (try 10%)
     - Reduce `max_open_positions` to 1
  4. Use `config.low-balance.json` as template:
     ```bash
     cp config.low-balance.json config.json
     nano config.json  # Add your API keys
     ```

#### "Could not set leverage for [SYMBOL]"
- **Cause:** API leverage setting failed (v1.0.2 handles this better)
- **Fix:** 
  - Update to v1.0.2+: `git pull origin main`
  - Bot will now show the actual error and continue with default leverage
  - If you see "agreement" in error, you need to accept trading terms on Bybit

#### "You must sign the required agreement before trading this contract"
- **Cause:** Some trading pairs require accepting Bybit's derivative terms
- **Fix:**
  1. Log in to Bybit website
  2. Go to Derivatives/Perpetual trading
  3. Try to manually trade the symbol that failed
  4. Accept the terms when prompted
  5. Run bot again - it will skip symbols you haven't accepted

#### "HTTP Error: 401"
- **Cause:** Invalid API key or secret
- **Fix:** Double-check your API credentials in config.json

#### "HTTP Error: 403"
- **Cause:** IP not whitelisted or insufficient permissions
- **Fix:** Add your IP to whitelist or check API permissions

#### "HTTP Error: 10001"
- **Cause:** Parameter error (usually qty or price format)
- **Fix:** Bot now handles this automatically in v1.0.1+

#### "retCode: 110001"
- **Cause:** Order quantity too small
- **Fix:** Increase wallet percentage or trade higher-priced coins

#### "retCode: 110003"
- **Cause:** Insufficient balance
- **Fix:** Deposit more USDT or reduce position size

#### "retCode: 110004"
- **Cause:** Leverage not set or invalid
- **Fix:** Bot sets leverage automatically now

---

## Debugging Tips

### Enable Verbose Output
The bot now shows API errors in real-time. Watch for:
```
API Error: {...}
Order failed: [error message]
```

### Check Your Config
```bash
cat config.json
```

Verify:
- ✅ `api_key` and `api_secret` are filled in
- ✅ `demo_mode` is `true` for testing
- ✅ `timeframe` is a valid value (1, 3, 5, 15, 30, 60, etc.)
- ✅ `leverage_percent` is reasonable (10-50%)
- ✅ `wallet_percent_per_position` is not too high (50-90%)

### Test Single Symbol Manually
```bash
python3 << 'EOF'
from fvg_bot import BybitAPI, FVGDetector

api = BybitAPI("YOUR_KEY", "YOUR_SECRET", False)

# Test getting klines
symbol = "BTCUSDT"
klines = api.get_kline_data(symbol, "5", 200)
print(f"Got {len(klines)} candles for {symbol}")

# Test FVG detection
detector = FVGDetector(0.0, False)
signal, data = detector.detect_fvg(klines)
print(f"Signal: {signal}")
EOF
```

---

## Configuration Recommendations

### For Testing (Safe)
```json
{
    "demo_mode": true,
    "demo_initial_balance": 10000,
    "timeframe": "5",
    "leverage_percent": 10,
    "wallet_percent_per_position": 50,
    "max_open_positions": 2
}
```

### For Live Trading (Start Small)
```json
{
    "demo_mode": false,
    "timeframe": "15",
    "leverage_percent": 20,
    "wallet_percent_per_position": 30,
    "max_open_positions": 1,
    "take_profit_percent": 1.5,
    "stop_loss_percent": 1.0
}
```

### For Aggressive Trading
```json
{
    "demo_mode": false,
    "timeframe": "5",
    "leverage_percent": 30,
    "wallet_percent_per_position": 80,
    "max_open_positions": 3,
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0
}
```

---

## Network Issues

### "Request Error: [Errno -3] Temporary failure in name resolution"
- **Cause:** No internet connection
- **Fix:** Check your internet connection

### "Request Error: timed out"
- **Cause:** Slow connection or Bybit API down
- **Fix:** 
  - Check https://status.bybit.com
  - Increase timeout in code (advanced)
  - Try again later

### "SSL: CERTIFICATE_VERIFY_FAILED"
- **Cause:** System certificates out of date
- **Fix on Termux:**
  ```bash
  pkg update
  pkg install ca-certificates
  ```
- **Fix on Linux:**
  ```bash
  sudo apt-get update
  sudo apt-get install ca-certificates
  ```

---

## Performance Issues

### Bot Running Slow
- **Reduce scan interval:** Set `scan_interval_seconds` to 120 or higher
- **Reduce symbol count:** Increase `min_volume_usdt` to scan fewer pairs
- **Exclude symbols:** Add low-volume coins to `excluded_symbols`

### Too Many Signals
- **Increase threshold:** Set `fvg_threshold_percent` to 0.1 or 0.2
- **Longer timeframe:** Use "15" or "60" instead of "5"
- **Reduce max positions:** Set `max_open_positions` to 1 or 2

### Not Enough Signals
- **Lower threshold:** Set `fvg_threshold_percent` to 0.0
- **Shorter timeframe:** Try "5" or "3"
- **Enable auto threshold:** Set `auto_threshold` to true

---

## Getting Help

### Before Asking for Help

1. ✅ Update to latest version: `git pull origin main`
2. ✅ Run tests: `python3 test_bot.py`
3. ✅ Check this troubleshooting guide
4. ✅ Try demo mode first
5. ✅ Copy the full error message

### Information to Provide

When reporting an issue, include:
- Bot version (check git commit)
- Python version: `python3 --version`
- Operating system (Linux/Termux)
- Config file (remove API keys!)
- Full error message
- Steps to reproduce

---

## Known Limitations

1. **No Historical Backtesting** - Bot only trades on live data
2. **Single Strategy** - Only FVG strategy implemented
3. **No Partial Closes** - Positions close entirely on TP/SL
4. **USDT Pairs Only** - Doesn't trade other quote currencies
5. **Linear Contracts Only** - Doesn't support inverse contracts

---

## Version History

### v1.0.1 (2024-07-10)
- ✅ Fixed Bybit API v5 authentication
- ✅ Improved error handling and messages
- ✅ Better quantity formatting
- ✅ Added minimum order validation
- ✅ Split TP/SL from order placement

### v1.0.0 (2024-07-09)
- Initial release
- FVG strategy implementation
- Demo mode
- Trailing stops
- Pure Python (no dependencies)

---

## Still Having Issues?

Contact the bot owners:
- beaver
- raylaraykapre

Or check the repository:
https://github.com/raylaraykapre/test2

---

**Remember:** Always test with demo mode before risking real money!
