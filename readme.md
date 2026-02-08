# 🚀 Automated Trading Engine

A production-grade algorithmic trading system with real-time market data processing,
technical analysis, and automated risk management.

## 🎯 What This Repository Demonstrates

This is a **system design showcase** for building scalable trading infrastructure:

- ✅ Clean architecture with separation of concerns
- ✅ Strategy Pattern for pluggable trading algorithms  
- ✅ Real-time WebSocket data processing (200+ instruments)
- ✅ Multi-broker integration (Zerodha, Upstox)
- ✅ Automated risk management and position sizing
- ✅ Multi-timeframe technical indicators (Daily/Weekly/Monthly)

## 🔒 About the Strategy

The actual trading strategy (developed by a CFA Level 1 analyst) is **proprietary**
and not included in this public repository.

**This repo contains:**
- ✅ Complete system architecture
- ✅ All infrastructure code
- ✅ Abstract strategy interfaces
- ✅ Example demonstration strategy

**Not included:**
- ❌ Proprietary entry/exit rules
- ❌ Specific indicator thresholds
- ❌ Position sizing formulas

## 📊 System Architecture

### **1. Data Layer** (Real-time Market Data Pipeline)
- **WebSocket Feed**: Persistent connection to Upstox API for live market data
- **Protobuf Decoder**: Decodes binary market data messages to structured format
- **Metadata Storage**: Historical OHLC data stored in Pickle (fast) + JSON (readable)
- **Instrument Loader**: Filters stocks by market cap and loads trading universe
- **Market Cap Updater**: Daily refresh of market capitalization data

### **2. Indicators Layer** (Technical Analysis Engine)
- **Moving Average Calculator**: Computes MAs across 3 timeframes
- **Multi-Timeframe Aggregation**: Daily → Weekly → Monthly OHLC conversion
- **Incremental Updates**: Efficient indicator updates using deque data structure
- **Signal Validator**: Checks if technical setup conditions are met

### **3. Strategy Layer** (Trading Logic - Abstracted)
- **Base Strategy Interface**: Abstract class defining entry/exit contract
- **Setup Validator**: Validates price, volume, and indicator conditions
- **Time Window Checker**: Ensures trades execute in valid time window
- **Example Strategy**: Demo implementation (actual strategy is private)

### **4. Portfolio Management Layer**
- **Position Tracker**: Maintains active positions in CSV database
- **Exit Monitor**: Continuously checks stop loss and target conditions
- **Trade Logger**: Records entry/exit with timestamps and P&L
- **Active Positions Filter**: Prevents duplicate entries

### **5. Risk Management Layer**
- **Position Sizer**: Calculates share quantity based on risk parameters
- **Daily Risk Limiter**: Caps total daily risk at configured percentage
- **Stop Loss Calculator**: Dynamic SL based on price action
- **Capital Constraint**: Ensures positions don't exceed available capital

### **6. Execution Layer** (Broker Integration)
- **Broker Adapter Pattern**: Abstract interface for multiple brokers
- **Zerodha Connector**: Places orders via Kite Connect API
- **GTT Order Manager**: Sets automated stop loss and target orders
- **Order Logger**: Tracks all order placement attempts

### **7. Orchestration Layer** (Main Engine)
- **WebSocket Manager**: Handles connection, subscription, reconnection
- **Event Loop**: Async processing of market data stream
- **Instrument Iterator**: Processes 200+ stocks in parallel
- **State Manager**: Tracks live setups and portfolio state
- **Shutdown Handler**: Graceful cleanup on market close

### **Data Flow**
1. **Market Open** → Load metadata + active portfolio
2. **Real-time** → WebSocket receives tick → Update indicators → Validate setup
3. **Setup Found** → Calculate position size → Log setup
4. **Time Window** → Execute order → Add to portfolio → Place GTT exits
5. **Continuous** → Monitor exit conditions → Update portfolio on exit
6. **Market Close** → Save metadata → Update market cap → Shutdown

### **Design Patterns Used**
- **Strategy Pattern**: Pluggable trading algorithms
- **Adapter Pattern**: Multi-broker abstraction
- **Observer Pattern**: Real-time data event processing
- **Repository Pattern**: Metadata and portfolio persistence
- **Singleton Pattern**: Configuration management

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Real-time Data**: WebSocket + Protocol Buffers
- **Brokers**: Zerodha Kite Connect, Upstox API
- **Data Processing**: Pandas, NumPy
- **State Management**: Pickle + CSV
- **Async I/O**: asyncio, websockets

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Setup

1. Copy `.env.example` to `.env` and add your API credentials
2. Create your strategy file (see `STRATEGY_TEMPLATE.md`)
3. Run metadata generator:
```bash
python scripts/create_metadata.py
```

4. Start the trading engine:
```bash
python src/engine.py
```

## 📈 Key Features

### Real-time Data Pipeline
- WebSocket connection with auto-reconnection
- Protobuf message decoding
- Sub-100ms latency for 200+ instruments

### Multi-Timeframe Analysis
- Daily, Weekly, Monthly OHLC aggregation
- Rolling moving averages (9-day, 200-day)
- Efficient indicator updates using deques

### Risk Management
- Dynamic position sizing based on volat