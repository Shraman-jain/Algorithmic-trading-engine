"""
Trading System Configuration
=============================

Central configuration module for the automated trading engine.
All system parameters, file paths, and trading rules are defined here.

Version: 1.0.0
"""

import os
from pathlib import Path
from abc import ABC, abstractmethod
from dotenv import load_dotenv


class TradingConfig(ABC):
    """
    Central configuration class for the trading system.
    
    Contains all configurable parameters organized into logical sections:
    - API credentials and endpoints
    - Portfolio and risk management settings
    - Market filtering criteria
    - File system paths
    - Trading strategy rules
    - Logging configuration
    
    Usage:
        from config.trading_config import TradingConfig
        capital = TradingConfig.PORTFOLIO_CAPITAL
    """
    
    load_dotenv()

    # ========================================================================
    # API CONFIGURATION
    # ========================================================================
    
    UPSTOX_MARKET_QUOTE_URL = "https://api.upstox.com/v3/market-quote/ohlc"  # Upstox OHLC data endpoint
    UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")  # Upstox API access token for WebSocket authentication
    
    ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")  # Zerodha Kite Connect API key
    ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")  # Zerodha API secret for token generation
    ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")  # Zerodha access token for order execution
    
    # ========================================================================
    # PORTFOLIO & RISK MANAGEMENT (Generic Examples)
    # ========================================================================
    
    PORTFOLIO_CAPITAL = 100000  # Example: ₹1 Lakh
    DAILY_RISK_PERCENTAGE = 0.01  # Example: 1% daily risk
    PLANNED_TRADES_PER_DAY = 5  # Example: 5 trades per day
    
    # ========================================================================
    # MARKET FILTERING (Generic Ranges)
    # ========================================================================
    
    MIN_MARKET_CAP = 50000000000   # Example: ₹5,000 Cr
    MAX_MARKET_CAP = 1000000000000  # Example: ₹1,00,000 Cr
    
    # ========================================================================
    # FILE SYSTEM PATHS
    # ========================================================================
    
    BASE_DIR = Path(__file__).resolve().parent  # Base directory for relative paths
    DATA_DIR = BASE_DIR / "data"
    MARKET_CAP_FILE = DATA_DIR / "market_cap.csv" # CSV file with market cap data and instrument mappings
    INSTRUMENT_KEY_FILE = DATA_DIR / "instruments.csv"  # Instrument key to symbol mapping file
    METADATA_PICKLE_FILE = DATA_DIR / "metadata.pkl" # Historical OHLC and moving averages (binary format)
    METADATA_JSON_FILE = DATA_DIR / "metadata.json" # Human-readable backup of metadata
    PORTFOLIO_FILE = DATA_DIR / "portfolio.csv" # Active positions and trade history
    


    # ========================================================================
    # TRADING STRATEGY RULES
    # ========================================================================
    
    """    These variables define the core decision rules used by the trading engine
        to filter stocks, identify valid candles, manage risk, and set target and stoploss.
    
    """

    
    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    
    LOG_FILE = "trading_engine.log"  # Application log file name
    LOG_MAX_BYTES = 5 * 1024 * 1024  # Maximum log file size before rotation (5 MB)
    LOG_BACKUP_COUNT = 10  # Number of rotated log files to keep



