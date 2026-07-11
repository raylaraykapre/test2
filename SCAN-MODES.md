# Scan Modes - All Derivatives vs Specific Pairs

## Overview

The bot now supports two scanning modes:
1. **All Derivatives** (default) - Scans all perpetual contracts with volume filtering
2. **Specific Pairs** - Trades only the pairs you specify

---

## Configuration

### Mode 1: All Derivatives (Default)

Scan all available perpetual contracts on Bybit, filtered by volume.

**config.json:**
```json
{
    "scan_mode": "all",
    "specific_pairs": [],
    "min_volume_usdt": 1000000,
    "excluded_symbols": ["BTCDOMUSDT"]
}
```

**What it does:**
- Scans ALL perpetual contracts on Bybit
- Filters out pairs with 24h volume < `min_volume_usdt`
- Excludes pairs in `excluded_symbols` list
- Typically finds 200-300 tradable pairs

**Use when:**
- You want maximum opportunities
- You trust the bot to find signals across all markets
- You want diversification

---

### Mode 2: Specific Pairs Only

Trade only the pairs you explicitly list.

**config.json:**
```json
{
    "scan_mode": "specific",
    "specific_pairs": [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "BNBUSDT",
        "XRPUSDT"
    ],
    "min_volume_usdt": 1000000,
    "excluded_symbols": []
}
```

**What it does:**
- Scans ONLY the pairs you list in `specific_pairs`
- Ignores `min_volume_usdt` (your specified pairs always trade)
- Ignores `excluded_symbols` for specific pairs
- Bot will warn if a pair doesn't exist on Bybit

**Use when:**
- You only want to trade major coins
- You have specific pairs you trust
- You want more control over what's traded
- You want to avoid low-cap altcoins

---

## Examples

### Example 1: Top 10 Coins Only

```json
{
    "scan_mode": "specific",
    "specific_pairs": [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "SOLUSDT",
        "XRPUSDT",
        "ADAUSDT",
        "DOGEUSDT",
        "MATICUSDT",
        "DOTUSDT",
        "AVAXUSDT"
    ]
}
```

### Example 2: Only Bitcoin and Ethereum

```json
{
    "scan_mode": "specific",
    "specific_pairs": [
        "BTCUSDT",
        "ETHUSDT"
    ],
    "max_open_positions": 2
}
```

### Example 3: DeFi Tokens

```json
{
    "scan_mode": "specific",
    "specific_pairs": [
        "UNIUSDT",
        "AAVEUSDT",
        "LINKUSDT",
        "MKRUSDT",
        "COMPUSDT"
    ]
}
```

### Example 4: All Derivatives (High Volume Only)

```json
{
    "scan_mode": "all",
    "min_volume_usdt": 10000000,
    "excluded_symbols": [
        "BTCDOMUSDT",
        "DEFIUSDT"
    ]
}
```

---

## Bot Output

### All Derivatives Mode

```
================================================================================
Fair Value Gap Trading Bot v1.1.0
...
================================================================================
Mode: DEMO
Timeframe: 15
Scan Interval: 60s
Max Open Positions: 3
Wallet Usage per Position: 50%
Leverage: 20% of max
Scan Mode: ALL DERIVATIVES (volume filtered)
================================================================================

[2024-07-10 10:00:00] Bot started!
[2024-07-10 10:00:00] Scanning all perpetuals...
[2024-07-10 10:00:02] Found 247 tradable symbols
[2024-07-10 10:00:03] Scanning 247 symbols for FVG signals...
```

### Specific Pairs Mode

```
================================================================================
Fair Value Gap Trading Bot v1.1.0
...
================================================================================
Mode: DEMO
Timeframe: 15
Scan Interval: 60s
Max Open Positions: 2
Wallet Usage per Position: 50%
Leverage: 20% of max
Scan Mode: SPECIFIC PAIRS ONLY
Trading Pairs: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT
================================================================================

[2024-07-10 10:00:00] Bot started!
[2024-07-10 10:00:00] Trading specific pairs: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT
[2024-07-10 10:00:01] Trading 5 specific pairs
[2024-07-10 10:00:02] Scanning 5 symbols for FVG signals...
```

