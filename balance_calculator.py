#!/usr/bin/env python3
"""
Balance Calculator - Figure out optimal settings for your balance
"""

def calculate_position_size(balance, wallet_percent, leverage_percent, max_pair_leverage=50):
    """Calculate position size and margin needed"""
    # Apply safety buffer (v1.0.3)
    safe_wallet_percent = wallet_percent * 0.9
    position_value = balance * (safe_wallet_percent / 100)
    
    # Calculate leverage
    actual_leverage = int(max_pair_leverage * (leverage_percent / 100))
    
    # Auto-reduce for low balances
    if balance < 20:
        actual_leverage = min(actual_leverage, 5)
    
    # Calculate quantities
    margin_needed = position_value
    position_size = position_value * actual_leverage
    balance_reserve = balance * 0.05  # 5% kept free
    
    return {
        'balance': balance,
        'wallet_percent': wallet_percent,
        'safe_percent': safe_wallet_percent,
        'position_value': position_value,
        'leverage_percent': leverage_percent,
        'actual_leverage': actual_leverage,
        'margin_needed': margin_needed,
        'position_size': position_size,
        'balance_reserve': balance_reserve,
        'usable_balance': balance - balance_reserve
    }

def recommend_settings(balance):
    """Recommend settings based on balance"""
    if balance < 10:
        return {
            'recommendation': 'Use DEMO MODE',
            'wallet_percent': 50,
            'leverage_percent': 20,
            'max_positions': 1,
            'reason': 'Balance too low for safe live trading'
        }
    elif balance < 20:
        return {
            'recommendation': 'VERY CONSERVATIVE',
            'wallet_percent': 30,
            'leverage_percent': 10,
            'max_positions': 1,
            'reason': 'Low balance - minimize risk'
        }
    elif balance < 50:
        return {
            'recommendation': 'CONSERVATIVE',
            'wallet_percent': 40,
            'leverage_percent': 15,
            'max_positions': 1,
            'reason': 'Small balance - focus on one good trade'
        }
    elif balance < 100:
        return {
            'recommendation': 'MODERATE',
            'wallet_percent': 50,
            'leverage_percent': 20,
            'max_positions': 2,
            'reason': 'Medium balance - balanced approach'
        }
    elif balance < 500:
        return {
            'recommendation': 'STANDARD',
            'wallet_percent': 60,
            'leverage_percent': 25,
            'max_positions': 2,
            'reason': 'Good balance - standard settings'
        }
    else:
        return {
            'recommendation': 'AGGRESSIVE',
            'wallet_percent': 70,
            'leverage_percent': 30,
            'max_positions': 3,
            'reason': 'High balance - can take more risk'
        }

def main():
    print("=" * 70)
    print("FVG Trading Bot - Balance Calculator")
    print("=" * 70)
    print()
    
    # Get balance from user
    try:
        balance_input = input("Enter your USDT balance (or press Enter for examples): $")
        if not balance_input:
            # Show examples
            examples = [5, 15, 30, 75, 150, 600]
        else:
            examples = [float(balance_input)]
    except ValueError:
        print("Invalid input, showing examples...")
        examples = [5, 15, 30, 75, 150, 600]
    
    for balance in examples:
        print("\n" + "=" * 70)
        print(f"BALANCE: ${balance:.2f} USDT")
        print("=" * 70)
        
        # Get recommendation
        rec = recommend_settings(balance)
        
        print(f"\n🎯 RECOMMENDATION: {rec['recommendation']}")
        print(f"   Reason: {rec['reason']}")
        print(f"\n📊 Suggested Config:")
        print(f"   wallet_percent_per_position: {rec['wallet_percent']}%")
        print(f"   leverage_percent: {rec['leverage_percent']}%")
        print(f"   max_open_positions: {rec['max_positions']}")
        
        if balance >= 10:
            # Calculate what this means
            calc = calculate_position_size(
                balance, 
                rec['wallet_percent'], 
                rec['leverage_percent']
            )
            
            print(f"\n💰 Position Breakdown:")
            print(f"   Balance: ${calc['balance']:.2f}")
            print(f"   - Reserve (5%): ${calc['balance_reserve']:.2f}")
            print(f"   = Usable: ${calc['usable_balance']:.2f}")
            print(f"   × Wallet {calc['wallet_percent']}%: ${calc['position_value']:.2f}")
            print(f"   × Safety 90%: ${calc['position_value']:.2f}")
            print(f"   = Margin needed: ${calc['margin_needed']:.2f}")
            print(f"   × Leverage {calc['actual_leverage']}x: ${calc['position_size']:.2f} position")
            
            # Success probability
            if calc['margin_needed'] < calc['usable_balance']:
                print(f"\n✅ SHOULD WORK - Margin fits within balance")
            else:
                print(f"\n❌ WON'T WORK - Need ${calc['margin_needed']:.2f}, only have ${calc['usable_balance']:.2f}")
        else:
            print(f"\n⚠️  Balance too low for live trading!")
            print(f"    Minimum recommended: $10 USDT")
            print(f"    Your balance: ${balance:.2f} USDT")
            print(f"    Deposit more or use demo mode")
    
    print("\n" + "=" * 70)
    print("💡 TIPS:")
    print("   - Start conservative and increase gradually")
    print("   - Test in demo mode first")
    print("   - Monitor first few trades closely")
    print("   - Lower settings = safer, higher = more aggressive")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
