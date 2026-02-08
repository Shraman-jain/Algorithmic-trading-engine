"""
Example Trading Strategy
========================

Simple moving average crossover strategy for demonstration.

⚠️ This is NOT the actual production strategy - it's a
   simplified example to show how strategies are implemented.

Version: 1.0.0
"""

from datetime import datetime
from typing import Dict, Tuple
from .base_strategy import BaseStrategy


class SimpleMAStrategy(BaseStrategy):
    """
    Basic moving average strategy for educational purposes.
    
    Entry Logic (Example):
    - Price above 9-day MA
    - Price above 200-day MA
    - Sufficient volume
    - Green candle or Doji
    
    Exit Logic (Example):
    - Stop loss: 2% below entry
    - Target: 4% above entry
    """
    
    def __init__(self, config):
        self.config = config
    
    def validate_entry_conditions(
        self,
        price_data: Dict[str, float],
        indicators: Dict[str, any],
        timestamp: datetime
    ) -> Tuple[bool, Dict]:
        """Check if basic MA conditions are met."""
        
        ltp = price_data.get('ltp', 0)
        open_price = price_data.get('open', 0)
        volume = price_data.get('volume', 0)
        
        # Get moving averages
        ma = indicators.get('daily_ma', 0)
        
        # Volume filter
        has_volume = volume > self.config.MIN_VOLUME_THRESHOLD
        
        # Price above MAs
        above_mas = ltp > ma
        
        # Candle type (simplified)
        price_change_pct = (ltp - open_price) / open_price if open_price else 0
        is_green = price_change_pct > 0.005  # 0.5% gain
        
        
        # Combined validation
        is_valid = has_volume and above_mas and is_green
        
        setup_details = {
            'strategy': 'simple_ma_crossover',
            'ltp': ltp,
            'ma': ma,
            'volume': volume,
            'candle_type': 'green' if is_green else 'red'
        }
        
        return is_valid, setup_details
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        account_size: float,
        planned_trades: int
    ) -> int:
        """Calculate position size based on fixed percentage risk."""
        
        if planned_trades <= 0:
            planned_trades = 5
        
        # Risk per trade
        risk_per_trade = 0.01 / planned_trades  # 1% daily risk
        risk_amount = account_size * risk_per_trade
        
        # Risk per share
        risk_per_share = entry_price - stop_loss
        
        if risk_per_share <= 0:
            return 0
        
        # Calculate quantity
        quantity = int(risk_amount / risk_per_share)
        
        # Capital constraint
        max_quantity = int(account_size / entry_price)
        
        return min(quantity, max_quantity, 100)  # Cap at 100 shares
    
    def get_exit_levels(
        self,
        entry_price: float,
        price_data: Dict[str, float]
    ) -> Tuple[float, float]:
        """Calculate simple percentage-based exits."""
        
        # 2% stop loss
        stop_loss = entry_price * 0.98
        
        # 4% target
        target = entry_price * 1.04
        
        return stop_loss, target
    
    def check_time_window(self, timestamp: datetime) -> bool:
        """Execute trades only in last minute before close."""
        return (
            timestamp.hour == 15 and
            timestamp.minute == 29 and
            timestamp.second >= 40
        )
