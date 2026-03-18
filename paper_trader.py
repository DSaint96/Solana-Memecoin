# paper_trader.py
# ─────────────────────────────────────────────────────────────────────────────
# Simulates buying and selling tokens without using real money.
#
# What this file does:
#   - Tracks your fake "wallet" balance
#   - Records every simulated buy and sell to a CSV log file
#   - Checks open positions every loop to see if stop-loss or take-profit hit
#   - Prints a P&L summary whenever you ask for it
# ─────────────────────────────────────────────────────────────────────────────

import csv
import logging
from datetime import datetime
from config import (
    STARTING_BALANCE_USD,
    MAX_POSITION_USD,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
    TRADE_LOG_FILE,
)

log = logging.getLogger(__name__)


class PaperTrader:
    """
    Simulates a trading wallet.

    Tracks:
        balance      → how much USD we have left to spend
        positions    → tokens we currently "own" (open trades)
        trade_log    → every completed trade written to CSV
    """

    def __init__(self):
        self.balance:   float = STARTING_BALANCE_USD
        self.positions: dict  = {}   # { "BONK": { entry_price, amount_usd, quantity } }
        self.total_pnl: float = 0.0  # Running total profit / loss

        # Create the CSV log file with headers if it doesn't exist yet
        self._init_log()

        log.info(f"Paper trader ready. Starting balance: ${self.balance:.2f}")

    def _init_log(self):
        """Create the CSV trade log file with column headers."""
        try:
            with open(TRADE_LOG_FILE, "x", newline="") as f:   # "x" = create, fail if exists
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "symbol", "action",
                    "price_usd", "quantity", "amount_usd",
                    "pnl_usd", "reason", "balance_after"
                ])
        except FileExistsError:
            pass  # File already exists from a previous run — that's fine

    def _write_trade(self, symbol, action, price, quantity, amount_usd, pnl_usd, reason):
        """Append one completed trade to the CSV log."""
        with open(TRADE_LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                action,
                f"{price:.8f}",
                f"{quantity:.4f}",
                f"{amount_usd:.2f}",
                f"{pnl_usd:.2f}" if pnl_usd is not None else "",
                reason,
                f"{self.balance:.2f}",
            ])

    def buy(self, symbol: str, price: float) -> bool:
        """
        Simulate buying a token.

        Args:
            symbol: Token name, e.g. "BONK"
            price:  Current price per token in USD

        Returns:
            True if the buy was executed, False if we couldn't afford it
            or already hold this token.
        """

        # Don't buy if we already have a position in this token
        if symbol in self.positions:
            log.info(f"Already holding {symbol} — skipping buy")
            return False

        # Don't buy if we can't afford the minimum position size
        spend = min(MAX_POSITION_USD, self.balance)
        if spend <= 0:
            log.warning("Balance too low to buy anything")
            return False

        # Calculate how many tokens we get for our money
        # e.g. spend $5, BONK costs $0.00001823 → we get 274,273 BONK
        quantity = spend / price

        # Deduct from our paper balance
        self.balance -= spend

        # Record the open position
        self.positions[symbol] = {
            "entry_price": price,
            "quantity":    quantity,
            "amount_usd":  spend,
        }

        # Log it
        self._write_trade(symbol, "BUY", price, quantity, spend, None, "momentum signal")
        log.info(f"[PAPER BUY]  {symbol} | {quantity:.4f} tokens @ ${price:.8f} | spent ${spend:.2f} | balance ${self.balance:.2f}")
        return True

    def check_exits(self, symbol: str, current_price: float):
        """
        Check if an open position should be closed (sold).

        Called every loop for each token we currently hold.
        Sells automatically if stop-loss or take-profit threshold is hit.

        Args:
            symbol:        Token name
            current_price: Latest price fetched from Birdeye
        """

        # If we don't hold this token, nothing to check
        if symbol not in self.positions:
            return

        pos = self.positions[symbol]
        entry_price = pos["entry_price"]

        # How much has the price changed since we bought?
        # Positive = profit, Negative = loss
        price_change = (current_price - entry_price) / entry_price

        log.info(f"{symbol} position check | entry ${entry_price:.8f} | now ${current_price:.8f} | change {price_change*100:+.2f}%")

        # ── Stop-loss: sell if we're down too much ─────────────────────────
        if price_change <= -STOP_LOSS_PCT:
            self._sell(symbol, current_price, "stop loss hit")

        # ── Take-profit: sell if we're up enough ───────────────────────────
        elif price_change >= TAKE_PROFIT_PCT:
            self._sell(symbol, current_price, "take profit hit")

    def _sell(self, symbol: str, current_price: float, reason: str):
        """
        Close a position and calculate profit or loss.

        Args:
            symbol:        Token to sell
            current_price: Price at the time of exit
            reason:        Why we're selling ("stop loss hit" or "take profit hit")
        """

        pos = self.positions.pop(symbol)  # Remove from open positions

        # Calculate what our tokens are worth now
        current_value = pos["quantity"] * current_price

        # P&L = what we got out minus what we put in
        pnl = current_value - pos["amount_usd"]

        # Add proceeds back to our paper balance
        self.balance += current_value
        self.total_pnl += pnl

        # Log it
        self._write_trade(symbol, "SELL", current_price, pos["quantity"], current_value, pnl, reason)

        emoji = "+" if pnl >= 0 else ""
        log.info(f"[PAPER SELL] {symbol} | {reason} | P&L ${emoji}{pnl:.2f} | balance ${self.balance:.2f}")

    def print_summary(self):
        """Print a quick summary of the paper wallet to the console."""
        open_positions = len(self.positions)
        log.info("─" * 50)
        log.info(f"  PAPER WALLET SUMMARY")
        log.info(f"  Balance:        ${self.balance:.2f}")
        log.info(f"  Open positions: {open_positions}")
        log.info(f"  Total P&L:      ${self.total_pnl:+.2f}")
        log.info("─" * 50)

        if self.positions:
            log.info("  Open positions:")
            for sym, pos in self.positions.items():
                log.info(f"    {sym}: {pos['quantity']:.4f} tokens @ ${pos['entry_price']:.8f} (${pos['amount_usd']:.2f} in)")
