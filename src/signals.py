from config import settings


def check_negative_gamma_breakdown(prev: dict, curr: dict) -> bool:
    """
    Signal 1: NetGEX heavily negative AND spot crosses below the flip line
    (DistanceToFlip% goes from >=0 to <0) since the previous scan.
    """
    if prev is None:
        return False
    if curr["net_gex"] > settings.NETGEX_NEGATIVE_THRESHOLD:
        return False
    prev_dist = prev.get("distance_to_flip_pct")
    curr_dist = curr.get("distance_to_flip_pct")
    if prev_dist is None or curr_dist is None:
        return False
    return prev_dist >= 0 and curr_dist < 0


def check_call_squeeze_breakout(prev: dict, curr: dict) -> bool:
    """
    Signal 2: spot rising, ATM straddle IV rising *with* price (unusual -- normally
    IV falls as price grinds up), and FlipLine shifting up sharply -- all since the
    previous scan. This combination signals dealers short calls being forced to
    chase delta by buying the underlying.
    """
    if prev is None:
        return False
    prev_spot, curr_spot = prev.get("spot"), curr.get("spot")
    prev_iv, curr_iv = prev.get("atm_iv"), curr.get("atm_iv")
    prev_flip, curr_flip = prev.get("flip_line"), curr.get("flip_line")
    if None in (prev_spot, curr_spot, prev_iv, curr_iv, prev_flip, curr_flip):
        return False
    if prev_spot <= 0 or prev_iv <= 0 or prev_flip <= 0:
        return False

    spot_change_pct = ((curr_spot - prev_spot) / prev_spot) * 100
    iv_change_pct = ((curr_iv - prev_iv) / prev_iv) * 100
    flip_change_pct = ((curr_flip - prev_flip) / prev_flip) * 100

    return (
        spot_change_pct >= settings.MIN_SPOT_CHANGE_PCT
        and iv_change_pct >= settings.MIN_IV_CHANGE_PCT
        and flip_change_pct >= settings.MIN_FLIPLINE_SHIFT_PCT
    )
