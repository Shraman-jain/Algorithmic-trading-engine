"""
Abstract Strategy Interface
===========================

Defines the contract that all trading strategies must implement.
This demonstrates the Strategy Pattern for pluggable algorithms.

Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple
from datetime import datetime


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All concrete strategies must implement these methods.
    This allows different trading algorithms to be swapped
    without modifying the trading engine infrastructure.
    """
    
    @abstractmethod
    def validate_entry_conditions(
        self,
        price_data: Dict[str, float],
        indicators: Dict[str, any],
        timestamp: datetime
    ) -> Tuple[bool, Dict]:
        """
        Determine if entry conditions are met.
        
        Args:
            price_data: {'open', 'high', 'low', 'close', 'volume', 'ltp'}
            indicators: Technical indicators (MAs, etc.)
            timestamp: Current market timestamp
            
        Returns:
            (is_valid_setup, setup_details_dict)
        """
        pass
    
    @abstractmethod
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        account_size: float,
        planned_trades: int
    ) -> int:
        """
        Calculate number of shares to buy based on risk management.
        
        Args:
            entry_price: Planned entry price
            stop_loss: Stop loss price
            account_size: Total trading capital
            planned_trades: Number of planned trades today
            
        Returns:
            Number of shares (quantity)
        """
        pass
    
    @abstractmethod
    def get_exit_levels(
        self,
        entry_price: float,
        price_data: Dict[str, float]
    ) -> Tuple[float, float]:
        """
        Calculate stop loss and target prices.
        
        Args:
            entry_price: Actual or planned entry price
            price_data: OHLC data for reference
            
        Returns:
            (stop_loss_price, target_price)
        """
        pass
    
    @abstractmethod
    def check_time_window(self, timestamp: datetime) -> bool:
        """
        Check if current time is valid for trade execution.
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            True if within trading window
        """
        pass
