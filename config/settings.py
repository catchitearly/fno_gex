"""Tunable parameters. Adjust freely without touching scanner logic."""

# --- Market hours (IST) ---
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"

# --- Option chain fetch ---
STRIKE_COUNT = 20          # strikes on each side of ATM to pull from Fyers
RISK_FREE_RATE = 0.065     # ~ India 91-day T-bill approx, used in BS IV/gamma calc
EXPIRY_INDEX = 0           # 0 = nearest expiry returned by Fyers option chain

# --- Signal 1: Negative Gamma Breakdown ---
NETGEX_NEGATIVE_THRESHOLD = -5e6   # NetGEX must be below this (heavily negative) to qualify
# fires when DistanceToFlip% crosses from >=0 to <0 AND NetGEX <= NETGEX_NEGATIVE_THRESHOLD

# --- Signal 2: Call-Squeeze Breakout ---
MIN_SPOT_CHANGE_PCT = 0.15     # spot must have risen at least this % since last scan
MIN_IV_CHANGE_PCT = 2.0        # ATM straddle IV must have risen at least this % (relative)
MIN_FLIPLINE_SHIFT_PCT = 0.5   # FlipLine must have shifted up at least this % since last scan

# --- Misc ---
REQUEST_SLEEP_SECONDS = 0.35   # pause between symbols to respect Fyers rate limits
STATE_FILE = "state/last_scan.json"
