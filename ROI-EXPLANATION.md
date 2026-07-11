# ROI-Based Take Profit & Stop Loss

## ✅ Confirmation: Bot Already Uses Bybit's ROI Method

The bot's TP/SL calculation **already follows Bybit's ROI percentage methodology exactly**.

---

## How It Works

### Config Settings

```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0,
    "leverage_percent": 30
}
```

These percentages are **ROI percentages**, not price movement percentages.

---

## The Math Behind It

### Bybit's ROI Formula

```
ROI% = (Price Change% × Leverage)
```

Therefore:
```
Price Change% = ROI% ÷ Leverage
```

### Bot's Implementation

```python
# From config
tp_percent = 2.0  # 2% ROI target
sl_percent = 1.0  # 1% ROI stop loss
leverage = 30     # 30x leverage

# Calculate actual price movement needed
price_move_tp = tp_percent / leverage  # 2.0 / 30 = 0.0667%
price_move_sl = sl_percent / leverage  # 1.0 / 30 = 0.0333%

# For LONG position at $50,000:
tp_price = 50000 * (1 + 0.0667 / 100) = $50,033.35
sl_price = 50000 * (1 - 0.0333 / 100) = $49,983.35
```

---

## Examples with Different Leverage

### Example 1: 10x Leverage

**Config:**
```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0,
    "leverage_percent": 20
}
```

Assuming BTCUSDT max leverage is 100x:
- Actual leverage: 100 × 20% = **20x**

**Long at $50,000:**
```
Price move for TP: 2.0% ÷ 20 = 0.1%
TP Price: $50,000 × 1.001 = $50,050

Price move for SL: 1.0% ÷ 20 = 0.05%
SL Price: $50,000 × 0.9995 = $49,975

When price hits $50,050: ROI = +2.0%
When price hits $49,975: ROI = -1.0%
```

### Example 2: 50x Leverage

**Config:**
```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0,
    "leverage_percent": 50
}
```

Assuming BTCUSDT max leverage is 100x:
- Actual leverage: 100 × 50% = **50x**

**Long at $50,000:**
```
Price move for TP: 2.0% ÷ 50 = 0.04%
TP Price: $50,000 × 1.0004 = $50,020

Price move for SL: 1.0% ÷ 50 = 0.02%
SL Price: $50,000 × 0.9998 = $49,990

When price hits $50,020: ROI = +2.0%
When price hits $49,990: ROI = -1.0%
```

### Example 3: 5x Leverage

**Config:**
```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0,
    "leverage_percent": 10
}
```

Assuming BTCUSDT max leverage is 100x:
- Actual leverage: 100 × 10% = **10x**

**Long at $50,000:**
```
Price move for TP: 2.0% ÷ 10 = 0.2%
TP Price: $50,000 × 1.002 = $50,100

Price move for SL: 1.0% ÷ 10 = 0.1%
SL Price: $50,000 × 0.999 = $49,950

When price hits $50,100: ROI = +2.0%
When price hits $49,950: ROI = -1.0%
```

---

## Key Insight

**The ROI percentage stays the same regardless of leverage!**

If you set:
- `take_profit_percent: 2.0`
- Any leverage value

You will **always** get **exactly 2% ROI** when TP is hit.

The only thing that changes is:
- **Higher leverage** = **Smaller price movement** needed
- **Lower leverage** = **Larger price movement** needed

---

## Verification in Bot Logs

When a position opens, you'll see:

```
[2024-07-10 12:00:00] ✓ OPENED: BTCUSDT Buy | Entry: 50000.00 | 
                       Leverage: 30x | TP: 50033.33 | SL: 49983.33
```

When it closes:

```
[2024-07-10 12:10:00] ✓ CLOSED: BTCUSDT | Entry: 50000.00 | Exit: 50033.33 | 
                       ROI: 2.00%
```

The ROI will match your `take_profit_percent` setting exactly!

---

## Comparison: ROI vs Price Movement

| Leverage | TP ROI | Price Move for TP | SL ROI | Price Move for SL |
|----------|--------|-------------------|--------|-------------------|
| 5x       | 2%     | 0.4%              | 1%     | 0.2%              |
| 10x      | 2%     | 0.2%              | 1%     | 0.1%              |
| 20x      | 2%     | 0.1%              | 1%     | 0.05%             |
| 30x      | 2%     | 0.067%            | 1%     | 0.033%            |
| 50x      | 2%     | 0.04%             | 1%     | 0.02%             |
| 100x     | 2%     | 0.02%             | 1%     | 0.01%             |