---

## Advantages & Disadvantages

### All Derivatives Mode

**Advantages:**
- ✅ More trading opportunities
- ✅ Can find signals in lesser-known coins
- ✅ Better for active trading
- ✅ Diversification across many pairs

**Disadvantages:**
- ❌ May trade obscure/volatile coins
- ❌ Slower scanning (more pairs to check)
- ❌ May hit pairs requiring trading agreements
- ❌ Less control over what's traded

### Specific Pairs Mode

**Advantages:**
- ✅ Trade only what you trust
- ✅ Faster scanning (fewer pairs)
- ✅ More predictable behavior
- ✅ Can focus on high-liquidity pairs
- ✅ Easier to monitor manually

**Disadvantages:**
- ❌ Fewer trading opportunities
- ❌ May miss good signals in other pairs
- ❌ Less diversification
- ❌ Need to manually choose pairs

---

## Configuration Files

The bot comes with example configs for both modes:

### config.example.json
Default configuration - scans all derivatives
```bash
cp config.example.json config.json
nano config.json  # Add your API keys
```

### config.specific-pairs.json
Pre-configured for top 5 coins
```bash
cp config.specific-pairs.json config.json
nano config.json  # Add your API keys, adjust pairs
```

### config.low-balance.json
For small accounts - scans all with high volume filter
```bash
cp config.low-balance.json config.json
nano config.json  # Add your API keys
```

---

## Tips & Best Practices

### For Beginners
```json
{
    "scan_mode": "specific",
    "specific_pairs": ["BTCUSDT", "ETHUSDT"],
    "max_open_positions": 1
}
```
Start with 1-2 major pairs you understand.

### For Active Traders
```json
{
    "scan_mode": "all",
    "min_volume_usdt": 5000000,
    "max_open_positions": 3
}
```
Scan everything with decent volume.

### For Conservative Traders
```json
{
    "scan_mode": "specific",
    "specific_pairs": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    "leverage_percent": 10
}
```
Stick to top coins with low leverage.

### For Aggressive Traders
```json
{
    "scan_mode": "all",
    "min_volume_usdt": 1000000,
    "max_open_positions": 5,
    "leverage_percent": 40
}
```
More pairs, more positions, more leverage.

---

## Validation

The bot validates your configuration:

**Invalid pair warning:**
```
[2024-07-10 10:00:00] Trading specific pairs: BTCUSDT, FAKECOIN, ETHUSDT
[2024-07-10 10:00:01] ⚠ Invalid pairs skipped: FAKECOIN
[2024-07-10 10:00:01] Trading 2 specific pairs
```

**No pairs configured:**
```
[2024-07-10 10:00:00] ⚠ Specific pairs mode enabled but no pairs configured!
```

**Empty list:**
```
[2024-07-10 10:00:00] Trading Pairs: None configured!
```

---

## Switching Modes

You can easily switch between modes by editing `config.json`:

**From All → Specific:**
```json
{
    "scan_mode": "specific",  // Changed from "all"
    "specific_pairs": [       // Add your pairs
        "BTCUSDT",
        "ETHUSDT"
    ]
}
```

**From Specific → All:**
```json
{
    "scan_mode": "all",       // Changed from "specific"
    "specific_pairs": []      // Can leave empty or remove
}
```

---

## FAQ

**Q: Can I use both modes at once?**  
A: No, you must choose either "all" or "specific".

**Q: Do I need to restart the bot when changing pairs?**  
A: Yes, always restart after editing config.json.

**Q: What if I list a pair that doesn't exist?**  
A: Bot will warn you and skip that pair, continuing with valid ones.

**Q: Can I use excluded_symbols with specific pairs?**  
A: Yes, but it's redundant - just don't list pairs you want to exclude.

**Q: Does scan_mode affect performance?**  
A: Specific pairs mode is faster as it scans fewer symbols.

**Q: Can I add/remove pairs while bot is running?**  
A: No, you must stop bot, edit config, then restart.

---

## Version

This feature was added in **v1.1.0**

---

**Happy Trading! 🚀**
