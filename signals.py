# signals.py
# ─────────────────────────────────────────────────────────────────────────────
# Decides whether a token has a strong enough momentum signal to buy.
#
# A BUY signal fires when BOTH conditions are true:
#   1. Volume spike  - current volume is 2x+ the rolling average
#   2. Price move    - price has risen 5%+ in the last 5 minutes
#                      (DexScreener gives us this directly for free!)
#
# Two conditions filter out noise. A price spike with no volume is often
# a fluke or a manipulation. We want BOTH confirming at the same time.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from collections import deque
from config import (
    VOLUME_SPIKE_MULTIPLIER,
    PRICE_CHANGE_MIN_PCT,
    ROLLING_WINDOW,
    MIN_LIQUIDITY_USD,
)

log = logging.getLogger(__name__)

# Add any known scam token addresses here — bot will never trade them
BLOCKLIST = {}


class SignalEngine:
    """
    Tracks price and volume history for each token and detects momentum signals.
    """

    def __init__(self):
        self.price_history:  dict[str, deque] = {}
        self.volume_history: dict[str, deque] = {}

    def _init_token(self, symbol: str):
        if symbol not in self.price_history:
            self.price_history[symbol]  = deque(maxlen=ROLLING_WINDOW)
            self.volume_history[symbol] = deque(maxlen=ROLLING_WINDOW)

    def update(self, symbol: str, price: float, volume: float):
        """Add the latest price and volume to this token's history."""
        self._init_token(symbol)
        self.price_history[symbol].append(price)
        self.volume_history[symbol].append(volume)

    def check_signal(
        self,
        symbol:    str,
        address:   str,
        price:     float,
        volume:    float,
        change_5m: float = 0.0,   # 5-min price change % from DexScreener
    ) -> bool:
        """
        Evaluate whether this token has a buy signal right now.

        Args:
            symbol:    Token name e.g. "BONK"
            address:   Contract address (for blocklist check)
            price:     Current price in USD
            volume:    24hr volume in USD
            change_5m: Price change % over last 5 minutes (from DexScreener)

        Returns:
            True  -> BUY signal detected
            False -> No signal, keep watching
        """

        # Safety check 1: blocklist
        if address in BLOCKLIST:
            log.warning(f"{symbol} is on the blocklist - skipping")
            return False

        # Safety check 2: minimum liquidity
        if volume < MIN_LIQUIDITY_USD:
            log.info(f"{symbol} liquidity too low (${volume:,.0f}) - skipping")
            return False

        # Need at least 2 data points before calculating averages
        self._init_token(symbol)
        if len(self.volume_history[symbol]) < 2:
            log.info(f"{symbol} - building history ({len(self.volume_history[symbol])}/{ROLLING_WINDOW})")
            return False

        # Condition 1: Volume spike
        avg_volume     = sum(self.volume_history[symbol]) / len(self.volume_history[symbol])
        volume_spiked  = volume >= (avg_volume * VOLUME_SPIKE_MULTIPLIER)

        if volume_spiked:
            log.info(f"{symbol} VOLUME SPIKE: ${volume:,.0f} vs avg ${avg_volume:,.0f} ({volume/avg_volume:.1f}x)")
        else:
            log.info(f"{symbol} volume normal: ${volume:,.0f} vs avg ${avg_volume:,.0f}")

        # Condition 2: Price momentum (using DexScreener's 5-min change directly)
        # This is more accurate than calculating it ourselves
        price_moving = change_5m >= PRICE_CHANGE_MIN_PCT

        if price_moving:
            log.info(f"{symbol} PRICE MOMENTUM: +{change_5m:.2f}% in last 5 min")
        else:
            log.info(f"{symbol} price change 5m: {change_5m:+.2f}% (need +{PRICE_CHANGE_MIN_PCT}%)")

        # Both must be true
        if volume_spiked and price_moving:
            log.info(f"*** BUY SIGNAL: {symbol} - volume + price momentum confirmed ***")
            return True

        return False
