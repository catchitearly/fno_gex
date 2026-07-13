"""
Fyers' option chain API does not return IV or Greeks (confirmed gap, see
Fyers community forum). We back out implied vol from the traded LTP using
Black-Scholes, then compute gamma from that IV. This is standard practice
for any GEX screener built on a broker feed that lacks native Greeks.
"""

import math
from scipy.stats import norm
from scipy.optimize import brentq


def _bs_price(S, K, T, r, sigma, option_type):
    if sigma <= 0 or T <= 0:
        return max(0.0, (S - K) if option_type == "CE" else (K - S))
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "CE":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def implied_vol(price, S, K, T, r, option_type, lo=0.001, hi=5.0):
    """
    Solve for sigma such that BS price == market LTP.
    Returns None if no solution found (illiquid/bad quote) so caller can skip it.
    """
    if price <= 0 or S <= 0 or K <= 0 or T <= 0:
        return None

    intrinsic = max(0.0, (S - K) if option_type == "CE" else (K - S))
    if price < intrinsic:
        return None  # bad/stale quote, below intrinsic value

    try:
        f = lambda sigma: _bs_price(S, K, T, r, sigma, option_type) - price
        if f(lo) * f(hi) > 0:
            return None
        return brentq(f, lo, hi, maxiter=100, xtol=1e-6)
    except Exception:
        return None


def gamma(S, K, T, r, sigma):
    """Black-Scholes gamma (same formula for calls and puts)."""
    if sigma <= 0 or T <= 0 or S <= 0 or K <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    return norm.pdf(d1) / (S * sigma * math.sqrt(T))
