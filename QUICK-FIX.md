# Quick Fix Guide - Leverage & Balance Issues

## 🚨 If You're Seeing These Errors:

### "Order failed: ab not enough for new order"
**Problem:** Not enough USDT in your account  
**Solution:**
```bash
# Option 1: Use demo mode (safest)
nano config.json
# Change: "demo_mode": true

# Option 2: Deposit more USDT to Bybit

# Option 3: Use low-balance config
cp config.low-balance.json config.json
nano config.json  # Add your API keys
```

### "Could not set leverage for [SYMBOL]"
**Problem:** Leverage API failing  
**Solution:**
```bash
# Update to v1.0.2
cd ~/test2
git pull origin main
python3 fvg_bot.py
```
Bot will now show the actual error and continue trading.

### "You must sign the required agreement"
**Problem:** Haven't accepted Bybit's trading terms for that pair  
**Solution:**
1. Go to Bybit website
2. Try to manually trade that symbol
3. Accept the terms when prompted
4. Run bot again - it will skip unaccepted symbols automatically

---

## ✅ Quick Update Command

```bash
cd ~/test2  # or wherever you have the bot
git pull origin main
python3 fvg_bot.py
```

---

## 💰 Balance Recommendations

| Your Balance | Config to Use | Settings |
|-------------|---------------|----------|
| < $10 | Demo mode | Test first! |
| $10-$50 | config.low-balance.json | 1 position, 10% leverage |
| $50-$200 | Modify config.json | 2 positions, 20% leverage |
| $200+ | Default config.json | 3 positions, 30% leverage |

---

## 📋 Low Balance Config (Recommended for $10-$100)

```json
{
    "demo_mode": false,
    "timeframe": "15",
    "wallet_percent_per_position": 50,
    "max_open_positions": 1,
    "leverage_percent": 10,
    "take_profit_percent": 1.5,
    "stop_loss_percent": 1.0,
    "min_volume_usdt": 5000000
}
```

Copy and use:
```bash
cp config.low-balance.json config.json
nano config.json  # Add API keys
```

---

## 🔍 Check If Fixed

```bash
# Run diagnostic
python3 diagnose.py

# Run bot - should show balance on startup
python3 fvg_bot.py
```

Look for:
```
Mode: LIVE
Wallet Balance: $XX.XX USDT  ← Should show your balance
```

---

## 📞 Still Having Issues?

1. Make sure you pulled latest: `git pull origin main`
2. Check version shows v1.0.2: Look at startup screen
3. Run: `python3 diagnose.py`
4. Read: `TROUBLESHOOTING.md`

---

**Version Required:** v1.0.2 or higher  
**Last Updated:** 2024-07-10
