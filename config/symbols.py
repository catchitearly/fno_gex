"""
Universe of NSE F&O stocks to scan.

IMPORTANT: NSE reviews the F&O eligible list periodically and lot sizes change
almost every expiry cycle (SEBI mandates lot-size revisions based on price).
The list below is a starting set of ~50 large/liquid F&O names. You MUST:
  1. Verify this list against the current NSE F&O list before relying on it.
  2. Update `lot_size` values each time NSE revises them
     (check: https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities
      -> NSE_FO_contract_ddmmyyyy.csv.gz)

`equity_symbol`  -> Fyers symbol for the underlying (used to fetch option chain + spot)
`lot_size`       -> current F&O lot size (used to weight GEX by contract size)
"""

SYMBOLS = [
    {"name": "RELIANCE",    "equity_symbol": "NSE:RELIANCE-EQ",    "lot_size": 500},
    {"name": "HDFCBANK",    "equity_symbol": "NSE:HDFCBANK-EQ",    "lot_size": 550},
    {"name": "ICICIBANK",   "equity_symbol": "NSE:ICICIBANK-EQ",   "lot_size": 700},
    {"name": "INFY",        "equity_symbol": "NSE:INFY-EQ",        "lot_size": 400},
    {"name": "TCS",         "equity_symbol": "NSE:TCS-EQ",         "lot_size": 150},
    {"name": "AXISBANK",    "equity_symbol": "NSE:AXISBANK-EQ",    "lot_size": 625},
    {"name": "SBIN",        "equity_symbol": "NSE:SBIN-EQ",        "lot_size": 750},
    {"name": "KOTAKBANK",   "equity_symbol": "NSE:KOTAKBANK-EQ",   "lot_size": 400},
    {"name": "BAJFINANCE",  "equity_symbol": "NSE:BAJFINANCE-EQ",  "lot_size": 125},
    {"name": "BHARTIARTL",  "equity_symbol": "NSE:BHARTIARTL-EQ",  "lot_size": 475},
    {"name": "LT",          "equity_symbol": "NSE:LT-EQ",          "lot_size": 300},
    {"name": "ITC",         "equity_symbol": "NSE:ITC-EQ",         "lot_size": 1600},
    {"name": "HINDUNILVR",  "equity_symbol": "NSE:HINDUNILVR-EQ",  "lot_size": 300},
    {"name": "MARUTI",      "equity_symbol": "NSE:MARUTI-EQ",      "lot_size": 50},
    {"name": "M&M",         "equity_symbol": "NSE:M&M-EQ",         "lot_size": 350},
    {"name": "SUNPHARMA",   "equity_symbol": "NSE:SUNPHARMA-EQ",   "lot_size": 350},
   
    {"name": "TATASTEEL",   "equity_symbol": "NSE:TATASTEEL-EQ",   "lot_size": 4250},
    {"name": "ADANIENT",    "equity_symbol": "NSE:ADANIENT-EQ",    "lot_size": 300},
    {"name": "ADANIPORTS",  "equity_symbol": "NSE:ADANIPORTS-EQ",  "lot_size": 500},
    {"name": "ULTRACEMCO",  "equity_symbol": "NSE:ULTRACEMCO-EQ",  "lot_size": 50},
    {"name": "TITAN",       "equity_symbol": "NSE:TITAN-EQ",       "lot_size": 200},
    {"name": "ASIANPAINT",  "equity_symbol": "NSE:ASIANPAINT-EQ",  "lot_size": 200},
    {"name": "BAJAJFINSV",  "equity_symbol": "NSE:BAJAJFINSV-EQ",  "lot_size": 500},
    {"name": "WIPRO",       "equity_symbol": "NSE:WIPRO-EQ",       "lot_size": 1500},
    {"name": "HCLTECH",     "equity_symbol": "NSE:HCLTECH-EQ",     "lot_size": 700},
    {"name": "NTPC",        "equity_symbol": "NSE:NTPC-EQ",        "lot_size": 1500},
    {"name": "POWERGRID",   "equity_symbol": "NSE:POWERGRID-EQ",   "lot_size": 1900},
    {"name": "ONGC",        "equity_symbol": "NSE:ONGC-EQ",        "lot_size": 3850},
    {"name": "COALINDIA",   "equity_symbol": "NSE:COALINDIA-EQ",   "lot_size": 2100},
    {"name": "JSWSTEEL",    "equity_symbol": "NSE:JSWSTEEL-EQ",    "lot_size": 800},
    {"name": "GRASIM",      "equity_symbol": "NSE:GRASIM-EQ",      "lot_size": 250},
    {"name": "HINDALCO",    "equity_symbol": "NSE:HINDALCO-EQ",    "lot_size": 1400},
    {"name": "DRREDDY",     "equity_symbol": "NSE:DRREDDY-EQ",     "lot_size": 625},
    {"name": "CIPLA",       "equity_symbol": "NSE:CIPLA-EQ",       "lot_size": 650},
    {"name": "DIVISLAB",    "equity_symbol": "NSE:DIVISLAB-EQ",    "lot_size": 200},
    {"name": "EICHERMOT",   "equity_symbol": "NSE:EICHERMOT-EQ",   "lot_size": 175},
    {"name": "HEROMOTOCO",  "equity_symbol": "NSE:HEROMOTOCO-EQ",  "lot_size": 300},
    {"name": "BAJAJ-AUTO",  "equity_symbol": "NSE:BAJAJ-AUTO-EQ",  "lot_size": 75},
    {"name": "INDUSINDBK",  "equity_symbol": "NSE:INDUSINDBK-EQ",  "lot_size": 900},
    {"name": "TECHM",       "equity_symbol": "NSE:TECHM-EQ",       "lot_size": 600},
    {"name": "SBILIFE",     "equity_symbol": "NSE:SBILIFE-EQ",     "lot_size": 750},
    {"name": "HDFCLIFE",    "equity_symbol": "NSE:HDFCLIFE-EQ",    "lot_size": 1100},
    {"name": "BPCL",        "equity_symbol": "NSE:BPCL-EQ",        "lot_size": 1800},
    {"name": "PIDILITIND",  "equity_symbol": "NSE:PIDILITIND-EQ",  "lot_size": 250},
    {"name": "DLF",         "equity_symbol": "NSE:DLF-EQ",         "lot_size": 1650},
    {"name": "VEDL",        "equity_symbol": "NSE:VEDL-EQ",        "lot_size": 2300},
    {"name": "GODREJCP",    "equity_symbol": "NSE:GODREJCP-EQ",    "lot_size": 500},
    {"name": "SHREECEM",    "equity_symbol": "NSE:SHREECEM-EQ",    "lot_size": 25},
    {"name": "PFC",         "equity_symbol": "NSE:PFC-EQ",         "lot_size": 2500},
    {"name": "SIEMENS",     "equity_symbol": "NSE:SIEMENS-EQ",     "lot_size": 125},
]