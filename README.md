# NSE F&O GEX Screener (Fyers + GitHub Actions)

Scans your top-50 F&O universe every 15 minutes during market hours, computes
NetGEX / FlipLine / DistanceToFlip% / ATM straddle IV from the Fyers option
chain, and pushes Telegram alerts for two signals:

1. **⚡ Negative Gamma Breakdown** — NetGEX deeply negative + spot crosses below FlipLine
2. **🚀 Call-Squeeze Breakout** — spot rising + ATM IV rising with it + FlipLine shifting up sharply

This is an **alert-only** screener. It does not place any orders.

## Why IV/Gamma are computed, not fetched

Fyers' option chain API returns OI, LTP, volume — but **not IV or Greeks**
(confirmed gap on their own community forum). This scanner backs out implied
vol from each strike's LTP via Black-Scholes (`src/black_scholes.py`), then
derives gamma from that IV. This is standard for any GEX tool built on a feed
without native Greeks.

## Setup

### 1. Secrets already in place
You've said `FYERS_CLIENT_ID` and `FYERS_ACCESS_TOKEN` are already in
GitHub Actions secrets — the workflow reads them directly.

**Important caveat on `FYERS_ACCESS_TOKEN`:** Fyers access tokens expire
**daily** (they're valid until ~end of day IST regardless of when generated).
A secret you set manually will go stale and every scan will start failing
after the next login cycle. You have two options:
- **Manual (works today, needs daily upkeep):** re-generate the access token
  each morning and update the GitHub secret before market open.
- **Automated (recommended, no daily upkeep):** add a small refresh step
  using Fyers' TOTP-based `validate-refresh-token` endpoint at the start of
  the workflow, fed by `FYERS_APP_ID`, `FYERS_SECRET_ID`, `FYERS_PIN`, and a
  `FYERS_REFRESH_TOKEN` (refresh tokens last ~15 days). Say the word and I'll
  add this step — it removes the daily-expiry problem entirely.

### 2. Add Telegram secrets
- Message [@BotFather](https://t.me/BotFather) on Telegram → `/newbot` → copy the bot token → `TELEGRAM_BOT_TOKEN`
- Message your new bot once, then hit `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat.id` → `TELEGRAM_CHAT_ID`
- Add both as repo secrets: **Settings → Secrets and variables → Actions → New repository secret**

### 3. Push this repo to GitHub
The workflow at `.github/workflows/scanner.yml` runs automatically every 15
minutes, 9:15–15:30 IST, Mon–Fri. You can also trigger a manual run from the
**Actions** tab (`workflow_dispatch`).

### 4. Verify the symbol list
`config/symbols.py` has ~50 large/liquid F&O names as a starting point —
**verify against NSE's current F&O list and update lot sizes**, since NSE
revises the eligible list and lot sizes periodically (roughly every 6 months
/ every expiry cycle respectively). Wrong lot sizes won't break the scanner
but will skew NetGEX magnitude.

## Tuning
All thresholds live in `config/settings.py` — NetGEX threshold, IV/spot/flip-shift
percentages for Signal 2, strike count pulled per symbol, risk-free rate, etc.
Nothing in `scanner.py` should need editing to tune sensitivity.

## State persistence
Since GitHub Actions runners are stateless, each run's results are saved to
`state/last_scan.json` and **committed back to the repo** by the workflow
(needs `permissions: contents: write`, already set). This is what lets the
scanner detect *crossings* and *changes since last scan* rather than just
absolute levels.

## Known limitations / things to sanity-check before trusting signals
- IV is derived, not exchange-quoted — for very illiquid strikes (wide
  bid-ask, stale LTP) the solver may return `None` and that strike is
  skipped; this can slightly distort NetGEX on thin names.
- The dealer-positioning convention (long call gamma / short put gamma) is
  the common retail approximation used by most public GEX tools — it is
  *not* verified against actual dealer books, since no vendor publishes that.
- First scan of the day has no `prev` state to compare against, so no
  crossing/change signals can fire on the very first run after market open.
- Cron schedule fires a few extra times right at the UTC-hour boundary due to
  cron granularity vs IST offset; `scanner.py` exits immediately outside
  market hours so this just costs a few no-op Action minutes, not false signals.
