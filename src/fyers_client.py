import os
import time
from fyers_apiv3 import fyersModel


class FyersClient:
    def __init__(self):
        client_id = os.environ.get("FYERS_CLIENT_ID")
        access_token = os.environ.get("FYERS_ACCESS_TOKEN")
        if not client_id or not access_token:
            raise RuntimeError(
                "FYERS_CLIENT_ID / FYERS_ACCESS_TOKEN not found in environment. "
                "Check GitHub Actions secrets are wired into the workflow env block."
            )
        self.fyers = fyersModel.FyersModel(
            client_id=client_id,
            token=access_token,
            is_async=False,
            log_path="",
        )

    def get_spot(self, equity_symbol: str):
        resp = self.fyers.quotes({"symbols": equity_symbol})
        if resp.get("s") != "ok" or not resp.get("d"):
            raise RuntimeError(f"Quote fetch failed for {equity_symbol}: {resp}")
        v = resp["d"][0].get("v", {})
        lp = v.get("lp")
        if lp is None:
            raise RuntimeError(
                f"Quote for {equity_symbol} missing 'lp' field. "
                f"Full response: {resp}"
            )
        return float(lp)

    def get_option_chain(self, equity_symbol: str, strike_count: int):
        resp = self.fyers.optionchain(
            data={"symbol": equity_symbol, "strikecount": strike_count, "timestamp": ""}
        )
        if resp.get("s") != "ok" or "data" not in resp:
            raise RuntimeError(f"Option chain fetch failed for {equity_symbol}: {resp}")
        return resp["data"]

    def sleep(self, seconds):
        time.sleep(seconds)
