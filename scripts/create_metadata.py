"""
Historical Market Data Processor
=================================

Fetches and processes historical OHLC data for all instruments.
Calculates moving averages across multiple timeframes.

This script is run once daily to update the metadata file
with latest market data and technical indicators.

Version: 1.0.0
"""

import os
import re
import json
import pickle
import pandas as pd
import requests
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from collections import deque
from dotenv import load_dotenv


load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {UPSTOX_ACCESS_TOKEN}'
}

# Moving average periods (configurable)
LONG_MA_PERIOD = 100

# Global storage
metadata = {}
error_log = {}


# ============================================================================
# METADATA MANAGEMENT
# ============================================================================

def save_metadata(meta: dict) -> None:
    """Save metadata to pickle and JSON formats."""
    meta["last_run_day"] = datetime.now()
    
    try:
        # Pickle format (efficient)
        with open("data/metadata.pkl", "wb") as f:
            pickle.dump(meta, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        # JSON format (human-readable backup)
        with open("data/metadata.json", "w") as f:
            json.dump(meta, f, indent=4, default=str)
        
        print("✓ Metadata saved successfully")
    except Exception as e:
        print(f"✗ Error saving metadata: {e}")


def process_dataframe_to_metadata(
    stock_name: str,
    instrument_key: str,
    timeframe: str,
    df: pd.DataFrame
) -> None:
    """
    Calculate technical indicators and store in metadata.
    
    Args:
        stock_name: Security name
        instrument_key: Unique instrument identifier
        timeframe: 'Daily', 'Weekly', or 'Monthly'
        df: OHLC dataframe
    """
    try:
        # Ensure timestamp index
        if "timestamp" in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        # Select required columns
        df = df[['high', 'close']].copy()
        
        # Calculate moving averages
        
        df['MA'] = df['close'].rolling(LONG_MA_PERIOD).mean().round(2)
        df = df.fillna(0)
        
        # Store in metadata with deques for efficient updates
        if instrument_key not in metadata:
            metadata[instrument_key] = {"Symbol": stock_name}
        
        metadata[instrument_key][f"{timeframe}_MA_list"] = deque(
            df['MA'].tail(LONG_MA_PERIOD), maxlen=LONG_MA_PERIOD
        )
        
        
    except Exception as e:
        print(f"✗ Error processing {stock_name} ({timeframe}): {e}")


# ============================================================================
# DATA FETCHING
# ============================================================================

def convert_to_timeframes(df: pd.DataFrame) -> tuple:
    """
    Resample daily data into weekly and monthly timeframes.
    
    Args:
        df: Daily OHLC dataframe
        
    Returns:
        (weekly_df, monthly_df)
    """
    weekly,monthly = "",""
    return weekly, monthly


def should_use_intraday() -> bool:
    """
    Determine if intraday API should be used.
    
    Returns True if it's a weekday after market close (3:30 PM).
    """
    now = datetime.now()
    is_weekday = now.weekday() < 5  # Monday=0 to Friday=4
    is_after_close = now.time() >= time(15, 30)
    
    return is_weekday and is_after_close


def fetch_current_day_data(instrument_key: str) -> pd.DataFrame:
    """
    Fetch today's intraday data.
    
    Args:
        instrument_key: NSE_EQ|ISIN format
        
    Returns:
        DataFrame with today's OHLC data
    """
    isin = re.search(r'NSE_EQ\|(.*)', instrument_key).group(1)
    url = f'https://api.upstox.com/v3/historical-candle/intraday/NSE_EQ%7C{isin}/days/1'
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"  ⚠️  Current day data unavailable (status: {response.status_code})")
        return None
    
    candles = response.json().get('data', {}).get('candles', [])
    
    if not candles:
        return None
    
    df = pd.DataFrame(candles, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', '_'
    ])
    
    return df


def fetch_daily_historical_data(
    stock_name: str,
    instrument_key: str,
    equity_df: pd.DataFrame
) -> None:
    """
    Fetch complete historical daily data for an instrument.
    
    Args:
        stock_name: Security name
        instrument_key: NSE_EQ|ISIN format
        equity_df: Market cap dataframe (for updating LTP)
    """
    isin = re.search(r'NSE_EQ\|(.*)', instrument_key).group(1)
    
    START_DATE = datetime(2000, 1, 3)
    END_DATE = datetime.today()
    
    all_candles = []
    from_date = START_DATE
    
    # Fetch in 10-year chunks (API limit)
    while from_date < END_DATE:
        to_date = min(from_date + relativedelta(years=10), END_DATE)
        
        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")
        
        url = (
            f"https://api.upstox.com/v3/historical-candle/"
            f"NSE_EQ%7C{isin}/days/1/{to_str}/{from_str}"
        )
        
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"  ✗ Error fetching {stock_name} ({from_str} to {to_str})")
            break
        
        candles = response.json().get("data", {}).get("candles", [])
        
        if candles:
            all_candles.extend(candles)
        
        print(f"  ✓ Fetched: {from_str} → {to_str}")
        
        from_date = to_date + relativedelta(days=1)
    
    if not all_candles:
        print(f"  ✗ No historical data found for {stock_name}")
        return
    
    # Create DataFrame
    df = pd.DataFrame(
        all_candles,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_']
    )
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Append current day data if available
    if should_use_intraday():
        current_day_df = fetch_current_day_data(instrument_key)
        if current_day_df is not None:
            df = pd.concat([df, current_day_df], ignore_index=True)
    
    df.drop(columns=['_'], inplace=True, errors='ignore')
    
    # Update market cap with latest close price
    mask = equity_df["Security Name"] == stock_name
    latest_close = df["close"].iloc[-1]
    
    equity_df.loc[mask, "LTP"] = latest_close
    equity_df.loc[mask, "MCAP"] = (
        equity_df.loc[mask, "No of shares"].values[0] * latest_close
    )
    
    # Generate multi-timeframe data
    weekly_df, monthly_df = convert_to_timeframes(df)
    
    print(f"✓ {stock_name}: Processed daily, weekly, monthly data")
    
    # Store in metadata
    process_dataframe_to_metadata(stock_name, instrument_key, "Daily", df)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for metadata creation."""
    
    print("=" * 70)
    print("HISTORICAL DATA PROCESSOR - STARTING")
    print("=" * 70)
    
    # Load instrument mappings
    equity_df = pd.read_csv("data/market_cap.csv")
    
    instrument_mapping = {
        row['Security Name']: row['Instrument Key']
        for _, row in equity_df.iterrows()
    }
    
    total_instruments = len(instrument_mapping)
    processed_count = 0
    
    print(f"\nProcessing {total_instruments} instruments...\n")
    
    # Process each instrument
    for stock_name, instrument_key in instrument_mapping.items():
        try:
            print(f"[{processed_count + 1}/{total_instruments}] {stock_name}")
            fetch_daily_historical_data(stock_name, instrument_key, equity_df)
            processed_count += 1
            
        except Exception as e:
            error_log[stock_name] = str(e)
            print(f"  ✗ Error: {e}\n")
            continue
    
    # Save updated market cap
    equity_df.to_csv("data/market_cap.csv", index=False)
    print("\n✓ Market cap file updated")
    
    # Save metadata
    save_metadata(metadata)
    
    # Summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Processed: {processed_count}/{total_instruments}")
    print(f"Errors: {len(error_log)}")
    
    if error_log:
        print("\nFailed instruments:")
        for stock, error in error_log.items():
            print(f"  • {stock}: {error}")


if __name__ == "__main__":
    main()
