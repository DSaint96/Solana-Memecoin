# config.py
# ─────────────────────────────────────────────────────────────────────────────
# All settings live here. Change values in this file, never in the other files.
# ─────────────────────────────────────────────────────────────────────────────


# ── API ───────────────────────────────────────────────────────────────────────
# Get your free Birdeye API key at: https://birdeye.so/
# Paste it below OR set it as an environment variable: BIRDEYE_API_KEY=your_key
# No API key needed - DexScreener is free!

# ── Mode ──────────────────────────────────────────────────────────────────────
# PAPER_TRADING = True  → simulate trades, no real money ever moves
# PAPER_TRADING = False → live mode (Phase 3 only, wallet required)
PAPER_TRADING = True

# ── Starting balance (paper trading only) ────────────────────────────────────
STARTING_BALANCE_USD = 25.00

# ── Position sizing ───────────────────────────────────────────────────────────
# Maximum dollars to spend on a single trade
MAX_POSITION_USD = 5.00

# ── Exit logic ────────────────────────────────────────────────────────────────
# Bot auto-sells if price drops this far below your entry (e.g. 0.25 = 25%)
STOP_LOSS_PCT = 0.25

# Bot auto-sells if price rises this far above your entry (e.g. 0.50 = 50%)
TAKE_PROFIT_PCT = 0.50

# ── Signal thresholds ─────────────────────────────────────────────────────────
# How many times bigger than the rolling average must volume be to trigger?
# 2.0 means "volume must be 2x the average to count as a spike"
VOLUME_SPIKE_MULTIPLIER = 2.0

# Minimum price % change in the last 5 minutes to confirm a momentum signal
# 5.0 means the token must have moved up at least 5% in 5 minutes
PRICE_CHANGE_MIN_PCT = 5.0

# ── Rug pull filters ──────────────────────────────────────────────────────────
# Skip any token with less than this much liquidity (in USD)
MIN_LIQUIDITY_USD = 10_000

# ── Tokens to watch ───────────────────────────────────────────────────────────
# These are real Solana token addresses for popular memecoins.
# You can add or remove any token address here.
WATCHLIST = {
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF":  "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "MEW":  "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5",
}

# ── Timing ────────────────────────────────────────────────────────────────────
# How often the bot checks prices (in seconds)
CHECK_INTERVAL_SECONDS = 60

# How many recent data points to use when calculating average volume
ROLLING_WINDOW = 10

# ── Logging ───────────────────────────────────────────────────────────────────
# Trade log file — every simulated buy/sell gets written here
TRADE_LOG_FILE = "trades.csv"

# App log file — every bot event, error, and signal gets logged here
APP_LOG_FILE = "bot.log"
