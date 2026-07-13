import sys
import datetime as dt
import pytz

from config.symbols import SYMBOLS
from config import settings
from src.fyers_client import FyersClient
from src.gex_engine import compute_gex
from src.state_store import load_state, save_state
from src.telegram import send_telegram
from src.signals import check_negative_gamma_breakdown, check_call_squeeze_breakout


def is_market_open_now() -> bool:
    ist = pytz.timezone("Asia/Kolkata")
    now = dt.datetime.now(ist)
    if now.weekday() >= 5:  # Sat/Sun
        return False
    open_t = dt.datetime.strptime(settings.MARKET_OPEN, "%H:%M").time()
    close_t = dt.datetime.strptime(settings.MARKET_CLOSE, "%H:%M").time()
    return open_t <= now.time() <= close_t


def format_signal1_message(sym_name, curr):
    return (
        f"⚡ *Negative Gamma Breakdown — {sym_name}*\n"
        f"Spot: {curr['spot']:.2f}\n"
        f"NetGEX: {curr['net_gex']:,.0f}\n"
        f"FlipLine: {curr['flip_line']:.2f}\n"
        f"DistanceToFlip: {curr['distance_to_flip_pct']:.2f}%\n"
        f"→ Dealers likely short-hedging into weakness. Consider NTM puts / bear put spread."
    )


def format_signal2_message(sym_name, prev, curr):
    return (
        f"🚀 *Call-Squeeze Breakout — {sym_name}*\n"
        f"Spot: {prev['spot']:.2f} → {curr['spot']:.2f}\n"
        f"ATM IV: {prev['atm_iv']*100:.1f}% → {curr['atm_iv']*100:.1f}%\n"
        f"FlipLine: {prev['flip_line']:.2f} → {curr['flip_line']:.2f}\n"
        f"→ Dealers likely short-gamma on calls, forced to chase delta. Consider bull call spread / long futures with trailing stop."
    )


def main():
    if not is_market_open_now():
        print("Market closed — skipping scan.")
        return 0

    fyers = FyersClient()
    state = load_state(settings.STATE_FILE)
    new_state = {}
    fired_any = False

    for sym in SYMBOLS:
        name = sym["name"]
        equity_symbol = sym["equity_symbol"]
        lot_size = sym["lot_size"]
        try:
            spot = fyers.get_spot(equity_symbol)
            chain = fyers.get_option_chain(equity_symbol, settings.STRIKE_COUNT)
            result = compute_gex(chain, spot, settings.RISK_FREE_RATE, lot_size)
            if result is None:
                print(f"[{name}] insufficient option data, skipping")
                fyers.sleep(settings.REQUEST_SLEEP_SECONDS)
                continue

            prev = state.get(name)

            if check_negative_gamma_breakdown(prev, result):
                send_telegram(format_signal1_message(name, result))
                fired_any = True
                print(f"[{name}] SIGNAL 1 fired")

            if prev and check_call_squeeze_breakout(prev, result):
                send_telegram(format_signal2_message(name, prev, result))
                fired_any = True
                print(f"[{name}] SIGNAL 2 fired")

            new_state[name] = result
            print(f"[{name}] spot={spot:.2f} netgex={result['net_gex']:,.0f} "
                  f"flip={result['flip_line']:.2f} dist={result['distance_to_flip_pct']:.2f}%")

        except Exception as e:
            print(f"[{name}] ERROR: {e}", file=sys.stderr)
            # keep previous state for this symbol so a transient API failure
            # doesn't wipe out the comparison baseline
            if name in state:
                new_state[name] = state[name]

        fyers.sleep(settings.REQUEST_SLEEP_SECONDS)

    save_state(settings.STATE_FILE, new_state)
    print(f"Scan complete. Signals fired: {fired_any}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
