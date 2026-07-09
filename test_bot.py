#!/usr/bin/env python3
"""
Test script for FVG Trading Bot
Verifies all components work correctly
"""

import json
import sys

def test_imports():
    """Test that all standard library imports work"""
    print("Testing imports...")
    try:
        import json
        import time
        import hmac
        import hashlib
        import urllib.request
        import urllib.parse
        import urllib.error
        from datetime import datetime
        from typing import List, Dict, Optional, Tuple
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test config file loading"""
    print("\nTesting config file...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = [
            'timeframe', 'scan_interval_seconds', 'wallet_percent_per_position',
            'max_open_positions', 'leverage_percent', 'take_profit_percent',
            'stop_loss_percent', 'demo_mode'
        ]
        
        missing = [key for key in required_keys if key not in config]
        if missing:
            print(f"✗ Missing config keys: {missing}")
            return False
        
        print("✓ Config file valid")
        print(f"  - Mode: {'DEMO' if config.get('demo_mode') else 'LIVE'}")
        print(f"  - Timeframe: {config.get('timeframe')}")
        print(f"  - Max Positions: {config.get('max_open_positions')}")
        print(f"  - Leverage: {config.get('leverage_percent')}%")
        return True
    except FileNotFoundError:
        print("✗ config.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return False

def test_fvg_detection():
    """Test FVG detection algorithm"""
    print("\nTesting FVG detection...")
    
    # Import the bot module
    sys.path.insert(0, '.')
    try:
        from fvg_bot import FVGDetector
    except ImportError as e:
        print(f"✗ Failed to import FVGDetector: {e}")
        return False
    
    detector = FVGDetector(threshold_percent=0.0)
    
    # Test bullish FVG pattern
    # Bybit returns newest first, so order: current, [1], [2], [3]...
    # Format: [startTime, openPrice, highPrice, lowPrice, closePrice, volume, turnover]
    # For bullish: low (current) > high[2] AND close[1] > high[2]
    bullish_klines = [
        ['4000', '108', '110', '108', '109', '1000', '100000'],  # current (low=108)
        ['3000', '105', '108', '104', '107', '1000', '100000'],  # [1] (close=107)
        ['2000', '104', '106', '103', '105', '1000', '100000'],  # [2] (high=106)
        ['1000', '100', '105', '99', '104', '1000', '100000']    # [3]
    ]
    
    signal, fvg_data = detector.detect_fvg(bullish_klines)
    if signal == 'BULL':
        print("✓ Bullish FVG detected correctly")
        print(f"  Gap: {fvg_data['min']:.2f} to {fvg_data['max']:.2f}")
    else:
        print(f"✗ Expected BULL signal, got {signal}")
        # Debug info
        print(f"  Debug: klines reversed and processed")
        return False
    
    # Test bearish FVG pattern  
    # For bearish: high (current) < low[2] AND close[1] < low[2]
    bearish_klines = [
        ['4000', '100', '102', '99', '101', '1000', '100000'],   # current (high=102)
        ['3000', '102', '104', '101', '102', '1000', '100000'],  # [1] (close=102)
        ['2000', '104', '106', '103', '105', '1000', '100000'],  # [2] (low=103)
        ['1000', '100', '105', '99', '104', '1000', '100000']    # [3]
    ]
    
    signal, fvg_data = detector.detect_fvg(bearish_klines)
    if signal == 'BEAR':
        print("✓ Bearish FVG detected correctly")
        print(f"  Gap: {fvg_data['min']:.2f} to {fvg_data['max']:.2f}")
    else:
        print(f"✗ Expected BEAR signal, got {signal}")
        return False
    
    return True

def test_position_calculations():
    """Test position and ROI calculations"""
    print("\nTesting position calculations...")
    
    sys.path.insert(0, '.')
    try:
        from fvg_bot import Position
    except ImportError as e:
        print(f"✗ Failed to import Position: {e}")
        return False
    
    # Test long position ROI
    long_pos = Position(
        symbol="BTCUSDT",
        side="Buy",
        entry_price=50000.0,
        quantity=0.1,
        leverage=10,
        stop_loss_price=49500.0,
        take_profit_price=50500.0,
        trailing_stop_percent=0.5,
        trailing_tp_percent=0.5
    )
    
    # Test ROI at 1% price increase with 10x leverage = 10% ROI
    current_price = 50500.0  # 1% increase
    roi = long_pos.get_roi_percent(current_price)
    expected_roi = 10.0  # 1% * 10x leverage
    
    if abs(roi - expected_roi) < 0.01:
        print(f"✓ Long position ROI calculation correct: {roi:.2f}%")
    else:
        print(f"✗ Long position ROI incorrect: {roi:.2f}% (expected {expected_roi:.2f}%)")
        return False
    
    # Test short position ROI
    short_pos = Position(
        symbol="BTCUSDT",
        side="Sell",
        entry_price=50000.0,
        quantity=0.1,
        leverage=20,
        stop_loss_price=50500.0,
        take_profit_price=49500.0,
        trailing_stop_percent=0.5,
        trailing_tp_percent=0.5
    )
    
    # Test ROI at 1% price decrease with 20x leverage = 20% ROI
    current_price = 49500.0  # 1% decrease
    roi = short_pos.get_roi_percent(current_price)
    expected_roi = 20.0  # 1% * 20x leverage
    
    if abs(roi - expected_roi) < 0.01:
        print(f"✓ Short position ROI calculation correct: {roi:.2f}%")
    else:
        print(f"✗ Short position ROI incorrect: {roi:.2f}% (expected {expected_roi:.2f}%)")
        return False
    
    return True

def test_demo_mode():
    """Test demo mode functionality"""
    print("\nTesting demo mode...")
    
    sys.path.insert(0, '.')
    try:
        from fvg_bot import DemoMode, Position
    except ImportError as e:
        print(f"✗ Failed to import DemoMode: {e}")
        return False
    
    demo = DemoMode(initial_balance=10000.0)
    
    # Test opening position
    position = Position(
        symbol="BTCUSDT",
        side="Buy",
        entry_price=50000.0,
        quantity=0.2,
        leverage=10,
        stop_loss_price=49500.0,
        take_profit_price=50500.0,
        trailing_stop_percent=0.5,
        trailing_tp_percent=0.5
    )
    
    success = demo.open_position(position)
    if success:
        print("✓ Demo position opened successfully")
    else:
        print("✗ Failed to open demo position")
        return False
    
    # Test closing with profit
    pnl = demo.close_position("BTCUSDT", 50500.0)
    if pnl is not None and pnl > 0:
        print(f"✓ Demo position closed with profit: ${pnl:.2f}")
    else:
        print(f"✗ Demo position PnL incorrect: {pnl}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("FVG Trading Bot - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Standard Library Imports", test_imports),
        ("Configuration File", test_config),
        ("FVG Detection Algorithm", test_fvg_detection),
        ("Position Calculations", test_position_calculations),
        ("Demo Mode", test_demo_mode)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All tests passed! Bot is ready to use.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
