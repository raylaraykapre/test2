#!/usr/bin/env python3
"""
Fair Value Gap Trading Bot for Bybit Perpetuals
Based on LuxAlgo Fair Value Gap Strategy

This work is licensed under Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
https://creativecommons.org/licenses/by-nc-sa/4.0/
© beaver and raylaraykapre - 2024
Original strategy concept by LuxAlgo
"""

import json
import time
import hmac
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import List, Dict, Optional, Tuple

VERSION = "1.0.0"

class BybitAPI:
    """Pure Python Bybit API client without external dependencies"""
    
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
        
    def _generate_signature(self, timestamp: str, params_str: str) -> str:
        """Generate HMAC SHA256 signature for Bybit API v5"""
        # V5 signature: timestamp + api_key + recv_window + params_str
        recv_window = "5000"
        sign_str = timestamp + self.api_key + recv_window + params_str
        return hmac.new(
            self.api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Make HTTP request to Bybit API"""
        if params is None:
            params = {}
            
        url = f"{self.base_url}{endpoint}"
        
        # Prepare request
        if method == "GET":
            if params:
                query_string = urllib.parse.urlencode(sorted(params.items()))
                url += "?" + query_string
            req = urllib.request.Request(url, method=method)
            params_str = query_string if params else ""
        else:
            params_str = json.dumps(params) if params else ""
            data = params_str.encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        
        # Add authentication headers for signed requests
        if signed:
            timestamp = str(int(time.time() * 1000))
            signature = self._generate_signature(timestamp, params_str)
            req.add_header('X-BAPI-API-KEY', self.api_key)
            req.add_header('X-BAPI-TIMESTAMP', timestamp)
            req.add_header('X-BAPI-SIGN', signature)
            req.add_header('X-BAPI-RECV-WINDOW', '5000')
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            print(f"API Error: {error_msg}")  # Debug output
            return {"retCode": -1, "retMsg": f"HTTP Error: {error_msg}"}
        except Exception as e:
            print(f"Request Error: {str(e)}")  # Debug output
            return {"retCode": -1, "retMsg": f"Request Error: {str(e)}"}
    
    def get_kline_data(self, symbol: str, interval: str, limit: int = 200) -> List[Dict]:
        """Fetch kline/candlestick data"""
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        result = self._request("GET", "/v5/market/kline", params)
        if result.get("retCode") == 0:
            return result.get("result", {}).get("list", [])
        return []
    
    def get_tickers(self, category: str = "linear") -> List[Dict]:
        """Get all tickers for perpetuals"""
        params = {"category": category}
        result = self._request("GET", "/v5/market/tickers", params)
        if result.get("retCode") == 0:
            return result.get("result", {}).get("list", [])
        return []


    def get_wallet_balance(self, account_type: str = "UNIFIED") -> float:
        """Get wallet balance"""
        params = {"accountType": account_type}
        result = self._request("GET", "/v5/account/wallet-balance", params, signed=True)
        if result.get("retCode") == 0:
            balances = result.get("result", {}).get("list", [])
            if balances:
                coins = balances[0].get("coin", [])
                for coin in coins:
                    if coin.get("coin") == "USDT":
                        return float(coin.get("walletBalance", 0))
        return 0.0
    
    def get_positions(self, category: str = "linear") -> List[Dict]:
        """Get current positions"""
        params = {"category": category}
        result = self._request("GET", "/v5/position/list", params, signed=True)
        if result.get("retCode") == 0:
            return result.get("result", {}).get("list", [])
        return []
    
    def set_leverage(self, symbol: str, buy_leverage: str, sell_leverage: str, category: str = "linear") -> bool:
        """Set leverage for a symbol"""
        params = {
            "category": category,
            "symbol": symbol,
            "buyLeverage": buy_leverage,
            "sellLeverage": sell_leverage
        }
        result = self._request("POST", "/v5/position/set-leverage", params, signed=True)
        return result.get("retCode") == 0
    
    def place_order(self, symbol: str, side: str, order_type: str, qty: str, 
                   price: str = None, stop_loss: str = None, take_profit: str = None,
                   category: str = "linear") -> Optional[str]:
        """Place an order"""
        params = {
            "category": category,
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "timeInForce": "GTC"
        }
        
        if price:
            params["price"] = price
        if stop_loss:
            params["stopLoss"] = stop_loss
        if take_profit:
            params["takeProfit"] = take_profit
            
        result = self._request("POST", "/v5/order/create", params, signed=True)
        
        # Better error handling
        if result.get("retCode") == 0:
            return result.get("result", {}).get("orderId")
        else:
            error_msg = result.get("retMsg", "Unknown error")
            print(f"Order failed: {error_msg}")
            return None


    def set_trading_stop(self, symbol: str, stop_loss: str = None, take_profit: str = None,
                        trailing_stop: str = None, position_idx: int = 0, category: str = "linear") -> bool:
        """Set trading stop (SL/TP/Trailing)"""
        params = {
            "category": category,
            "symbol": symbol,
            "positionIdx": position_idx
        }
        
        if stop_loss:
            params["stopLoss"] = stop_loss
        if take_profit:
            params["takeProfit"] = take_profit
        if trailing_stop:
            params["trailingStop"] = trailing_stop
            
        result = self._request("POST", "/v5/position/trading-stop", params, signed=True)
        return result.get("retCode") == 0
    
    def close_position(self, symbol: str, category: str = "linear") -> bool:
        """Close a position"""
        params = {
            "category": category,
            "symbol": symbol,
            "orderType": "Market",
            "timeInForce": "GTC",
            "reduceOnly": True
        }
        result = self._request("POST", "/v5/order/create", params, signed=True)
        return result.get("retCode") == 0
    
    def get_instruments_info(self, category: str = "linear") -> List[Dict]:
        """Get instruments information including max leverage"""
        params = {"category": category, "limit": 1000}
        result = self._request("GET", "/v5/market/instruments-info", params)
        if result.get("retCode") == 0:
            return result.get("result", {}).get("list", [])
        return []


class FVGDetector:
    """Fair Value Gap Detection Algorithm"""
    
    def __init__(self, threshold_percent: float = 0.0, auto_threshold: bool = False):
        self.threshold_percent = threshold_percent / 100.0
        self.auto_threshold = auto_threshold
        self.threshold_sum = 0.0
        self.bar_count = 0


    def detect_fvg(self, klines: List[List]) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Detect Fair Value Gap from kline data
        Bybit kline format: [startTime, openPrice, highPrice, lowPrice, closePrice, volume, turnover]
        Returns: (signal_type, fvg_data) where signal_type is 'BULL', 'BEAR', or None
        """
        if len(klines) < 3:
            return None, None
        
        # Convert to float - Bybit returns newest first, so reverse to get oldest first
        klines = [[float(x) if isinstance(x, str) else x for x in k] for k in reversed(klines)]
        
        # We need at least 3 candles
        if len(klines) < 3:
            return None, None
        
        # Get latest 3 candles (in Pine Script terms: current, [1], [2])
        current = klines[-1]  # Latest bar (index 0 in Pine)
        prev1 = klines[-2]    # Bar [1] in Pine
        prev2 = klines[-3]    # Bar [2] in Pine
        
        # Extract OHLC
        # Format: [time, open, high, low, close, volume, turnover]
        # Pine Script: low (current), high[2] (prev2), close[1] (prev1)
        low_current = current[3]
        high_current = current[2]
        close_prev1 = prev1[4]
        high_prev2 = prev2[2]
        low_prev2 = prev2[3]
        
        # Calculate threshold
        if self.auto_threshold:
            self.bar_count += 1
            if low_current > 0:
                self.threshold_sum += (high_current - low_current) / low_current
            threshold = self.threshold_sum / self.bar_count if self.bar_count > 0 else 0
        else:
            threshold = self.threshold_percent
        
        # Bullish FVG: low > high[2] and close[1] > high[2] and gap% > threshold
        if high_prev2 > 0:
            bull_gap_pct = (low_current - high_prev2) / high_prev2
            bull_fvg = (low_current > high_prev2 and 
                       close_prev1 > high_prev2 and 
                       bull_gap_pct > threshold)
        else:
            bull_fvg = False
        
        # Bearish FVG: high < low[2] and close[1] < low[2] and gap% > threshold
        if high_current > 0:
            bear_gap_pct = (low_prev2 - high_current) / high_current
            bear_fvg = (high_current < low_prev2 and 
                       close_prev1 < low_prev2 and 
                       bear_gap_pct > threshold)
        else:
            bear_fvg = False
        
        if bull_fvg:
            return "BULL", {
                "max": low_current,
                "min": high_prev2,
                "time": current[0]
            }
        elif bear_fvg:
            return "BEAR", {
                "max": low_prev2,
                "min": high_current,
                "time": current[0]
            }
        
        return None, None




class Position:
    """Position tracking with trailing stops"""
    
    def __init__(self, symbol: str, side: str, entry_price: float, quantity: float,
                 leverage: int, stop_loss_price: float, take_profit_price: float,
                 trailing_stop_percent: float, trailing_tp_percent: float):
        self.symbol = symbol
        self.side = side  # "Buy" or "Sell"
        self.entry_price = entry_price
        self.quantity = quantity
        self.leverage = leverage
        self.stop_loss_price = stop_loss_price
        self.take_profit_price = take_profit_price
        self.trailing_stop_percent = trailing_stop_percent
        self.trailing_tp_percent = trailing_tp_percent
        self.highest_price = entry_price if side == "Buy" else None
        self.lowest_price = entry_price if side == "Sell" else None
        self.opened_at = datetime.now()
        
    def update_trailing(self, current_price: float) -> Tuple[bool, bool]:
        """
        Update trailing stop and take profit
        Returns: (should_update_sl, should_update_tp)
        """
        should_update_sl = False
        should_update_tp = False
        
        if self.side == "Buy":  # Long position
            # Update highest price
            if current_price > self.highest_price:
                self.highest_price = current_price
                
                # Update trailing stop loss
                if self.trailing_stop_percent > 0:
                    new_sl = self.highest_price * (1 - self.trailing_stop_percent / 100)
                    if new_sl > self.stop_loss_price:
                        self.stop_loss_price = new_sl
                        should_update_sl = True
                
                # Update trailing take profit
                if self.trailing_tp_percent > 0:
                    new_tp = self.highest_price * (1 + self.trailing_tp_percent / 100)
                    if new_tp > self.take_profit_price:
                        self.take_profit_price = new_tp
                        should_update_tp = True
        
        else:  # Short position
            # Update lowest price
            if current_price < self.lowest_price:
                self.lowest_price = current_price
                
                # Update trailing stop loss
                if self.trailing_stop_percent > 0:
                    new_sl = self.lowest_price * (1 + self.trailing_stop_percent / 100)
                    if new_sl < self.stop_loss_price:
                        self.stop_loss_price = new_sl
                        should_update_sl = True
                
                # Update trailing take profit
                if self.trailing_tp_percent > 0:
                    new_tp = self.lowest_price * (1 - self.trailing_tp_percent / 100)
                    if new_tp < self.take_profit_price:
                        self.take_profit_price = new_tp
                        should_update_tp = True
        
        return should_update_sl, should_update_tp


    def get_roi_percent(self, current_price: float) -> float:
        """Calculate ROI percentage"""
        if self.side == "Buy":
            roi = ((current_price - self.entry_price) / self.entry_price) * 100 * self.leverage
        else:
            roi = ((self.entry_price - current_price) / self.entry_price) * 100 * self.leverage
        return roi
    
    def should_close(self, current_price: float) -> bool:
        """Check if position should be closed based on SL/TP"""
        if self.side == "Buy":
            return current_price <= self.stop_loss_price or current_price >= self.take_profit_price
        else:
            return current_price >= self.stop_loss_price or current_price <= self.take_profit_price
    
    def __str__(self) -> str:
        return (f"{self.symbol} {self.side} | Entry: {self.entry_price:.4f} | "
                f"Qty: {self.quantity} | Leverage: {self.leverage}x | "
                f"SL: {self.stop_loss_price:.4f} | TP: {self.take_profit_price:.4f}")


class DemoMode:
    """Demo trading simulator using real Bybit chart data"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.closed_trades = []
        
    def open_position(self, position: Position) -> bool:
        """Open a demo position"""
        if position.symbol in self.positions:
            return False
        
        # Calculate position value
        position_value = position.quantity * position.entry_price / position.leverage
        
        if position_value > self.balance:
            return False
        
        self.balance -= position_value
        self.positions[position.symbol] = position
        return True
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[float]:
        """Close a demo position and return PnL"""
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        pnl = self._calculate_pnl(position, exit_price)
        
        # Return margin
        position_value = position.quantity * position.entry_price / position.leverage
        self.balance += position_value + pnl
        
        # Record trade
        self.closed_trades.append({
            "symbol": symbol,
            "side": position.side,
            "entry": position.entry_price,
            "exit": exit_price,
            "pnl": pnl,
            "roi": position.get_roi_percent(exit_price),
            "closed_at": datetime.now()
        })
        
        del self.positions[symbol]
        return pnl


    def _calculate_pnl(self, position: Position, exit_price: float) -> float:
        """Calculate PnL for a position"""
        if position.side == "Buy":
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity
        return pnl
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """Get total account value including unrealized PnL"""
        total = self.balance
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position_value = position.quantity * position.entry_price / position.leverage
                pnl = self._calculate_pnl(position, current_prices[symbol])
                total += position_value + pnl
        return total


class FVGTradingBot:
    """Main trading bot class"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.api = BybitAPI(
            api_key=self.config.get("api_key", ""),
            api_secret=self.config.get("api_secret", ""),
            testnet=self.config.get("testnet", False)
        )
        self.fvg_detector = FVGDetector(
            threshold_percent=self.config.get("fvg_threshold_percent", 0.0),
            auto_threshold=self.config.get("auto_threshold", False)
        )
        self.demo_mode = None
        if self.config.get("demo_mode", True):
            self.demo_mode = DemoMode(initial_balance=self.config.get("demo_initial_balance", 10000.0))
        
        self.positions: Dict[str, Position] = {}
        self.instruments_cache = {}
        self.last_scan_time = 0
        self.running = False
        
        self._print_header()


    def _print_header(self):
        """Print bot header"""
        print("=" * 80)
        print(f"Fair Value Gap Trading Bot v{VERSION}")
        print("Based on LuxAlgo Fair Value Gap Strategy")
        print("© beaver and raylaraykapre - 2024")
        print("Licensed under CC BY-NC-SA 4.0")
        print("=" * 80)
        mode = "DEMO" if self.demo_mode else "LIVE"
        print(f"Mode: {mode}")
        print(f"Timeframe: {self.config.get('timeframe', '5')}")
        print(f"Scan Interval: {self.config.get('scan_interval_seconds', 60)}s")
        print(f"Max Open Positions: {self.config.get('max_open_positions', 3)}")
        print(f"Wallet Usage per Position: {self.config.get('wallet_percent_per_position', 80)}%")
        print("=" * 80)
        print()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            print("Creating default config...")
            default_config = self._get_default_config()
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Default config created at {config_path}")
            print("Please edit the config file and restart the bot.")
            exit(0)
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            exit(1)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "api_key": "YOUR_API_KEY_HERE",
            "api_secret": "YOUR_API_SECRET_HERE",
            "testnet": False,
            "demo_mode": True,
            "demo_initial_balance": 10000.0,
            "timeframe": "5",
            "scan_interval_seconds": 60,
            "wallet_percent_per_position": 80,
            "max_open_positions": 3,
            "leverage_percent": 30,
            "take_profit_percent": 2.0,
            "stop_loss_percent": 1.0,
            "trailing_stop_percent": 0.5,
            "trailing_tp_percent": 0.5,
            "min_volume_usdt": 1000000,
            "fvg_threshold_percent": 0.0,
            "auto_threshold": False,
            "excluded_symbols": []
        }


    def _calculate_leverage(self, symbol: str) -> int:
        """Calculate leverage based on config percentage and max leverage"""
        if symbol not in self.instruments_cache:
            return 1
        
        max_leverage = self.instruments_cache[symbol].get("maxLeverage", "1")
        max_lev = int(float(max_leverage))
        leverage_percent = self.config.get("leverage_percent", 30)
        
        calculated_leverage = max(1, int(max_lev * leverage_percent / 100))
        return min(calculated_leverage, max_lev)
    
    def _get_tradable_symbols(self) -> List[str]:
        """Get list of tradable symbols with volume"""
        self._log("Scanning for tradable perpetuals...")
        
        tickers = self.api.get_tickers(category="linear")
        instruments = self.api.get_instruments_info(category="linear")
        
        # Build instruments cache
        self.instruments_cache = {}
        for inst in instruments:
            symbol = inst.get("symbol", "")
            self.instruments_cache[symbol] = {
                "maxLeverage": inst.get("leverageFilter", {}).get("maxLeverage", "1"),
                "minOrderQty": inst.get("lotSizeFilter", {}).get("minOrderQty", "0.001"),
                "qtyStep": inst.get("lotSizeFilter", {}).get("qtyStep", "0.001")
            }
        
        tradable = []
        min_volume = self.config.get("min_volume_usdt", 1000000)
        excluded = self.config.get("excluded_symbols", [])
        
        for ticker in tickers:
            symbol = ticker.get("symbol", "")
            volume = float(ticker.get("turnover24h", 0))
            
            # Filter: must be USDT pair, have volume, not excluded
            if (symbol.endswith("USDT") and 
                volume >= min_volume and 
                symbol not in excluded and
                symbol in self.instruments_cache):
                tradable.append(symbol)
        
        self._log(f"Found {len(tradable)} tradable symbols")
        return tradable
    
    def _log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")


    def _scan_symbol(self, symbol: str) -> Optional[Tuple[str, Dict]]:
        """Scan a symbol for FVG signals"""
        timeframe = self.config.get("timeframe", "5")
        klines = self.api.get_kline_data(symbol, timeframe, limit=200)
        
        if not klines or len(klines) < 3:
            return None
        
        signal, fvg_data = self.fvg_detector.detect_fvg(klines)
        
        if signal:
            # Get current price
            current_price = float(klines[0][4])  # Close price of latest candle
            return signal, {
                "symbol": symbol,
                "signal": signal,
                "fvg_data": fvg_data,
                "current_price": current_price
            }
        
        return None
    
    def _open_position(self, signal_data: Dict):
        """Open a new position"""
        symbol = signal_data["symbol"]
        signal = signal_data["signal"]
        current_price = signal_data["current_price"]
        
        # Check if we already have a position
        if symbol in self.positions:
            return
        
        # Check max open positions
        if len(self.positions) >= self.config.get("max_open_positions", 3):
            return
        
        # Calculate position size
        if self.demo_mode:
            balance = self.demo_mode.get_balance()
        else:
            balance = self.api.get_wallet_balance()
            if balance == 0:
                self._log(f"✗ Failed to get wallet balance for {symbol}")
                return
        
        wallet_percent = self.config.get("wallet_percent_per_position", 80)
        position_value = balance * (wallet_percent / 100)
        
        # Calculate leverage
        leverage = self._calculate_leverage(symbol)
        if leverage == 1 and symbol in self.instruments_cache:
            # Fallback if instrument cache doesn't have leverage
            leverage = max(1, int(self.config.get("leverage_percent", 30) / 100 * 50))
        
        # Calculate quantity (position_value * leverage / price)
        quantity = (position_value * leverage) / current_price
        
        # Get instrument constraints
        min_qty = 0.001
        qty_step = 0.001
        
        if symbol in self.instruments_cache:
            min_qty = float(self.instruments_cache[symbol].get("minOrderQty", "0.001"))
            qty_step = float(self.instruments_cache[symbol].get("qtyStep", "0.001"))
            
            # Round to instrument's step
            quantity = round(quantity / qty_step) * qty_step
            
            # Check minimum
            if quantity < min_qty:
                self._log(f"✗ Quantity {quantity} below minimum {min_qty} for {symbol}")
                return
        
        # Format quantity string (remove trailing zeros)
        qty_str = f"{quantity:.8f}".rstrip('0').rstrip('.')
        
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

        # Create position object
        position = Position(
            symbol=symbol,
            side=side,
            entry_price=current_price,
            quantity=quantity,
            leverage=leverage,
            stop_loss_price=sl_price,
            take_profit_price=tp_price,
            trailing_stop_percent=self.config.get("trailing_stop_percent", 0.5),
            trailing_tp_percent=self.config.get("trailing_tp_percent", 0.5)
        )
        
        # Execute trade
        if self.demo_mode:
            success = self.demo_mode.open_position(position)
            if success:
                self.positions[symbol] = position
                self._log(f"✓ DEMO OPENED: {position}")
            else:
                self._log(f"✗ Insufficient demo balance for {symbol}")
        else:
            try:
                # Set leverage first
                leverage_set = self.api.set_leverage(symbol, str(leverage), str(leverage))
                if not leverage_set:
                    self._log(f"⚠ Could not set leverage for {symbol}, using default")
                
                # Place market order (without SL/TP initially)
                order_id = self.api.place_order(
                    symbol=symbol,
                    side=side,
                    order_type="Market",
                    qty=qty_str
                )
                
                if order_id:
                    self.positions[symbol] = position
                    self._log(f"✓ LIVE OPENED: {position}")
                    
                    # Set TP/SL after order is filled (give it a moment)
                    time.sleep(1)
                    self.api.set_trading_stop(
                        symbol=symbol,
                        stop_loss=f"{sl_price:.8f}".rstrip('0').rstrip('.'),
                        take_profit=f"{tp_price:.8f}".rstrip('0').rstrip('.')
                    )
                else:
                    self._log(f"✗ Failed to open position for {symbol} (order rejected)")
            except Exception as e:
                self._log(f"✗ Error opening position for {symbol}: {str(e)}")
    
    def _update_positions(self):
        """Update trailing stops for open positions"""
        if not self.positions:
            return
        
        symbols_to_close = []
        
        for symbol, position in self.positions.items():
            # Get current price
            klines = self.api.get_kline_data(symbol, self.config.get("timeframe", "5"), limit=1)
            if not klines:
                continue
            
            current_price = float(klines[0][4])
            
            # Update trailing
            should_update_sl, should_update_tp = position.update_trailing(current_price)
            
            # Update trading stops if needed
            if not self.demo_mode and (should_update_sl or should_update_tp):
                self.api.set_trading_stop(
                    symbol=symbol,
                    stop_loss=str(position.stop_loss_price),
                    take_profit=str(position.take_profit_price)
                )
                self._log(f"Updated trailing for {symbol} - SL: {position.stop_loss_price:.4f}, TP: {position.take_profit_price:.4f}")
            
            # Check if should close
            if position.should_close(current_price):
                symbols_to_close.append((symbol, current_price))
        
        # Close positions
        for symbol, exit_price in symbols_to_close:
            self._close_position(symbol, exit_price)


    def _close_position(self, symbol: str, exit_price: float):
        """Close a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        roi = position.get_roi_percent(exit_price)
        
        if self.demo_mode:
            pnl = self.demo_mode.close_position(symbol, exit_price)
            if pnl is not None:
                self._log(f"✓ DEMO CLOSED: {symbol} | Entry: {position.entry_price:.4f} | "
                         f"Exit: {exit_price:.4f} | ROI: {roi:.2f}% | PnL: ${pnl:.2f}")
        else:
            success = self.api.close_position(symbol)
            if success:
                self._log(f"✓ LIVE CLOSED: {symbol} | Entry: {position.entry_price:.4f} | "
                         f"Exit: {exit_price:.4f} | ROI: {roi:.2f}%")
        
        del self.positions[symbol]
    
    def _display_positions(self):
        """Display current open positions"""
        if not self.positions:
            return
        
        print("\n" + "=" * 80)
        print("OPEN POSITIONS:")
        print("=" * 80)
        
        for symbol, position in self.positions.items():
            # Get current price and ROI
            klines = self.api.get_kline_data(symbol, self.config.get("timeframe", "5"), limit=1)
            if klines:
                current_price = float(klines[0][4])
                roi = position.get_roi_percent(current_price)
                
                print(f"{position} | Current: {current_price:.4f} | ROI: {roi:.2f}%")
        
        if self.demo_mode:
            balance = self.demo_mode.get_balance()
            current_prices = {}
            for symbol in self.positions.keys():
                klines = self.api.get_kline_data(symbol, self.config.get("timeframe", "5"), limit=1)
                if klines:
                    current_prices[symbol] = float(klines[0][4])
            
            total_value = self.demo_mode.get_total_value(current_prices)
            print(f"\nDemo Balance: ${balance:.2f} | Total Value: ${total_value:.2f}")
        
        print("=" * 80 + "\n")


    def run(self):
        """Main bot loop"""
        self.running = True
        self._log("Bot started!")
        
        try:
            while self.running:
                try:
                    # Update existing positions
                    self._update_positions()
                    
                    # Display positions
                    self._display_positions()
                    
                    # Check if we can open new positions
                    if len(self.positions) < self.config.get("max_open_positions", 3):
                        # Get tradable symbols
                        symbols = self._get_tradable_symbols()
                        
                        # Scan for signals
                        self._log(f"Scanning {len(symbols)} symbols for FVG signals...")
                        signals_found = 0
                        
                        for symbol in symbols:
                            if symbol in self.positions:
                                continue
                            
                            result = self._scan_symbol(symbol)
                            if result:
                                signal, signal_data = result
                                signals_found += 1
                                self._log(f"Signal found: {symbol} - {signal}")
                                self._open_position(signal_data)
                                
                                # Check if we reached max positions
                                if len(self.positions) >= self.config.get("max_open_positions", 3):
                                    break
                        
                        if signals_found == 0:
                            self._log("No signals found")
                    else:
                        self._log(f"Max positions reached ({len(self.positions)})")
                    
                    # Sleep until next scan
                    scan_interval = self.config.get("scan_interval_seconds", 60)
                    self._log(f"Sleeping for {scan_interval} seconds...\n")
                    time.sleep(scan_interval)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self._log(f"Error in main loop: {str(e)}")
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            self._log("\nShutting down bot...")
            self.running = False
            
            # Close all positions on shutdown
            if self.positions:
                self._log("Closing all open positions...")
                for symbol in list(self.positions.keys()):
                    klines = self.api.get_kline_data(symbol, self.config.get("timeframe", "5"), limit=1)
                    if klines:
                        current_price = float(klines[0][4])
                        self._close_position(symbol, current_price)
            
            self._log("Bot stopped!")


if __name__ == "__main__":
    import sys
    
    config_file = "config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    bot = FVGTradingBot(config_file)
    bot.run()
