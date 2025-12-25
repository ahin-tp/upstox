import csv

INSTRUMENT_FILE = "instruments.csv"

# Load once at startup
_instruments = []

with open(INSTRUMENT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        # Typical NSE.csv format:
        # 0: trading_symbol, 1: isin, 2: instrument_key, ...
        if len(row) > 2 and row[2].startswith("NSE_EQ"):
            _instruments.append({
                "symbol": row[0],
                "isin": row[1],
                "token": row[2]
            })


def search_instrument(query, limit=10):
    q = query.upper()
    results = []

    for inst in _instruments:
        if q in inst["symbol"]:
            results.append(inst)
            if len(results) >= limit:
                break

    return results
