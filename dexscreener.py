# dexscreener.py
# ─────────────────────────────────────────────────────────────────────────────
# Fetches live price and volume data from DexScreener.
#
# DexScreener is 100% FREE — no API key, no account, no credit card.
# It tracks every token trading on Solana DEXes in real time.
#
# Replaces birdeye.py — everything else (signals.py, paper_trader.py, bot.py)
# stays exactly the same.
# ─────────────────────────────────────────────────────────────────────────────

import requests
import logging

log = logging.getLogger(__name__)

DEXSCREENER_BASE_URL = "https://api.dexscreener.com/latest/dex/tokens"


def get_token_data(token_address: str) -> dict | None:
    """
    Fetch the latest price and volume for a single Solana token.

    Args:
        token_address: The token's contract address on Solana

    Returns:
        A dictionary like:
        {
            "address":   "DezXAZ8z...",
            "price":     0.00001823,    ← current price in USD
            "volume":    1_450_000.0,   ← 24hr trading volume in USD
            "liquidity": 85_000.0,      ← liquidity in USD (bonus vs Birdeye)
            "change_5m": 6.2,           ← % price change last 5 min (bonus)
            "change_1h": 12.4,          ← % price change last 1 hour (bonus)
        }
        Returns None if the request fails for any reason.
    """

    url = f"{DEXSCREENER_BASE_URL}/{token_address}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # DexScreener returns a list of trading pairs for this token
        # A token can trade on multiple DEXes — we want the one with
        # the most liquidity (first result is usually the best pair)
        pairs = data.get("pairs", [])

        if not pairs:
            log.warning(f"No trading pairs found for {token_address}")
            return None

        # Filter to Solana pairs only, sort by liquidity descending
        solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]

        if not solana_pairs:
            log.warning(f"No Solana pairs found for {token_address}")
            return None

        # Pick the pair with the highest liquidity
        best_pair = max(
            solana_pairs,
            key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0)
        )

        # Pull the values we need out of the pair data
        price_usd  = float(best_pair.get("priceUsd", 0) or 0)
        volume_24h = float(best_pair.get("volume", {}).get("h24", 0) or 0)
        liquidity  = float(best_pair.get("liquidity", {}).get("usd", 0) or 0)

        # Price change percentages (bonus data — Birdeye didn't give us this free)
        price_change = best_pair.get("priceChange", {})
        change_5m  = float(price_change.get("m5",  0) or 0)
        change_1h  = float(price_change.get("h1",  0) or 0)
        change_24h = float(price_change.get("h24", 0) or 0)

        if price_usd == 0:
            log.warning(f"Price is zero for {token_address} — token may be inactive")
            return None

        return {
            "address":   token_address,
            "price":     price_usd,
            "volume":    volume_24h,
            "liquidity": liquidity,
            "change_5m": change_5m,
            "change_1h": change_1h,
            "change_24h": change_24h,
        }

    except requests.exceptions.Timeout:
        log.error(f"DexScreener request timed out for {token_address}")
        return None

    except requests.exceptions.ConnectionError:
        log.error("No internet connection — could not reach DexScreener")
        return None

    except requests.exceptions.HTTPError as e:
        log.error(f"DexScreener HTTP error for {token_address}: {e}")
        return None

    except Exception as e:
        log.error(f"Unexpected error fetching {token_address}: {e}")
        return None


def get_all_tokens(watchlist: dict) -> dict:
    """
    Fetch price and volume data for every token in the watchlist.

    Args:
        watchlist: The WATCHLIST dict from config.py
                   e.g. {"BONK": "DezXAZ8z...", "WIF": "EKpQGSJ..."}

    Returns:
        A dictionary keyed by token symbol with full market data.
        Tokens that failed to fetch are left out.
    """
    results = {}

    for symbol, address in watchlist.items():
        log.info(f"Fetching {symbol} from DexScreener...")
        data = get_token_data(address)

        if data:
            results[symbol] = data
            log.info(
                f"  {symbol}: ${data['price']:.8f} | "
                f"vol ${data['volume']:,.0f} | "
                f"liq ${data['liquidity']:,.0f} | "
                f"5m {data['change_5m']:+.1f}%"
            )
        else:
            log.warning(f"  {symbol}: SKIPPED — no data returned")

    return results