**Notice:** ROI column stays the same, but price movement decreases as leverage increases.

---

## Why This Matters

### Traditional Method (Wrong)
Some bots use price percentage directly:
```
TP at 2% price increase  
SL at 1% price decrease
```

With 10x leverage:
- 2% price move = 20% ROI (unexpected!)
- 1% price move = 10% loss (unexpected!)

### Bot's Method (Correct - Bybit ROI)
This bot uses ROI percentage:
```
TP at 2% ROI
SL at 1% ROI
```

With 10x leverage:
- 0.2% price move = 2% ROI (as expected!)
- 0.1% price move = 1% loss (as expected!)

---

## Real Trading Example

**Your Setup:**
```json
{
    "demo_mode": false,
    "leverage_percent": 30,
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0
}
```

**BTCUSDT Trade:**
- Entry: $50,000
- Leverage: 30x (if BTCUSDT max is 100x)
- Position size: $15,000 with 30x = $450,000 notional

**What Happens:**

Price moves to $50,033.33 (+0.067%):
```
PnL = ($50,033.33 - $50,000) / $50,000 × 100% × 30 = 2.00% ROI
On $15,000 margin = $300 profit
```

Price moves to $49,983.33 (-0.033%):
```
PnL = ($50,000 - $49,983.33) / $50,000 × 100% × 30 = -1.00% ROI
On $15,000 margin = -$150 loss
```

**This matches Bybit exactly!**

---

## Settings Recommendations

### Conservative (Wider stops)
```json
{
    "take_profit_percent": 3.0,
    "stop_loss_percent": 1.5,
    "leverage_percent": 10
}
```
- Gives price more room to move
- Less likely to get stopped out
- Lower risk

### Moderate (Balanced)
```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0,
    "leverage_percent": 20
}
```
- Standard settings
- Good risk/reward (2:1)

### Aggressive (Tight stops)
```json
{
    "take_profit_percent": 1.5,
    "stop_loss_percent": 0.75,
    "leverage_percent": 40
}
```
- Quick profits/losses
- Higher leverage = smaller price moves
- Higher risk

---

## Testing Your Understanding

**Quiz:** With these settings, what's the TP price for a LONG at $1,000?
```json
{
    "take_profit_percent": 3.0,
    "leverage_percent": 30
}
```

**Answer:**
```
Leverage = 30x
Price move needed = 3.0% ÷ 30 = 0.1%
TP Price = $1,000 × 1.001 = $1,001
```

When price hits $1,001:
```
ROI = ($1 / $1,000) × 100% × 30 = 3.0% ✓
```

---

## Code Reference

From `fvg_bot.py`:

```python
# Calculate SL and TP based on ROI
tp_percent = self.config.get("take_profit_percent", 2.0)
sl_percent = self.config.get("stop_loss_percent", 1.0)

# ROI calculation: actual ROI = price_move_percent * leverage
# So price_move_percent = ROI / leverage
price_move_tp = tp_percent / leverage
price_move_sl = sl_percent / leverage

if signal == "BULL":
    side = "Buy"
    tp_price = current_price * (1 + price_move_tp / 100)
    sl_price = current_price * (1 - price_move_sl / 100)
else:
    side = "Sell"
    tp_price = current_price * (1 - price_move_tp / 100)
    sl_price = current_price * (1 + price_move_sl / 100)
```

And ROI calculation:

```python
def get_roi_percent(self, current_price: float) -> float:
    """Calculate ROI percentage"""
    if self.side == "Buy":
        roi = ((current_price - self.entry_price) / self.entry_price) * 100 * self.leverage
    else:
        roi = ((self.entry_price - current_price) / self.entry_price) * 100 * self.leverage
    return roi
```

**This is exactly Bybit's formula!**

---

## Conclusion

✅ The bot **already uses Bybit's ROI percentage method**  
✅ Your config settings are ROI percentages, not price percentages  
✅ The math is correct and matches Bybit exactly  
✅ No changes needed - it's already implemented correctly!

When you set:
```json
{
    "take_profit_percent": 2.0,
    "stop_loss_percent": 1.0
}
```

You get:
- **Exactly 2% ROI** at take profit
- **Exactly 1% ROI** at stop loss

Regardless of leverage or entry price!

---

**The bot is working correctly. Your TP/SL settings already follow Bybit's ROI methodology! ✅**
