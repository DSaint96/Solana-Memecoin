Solana Memecoin Trading Bot
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Solana](https://img.shields.io/badge/Blockchain-Solana-9945FF?style=flat-square)
![Status](https://img.shields.io/badge/Status-Phase%201%20%7C%20Paper%20Trading-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)
A Python-based trading bot for Solana memecoins that monitors live market data via the Birdeye API, identifies momentum-based entry signals, and executes trades through a Phantom wallet connection. Built with a full paper trading simulation mode to validate logic before any real capital is deployed.
---
Features
Real-time price & volume monitoring — pulls live data from Birdeye API across multiple Solana token pairs
Momentum signal detection — triggers on configurable volume spike + price % change thresholds
Automated stop-loss & take-profit — bot exits positions automatically to protect capital
Paper trading mode — simulates full trade lifecycle with P&L tracking and zero real funds
Trade log — every signal, entry, and exit is written to a structured CSV log
Wallet integration — connects to Phantom wallet via Solana web3 for live execution (Phase 3)
Rug pull protections — contract blocklist, max position size cap, and liquidity checks
---
Tech Stack
Tool	Purpose
Python 3.10+	Core language
`solana-py`	Solana blockchain interaction
`solders`	Solana transaction building
Birdeye API	Real-time Solana token price/volume data
Jupiter Aggregator API	Best-price swap routing
`pandas`	Trade log analysis
`logging`	Structured event logging
---
How It Works
```
Startup
  └── Connect to Solana RPC endpoint
  └── Load watchlist of token addresses
  └── Initialize paper trading ledger

Every 60 seconds
  └── Fetch price + volume for each token (Birdeye API)
  └── Check momentum signal:
      ├── Volume spike > 200% of 10-min average?
      └── Price change > +5% in last 5 minutes?
          └── NO  → continue watching
          └── YES → check rug pull filters
              ├── Token on blocklist? → SKIP
              ├── Liquidity < $10k?   → SKIP
              └── PASS → fire BUY signal
                  ├── [Paper mode] → log simulated buy, track P&L
                  └── [Live mode]  → route swap via Jupiter, sign with Phantom

Position monitoring (every 30 seconds)
  └── Price DOWN 25% → STOP LOSS  → sell
  └── Price UP 50%  → TAKE PROFIT → sell
```
---
Setup
1. Clone the repo
```bash
git clone https://github.com/DSaint96/solana-memecoin-bot.git
cd solana-memecoin-bot
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Configure API keys
Create a `.env` file:
```
BIRDEYE_API_KEY=your_birdeye_api_key
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
WALLET_PRIVATE_KEY=your_phantom_private_key
```
> ⚠️ **Never commit your `.env` file or private key to GitHub.** Add `.env` to your `.gitignore`.
4. Configure trading parameters
Edit `config.py`:
```python
PAPER_TRADING         = True   # Set False for live mode
MAX_POSITION_SIZE_USD = 5.00   # Max $ per trade
STOP_LOSS_PCT         = 0.25   # Exit if down 25%
TAKE_PROFIT_PCT       = 0.50   # Exit if up 50%
VOLUME_SPIKE_MULT     = 2.0    # Volume trigger multiplier
PRICE_CHANGE_MIN_PCT  = 5.0    # Min % move to trigger
```
5. Run the bot
```bash
python memecoin_bot.py
```
---
Sample Trade Log
```
timestamp,token,action,price_usd,amount_usd,pnl_usd,reason
2026-03-14 10:12:05,BONK,BUY,0.00001823,5.00,,momentum signal
2026-03-14 10:38:47,BONK,SELL,0.00002710,7.43,+2.43,take profit hit
2026-03-14 11:05:22,WIF,BUY,2.1840,5.00,,momentum signal
2026-03-14 11:19:08,WIF,SELL,1.6380,3.75,-1.25,stop loss hit
```
---
Project Phases
Phase	Description	Status
Phase 1	Paper trading engine + Birdeye API integration	🔄 In progress
Phase 2	Signal tuning + rug pull filter refinement	🔜 Planned
Phase 3	Live wallet integration + Jupiter swap execution	🔜 Planned
Phase 4	Multi-token monitoring + performance dashboard	🔜 Planned
---
Risk Controls
Control	Value	Purpose
Max position size	$5.00	Caps loss per trade
Stop-loss	−25%	Auto-exits losing trades
Take-profit	+50%	Locks in gains
Liquidity check	> $10,000	Filters low-liquidity tokens
Contract blocklist	Maintained manually	Blocks known scam tokens
Paper mode default	`True`	Prevents accidental live trades
---
Skills Demonstrated
`Python` `Blockchain Development` `Solana Web3` `REST APIs` `Real-Time Data Processing` `Algorithmic Trading Logic` `Risk Management` `Wallet Integration` `pandas` `Environment Variables`
---
Disclaimer
This project is for educational and portfolio purposes only. Memecoin trading carries extreme financial risk. Always run paper trading mode before deploying real funds. This is not financial advice.
---
Built by Dennis Saint — part of an IT/cybersecurity portfolio demonstrating blockchain scripting, API integration, and automated systems design.
