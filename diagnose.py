#!/usr/bin/env python3
"""
Diagnostic tool for FVG Trading Bot
Helps identify configuration and connectivity issues
"""

import json
import sys

print("=" * 70)
print("FVG Trading Bot - Diagnostic Tool")
print("=" * 70)
print()

# Test 1: Check config file
print("📋 Test 1: Checking configuration file...")
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    print("  ✓ config.json found and valid JSON")
    
    # Check required fields
    required = ['api_key', 'api_secret', 'demo_mode', 'timeframe']
    missing = [k for k in required if k not in config]
    
    if missing:
        print(f"  ✗ Missing fields: {missing}")
    else:
        print("  ✓ All required fields present")
    
    # Check demo mode
    if config.get('demo_mode', True):
        print("  ✓ Demo mode: ENABLED (safe)")
    else:
        print("  ⚠ Demo mode: DISABLED (live trading!)")
    
    # Check API keys
    if config.get('api_key') == 'YOUR_API_KEY_HERE':
        print("  ⚠ API key not configured (OK for demo mode)")
    else:
        print(f"  ✓ API key configured (length: {len(config.get('api_key', ''))})")
    
except FileNotFoundError:
    print("  ✗ config.json not found!")
    print("    Run: cp config.example.json config.json")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"  ✗ Invalid JSON: {e}")
    sys.exit(1)

print()

# Test 2: Check Python version
print("🐍 Test 2: Checking Python version...")
version = sys.version_info
print(f"  Python {version.major}.{version.minor}.{version.micro}")
if version.major >= 3 and version.minor >= 6:
    print("  ✓ Python version OK")
else:
    print("  ✗ Python 3.6+ required")

print()

# Test 3: Import bot modules
print("📦 Test 3: Checking bot imports...")
try:
    from fvg_bot import BybitAPI, FVGDetector, Position, DemoMode
    print("  ✓ All bot modules imported successfully")
except ImportError as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

print()

# Test 4: Test demo mode
print("💰 Test 4: Testing demo mode...")
try:
    demo = DemoMode(initial_balance=10000.0)
    balance = demo.get_balance()
    print(f"  ✓ Demo mode working (balance: ${balance:.2f})")
except Exception as e:
    print(f"  ✗ Demo mode failed: {e}")

print()

# Test 5: Test FVG detection
print("📊 Test 5: Testing FVG detection...")
try:
    detector = FVGDetector(threshold_percent=0.0, auto_threshold=False)
    
    # Sample bullish FVG data
    test_klines = [
        ['4000', '108', '110', '108', '109', '1000', '100000'],
        ['3000', '105', '108', '104', '107', '1000', '100000'],
        ['2000', '104', '106', '103', '105', '1000', '100000'],
        ['1000', '100', '105', '99', '104', '1000', '100000']
    ]
    
    signal, data = detector.detect_fvg(test_klines)
    if signal == 'BULL':
        print("  ✓ FVG detection working")
    else:
        print("  ⚠ FVG detection returned unexpected result")
except Exception as e:
    print(f"  ✗ FVG detection failed: {e}")

print()

# Test 6: Test API connection (if not demo mode)
if not config.get('demo_mode', True):
    print("🌐 Test 6: Testing Bybit API connection...")
    try:
        api = BybitAPI(
            api_key=config.get('api_key', ''),
            api_secret=config.get('api_secret', ''),
            testnet=config.get('testnet', False)
        )
        
        # Test public endpoint (doesn't need auth)
        tickers = api.get_tickers()
        if tickers:
            print(f"  ✓ Public API working ({len(tickers)} pairs)")
        else:
            print("  ✗ Could not fetch tickers")
        
        # Test private endpoint (needs auth)
        if config.get('api_key') != 'YOUR_API_KEY_HERE':
            balance = api.get_wallet_balance()
            if balance >= 0:
                print(f"  ✓ Authenticated API working (balance: ${balance:.2f})")
            else:
                print("  ✗ Could not fetch wallet balance")
                print("    Check your API keys and permissions")
        else:
            print("  ⚠ Skipping auth test (no API keys configured)")
            
    except Exception as e:
        print(f"  ✗ API connection failed: {e}")
        print("    Check your internet connection and API credentials")
else:
    print("🌐 Test 6: Skipping API test (demo mode enabled)")

print()

# Summary
print("=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

if config.get('demo_mode', True):
    print("✓ Bot is ready to run in DEMO mode")
    print()
    print("Next steps:")
    print("  1. Run: python3 fvg_bot.py")
    print("  2. Watch for signals and positions")
    print("  3. Press Ctrl+C to stop")
else:
    if config.get('api_key') == 'YOUR_API_KEY_HERE':
        print("✗ Cannot run in LIVE mode without API keys")
        print()
        print("Next steps:")
        print("  1. Set demo_mode to true in config.json")
        print("  2. OR add your Bybit API keys")
    else:
        print("⚠ Bot is configured for LIVE trading")
        print()
        print("Next steps:")
        print("  1. Make sure you have tested in demo mode first!")
        print("  2. Start with small position sizes")
        print("  3. Run: python3 fvg_bot.py")
        print("  4. Monitor closely")

print()
print("=" * 70)
print()

print("For more help, see:")
print("  - README.md - Complete documentation")
print("  - QUICKSTART.md - Quick setup guide")
print("  - TROUBLESHOOTING.md - Common issues")
print()
