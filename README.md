# 🇮🇳 Indian Stock Market AI Engine (MiroFish Swarm Architecture)

An advanced, real-time AI Agent trading and market analysis engine built specifically for the **Indian Stock Market (NSE & BSE)**, powered by the multi-agent swarm intelligence concept adapted from **[MiroFish](https://github.com/666ghj/MiroFish)**.

---

## ⚡ Key Highlights

1. **Live Indian Market Data (NSE & BSE)**
   - Real-time intraday feeds for Indices (`NIFTY 50`, `BANK NIFTY`, `SENSEX`, `FINNIFTY`) and all NSE/BSE equities (`RELIANCE`, `TCS`, `HDFCBANK`, `TATAMOTORS`, `INFY`, etc.).
   - Multi-Timeframe simultaneous ingestion: **5m**, **15m**, **1h**, and **1D**.

2. **Complete Pattern Recognition Engine ("Koi bhi chiz miss na ho")**
   - **Candlestick Patterns**: Hammer, Inverted Hammer, Shooting Star, Hanging Man, Bullish/Bearish Engulfing, Morning/Evening Star, Dragonfly/Gravestone Doji, Marubozu, Piercing Line, Dark Cloud Cover, Harami, Tweezer Top/Bottom, Three White Soldiers, Three Black Crows.
   - **Classical Chart Patterns**: Head and Shoulders & Inverse H&S, Double Top (M) & Double Bottom (W), Triple Top/Bottom, Ascending/Descending/Symmetrical Triangles, Rising/Falling Wedges, Bull/Bear Flags, and Breakouts.
   - **Technical Indicators**: EMAs (9, 20, 50, 200), Golden/Death Cross, RSI (14) + Regular & Hidden Divergences, MACD, Bollinger Bands with Squeeze Detection, Supertrend (10, 3), ATR (14), OBV, VWAP, Standard Floor Pivots, Camarilla Pivots, and Fibonacci Retracements.

3. **MiroFish Multi-Agent Swarm Intelligence (Backend Sandbox)**
   - Instead of single-model hallucinations, 5 specialized agents deliberate in a parallel simulation:
     - 📐 **Aarav (Price Action Chartist)**: Evaluates candlestick & geometric formations.
     - 📈 **Vikram (MTF Trend Confluence)**: Evaluates institutional trend alignment across 5m/15m/1h/1D.
     - ⚡ **Priya (Momentum & Divergences)**: Scans RSI, MACD, and exhaustion traps.
     - 🏦 **Rajesh (Smart Money & Volume Flow)**: Tracks VWAP, volume spikes, and institutional footprints.
     - 🛡️ **Kavita (Risk Sentinel & Gatekeeper)**: Enforces ATR-based invalidation stop-loss and strict R:R ratios.

4. **Zero-Loop Shield (Eliminating AI's "Dark Side")**
   - Pure recursive ReAct loops and unconstrained autonomous loops often cause deadlocks, token drain, and infinite repetition.
   - Powered by `LoopProtector`:
     - **Strict Bounded Rounds**: Maximum 2 cross-examination debate passes.
     - **DAG Execution**: Directed Acyclic Graph prevents recursive cyclic re-entry.
     - **Watchdog Timer**: Strict timeout budget.
     - **Anti-Oscillation Guard**: Instantly halts if agents flip-flop repeatedly.

5. **Self-Developing & Self-Learning Engine**
   - **Persistent Ledger (`knowledge_base/prediction_ledger.json`)**: Records predictions, targets, and stop-loss levels.
   - **Dynamic Weight Calibrator**: Calibrates pattern confidence based on empirical win-rates in Indian stocks.
   - **Self-Refining Code Agent (`learning/self_refine.py`)**: AST syntax verification, mathematical sanity checks, and self-healing system state.

---

## 🚀 Quick Start Guide

### Option 1: 1-Click Launch (Windows)
Double-click `run.bat` in `d:\AGI\` to open the interactive menu:
- **1**: Launch Interactive Web Dashboard (`http://127.0.0.1:8000`)
- **2**: Run Interactive Terminal CLI
- **3**: Run Quick NIFTY 50 Analysis
- **4**: Run Self-Refining AI Diagnostics & Health Check

---

### Option 2: Web Dashboard Mode
Start the FastAPI server:
```powershell
.\.venv\Scripts\python.exe main.py --web
```
Open your browser at **`http://127.0.0.1:8000`** to access the Dark Mode Glassmorphism Dashboard with interactive canvas charts, pattern radar, and live swarm debate transcript.

---

### Option 3: Terminal CLI Mode
Analyze any Indian stock or index in the terminal:
```powershell
# Analyze NIFTY 50
.\.venv\Scripts\python.exe cli.py --symbol NIFTY

# Analyze BANK NIFTY
.\.venv\Scripts\python.exe cli.py --symbol BANKNIFTY

# Analyze RELIANCE or TCS
.\.venv\Scripts\python.exe cli.py --symbol RELIANCE
.\.venv\Scripts\python.exe cli.py --symbol TCS
```

---

### Option 4: Self-Refining System Diagnostics
Run full code inspection and self-healing:
```powershell
.\.venv\Scripts\python.exe main.py --refine
```

---

## 📂 Project Architecture

```
d:\AGI\
  ├── MiroFish_upstream\      # Downloaded upstream MiroFish repository
  ├── config.py               # Symbols, timeframe parameters & loop bounds
  ├── engine.py               # Master Coordinator Orchestrating Swarm & Market Data
  ├── server.py               # FastAPI Web & REST Server
  ├── cli.py                  # Terminal CLI with Rich formatting
  ├── main.py                 # Unified entrypoint
  ├── run.bat                 # 1-click Windows launcher
  ├── indian_market\
  │   ├── data_fetcher.py     # Live 5m, 15m, 1h, 1D candle fetcher with IST timestamps
  │   ├── symbol_resolver.py  # User input resolver (NIFTY, BANKNIFTY, RELIANCE, etc.)
  │   └── market_depth.py     # Standard & Camarilla Pivots, Fibonacci, Support/Resistance
  ├── patterns\
  │   ├── candlestick.py      # Complete Japanese Candlestick detector
  │   ├── chart_patterns.py   # Geometric Classical chart pattern detector
  │   └── pattern_engine.py   # Multi-timeframe pattern aggregator
  ├── indicators\
  │   ├── technical.py        # EMA 9/20/50/200, RSI, MACD, Bollinger Bands, Supertrend, ATR
  │   ├── divergence.py       # Regular & Hidden RSI/MACD divergences
  │   └── mtf_confluence.py   # 5m/15m/1h/1D Confluence scoring engine
  ├── mirofish_core\
  │   ├── loop_protector.py   # Zero-Loop Circuit Breaker & Anti-Recursion Shield
  │   ├── swarm_personas.py   # Aarav, Vikram, Priya, Rajesh, Kavita agent personas
  │   ├── simulation_sandbox.py # Bounded parallel swarm debate sandbox
  │   └── consensus_engine.py # Emergent trade plan & probability generator
  ├── learning\
  │   ├── pattern_ledger.py   # Historical prediction & win-rate logger
  │   ├── weight_calibrator.py# Dynamic pattern confidence calibrator
  │   └── self_refine.py      # AST syntax analyzer & self-healing engine
  └── ui\
      ├── index.html          # Glassmorphism dark-mode UI
      └── static\
          ├── style.css       # Responsive dark-theme styling
          └── app.js          # Interactive HTML5 Canvas chart & live REST consumer
```
