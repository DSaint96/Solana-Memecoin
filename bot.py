# bot.py
# ─────────────────────────────────────────────────────────────────────────────
# The main entry point. Run this file to start the bot.
#
# What happens when you run this:
#   1. Bot logs start message and initializes everything
#   2. Every 60 seconds (configurable in config.py):
#      a. Fetch live price + volume for every token in WATCHLIST
#      b. Feed data into the signal engine (updates history)
#      c. Check if any open positions hit stop-loss or take-profit
#      d. Check if any token has a buy signal
#      e. If buy signal -> simulate a paper trade
#   3. Prints a wallet summary every 10 cycles
#   4. Runs until you press Ctrl+C
# ─────────────────────────────────────────────────────────────────────────────

import time
import logging
from datetime import datetime

from config       import WATCHLIST, CHECK_INTERVAL_SECONDS, PAPER_TRADING, APP_LOG_FILE
from dexscreener  import get_all_tokens
from signals      import SignalEngine
from paper_trader import PaperTrader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(APP_LOG_FILE),
    ]
)
log = logging.getLogger(__name__)


def main():
    log.info("=" * 60)
    log.info("  SOLANA MEMECOIN BOT - Phase 1 (Paper Trading)")
    log.info("  Data source: DexScreener (free, no API key needed)")
    log.info(f"  Mode:     {'PAPER TRADING' if PAPER_TRADING else 'LIVE WARNING'}")
    log.info(f"  Tokens:   {', '.join(WATCHLIST.keys())}")
    log.info(f"  Interval: every {CHECK_INTERVAL_SECONDS}s")
    log.info(f"  Started:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    engine = SignalEngine()
    trader = PaperTrader()
    cycle  = 0

    while True:
        cycle += 1
        log.info(f"\n---- Cycle #{cycle} | {datetime.now().strftime('%H:%M:%S')} ----")

        # Step 1: Fetch live data from DexScreener
        token_data = get_all_tokens(WATCHLIST)

        if not token_data:
            log.warning("No token data returned - check internet connection")
            time.sleep(CHECK_INTERVAL_SECONDS)
            continue

        # Step 2: Process each token
        for symbol, data in token_data.items():
            price     = data["price"]
            volume    = data["volume"]
            address   = data["address"]
            change_5m = data.get("change_5m", 0)

            # Update signal engine history
            engine.update(symbol, price, volume)

            # Check if open position needs to exit
            trader.check_exits(symbol, price)

            # Check for buy signal if not already holding
            if symbol not in trader.positions:
                signal = engine.check_signal(symbol, address, price, volume, change_5m)
                if signal:
                    if PAPER_TRADING:
                        trader.buy(symbol, price)
                    else:
                        log.warning("Live trading not yet implemented - set PAPER_TRADING=True")

        # Step 3: Print summary every 10 cycles
        if cycle % 10 == 0:
            trader.print_summary()

        log.info(f"Sleeping {CHECK_INTERVAL_SECONDS}s until next cycle...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("\nBot stopped (Ctrl+C). Check trades.csv for your log.")
