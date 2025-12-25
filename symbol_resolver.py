import csv

INSTRUMENT_FILE = "instruments.csv"

_symbol_to_token = {}

with open(INSTRUMENT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        key = row.get("instrument_key")
        symbol = row.get("trading_symbol")

        if not key or not symbol:
            continue

        if not key.startswith("NSE_EQ"):
            continue

        _symbol_to_token[symbol.upper()] = key


def resolve_symbol(symbol: str):
    return _symbol_to_token.get(symbol.upper().strip())
