import datetime as dt
from src.black_scholes import implied_vol, gamma as bs_gamma


def _years_to_expiry(expiry_value):
    """
    Fyers expiryData entries expose the expiry as an epoch timestamp -- but as a
    numeric STRING (e.g. "1785232800"), not an int/float, and not a dd-mm-yyyy
    string. Handle all three shapes defensively since Fyers has been inconsistent
    about this across SDK versions.
    """
    now = dt.datetime.now()

    if isinstance(expiry_value, (int, float)):
        expiry_dt = dt.datetime.fromtimestamp(expiry_value)
    else:
        s = str(expiry_value).strip()
        if s.isdigit():
            expiry_dt = dt.datetime.fromtimestamp(int(s))
        else:
            expiry_dt = dt.datetime.strptime(s, "%d-%m-%Y")

    days = max((expiry_dt - now).total_seconds() / 86400.0, 0.25)  # floor to avoid T=0
    return days / 365.0


def compute_gex(chain_data: dict, spot: float, risk_free_rate: float, lot_size: int = 1):
    """
    Returns dict with:
      net_gex, flip_line, distance_to_flip_pct, atm_iv, per_strike (for debugging)
    Returns None if not enough usable data (e.g. all quotes illiquid/stale).
    """
    options = [
        row for row in chain_data.get("optionsChain", [])
        if row.get("option_type") in ("CE", "PE") and row.get("strike_price")
    ]
    if not options:
        return None

    expiry_list = chain_data.get("expiryData", [])
    if expiry_list:
        T = _years_to_expiry(expiry_list[0].get("expiry", expiry_list[0].get("date")))
    else:
        T = 7 / 365.0  # fallback: assume ~weekly expiry if Fyers omits expiryData

    strikes = {}
    for row in options:
        K = float(row["strike_price"])
        ltp = float(row.get("ltp") or 0)
        oi = float(row.get("oi") or 0)
        opt_type = row["option_type"]

        iv = implied_vol(ltp, spot, K, T, risk_free_rate, opt_type)
        if iv is None:
            continue
        g = bs_gamma(spot, K, T, risk_free_rate, iv)

        strikes.setdefault(K, {"CE": None, "PE": None})
        strikes[K][opt_type] = {"oi": oi, "iv": iv, "gamma": g}

    if not strikes:
        return None

    # --- Per-strike net GEX (standard dealer-positioning convention:
    #     dealers assumed net long call gamma, net short put gamma) ---
    per_strike_gex = {}
    for K, sides in strikes.items():
        call_gex = 0.0
        put_gex = 0.0
        if sides["CE"]:
            call_gex = sides["CE"]["gamma"] * sides["CE"]["oi"] * lot_size * (spot ** 2) * 0.01
        if sides["PE"]:
            put_gex = -1 * sides["PE"]["gamma"] * sides["PE"]["oi"] * lot_size * (spot ** 2) * 0.01
        per_strike_gex[K] = call_gex + put_gex

    net_gex = sum(per_strike_gex.values())

    # --- Flip line: strike where cumulative GEX (sorted by strike) crosses zero ---
    sorted_strikes = sorted(per_strike_gex.keys())
    cumulative = 0.0
    flip_line = sorted_strikes[0]
    prev_strike, prev_cum = sorted_strikes[0], 0.0
    for K in sorted_strikes:
        cumulative += per_strike_gex[K]
        if prev_cum < 0 <= cumulative or prev_cum > 0 >= cumulative:
            # linear interpolate between prev_strike and K for the zero-cross point
            if cumulative != prev_cum:
                frac = (0 - prev_cum) / (cumulative - prev_cum)
                flip_line = prev_strike + frac * (K - prev_strike)
            else:
                flip_line = K
            break
        prev_strike, prev_cum = K, cumulative
    else:
        flip_line = sorted_strikes[len(sorted_strikes) // 2]  # no crossing found, fallback to mid strike

    distance_to_flip_pct = ((spot - flip_line) / flip_line) * 100 if flip_line else None

    # --- ATM straddle IV (average of nearest-strike CE and PE IV) ---
    atm_strike = min(strikes.keys(), key=lambda k: abs(k - spot))
    atm_ivs = []
    if strikes[atm_strike]["CE"]:
        atm_ivs.append(strikes[atm_strike]["CE"]["iv"])
    if strikes[atm_strike]["PE"]:
        atm_ivs.append(strikes[atm_strike]["PE"]["iv"])
    atm_iv = sum(atm_ivs) / len(atm_ivs) if atm_ivs else None

    return {
        "net_gex": net_gex,
        "flip_line": flip_line,
        "distance_to_flip_pct": distance_to_flip_pct,
        "atm_iv": atm_iv,
        "spot": spot,
    }
