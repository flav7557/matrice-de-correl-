"""
update.py — recupere les cours via yfinance et ecrit data.json
Lance chaque jour par GitHub Actions (voir .github/workflows/update.yml).
Edite ASSETS pour changer l'univers.
"""
import json
import pandas as pd
import yfinance as yf

# (ticker Yahoo, libelle court, nom complet, classe d'actif)
ASSETS = [
    ("^STOXX50E", "SX5E",   "Euro Stoxx 50", "Actions"),
    ("^FCHI",     "CAC",    "CAC 40",        "Actions"),
    ("^GDAXI",    "DAX",    "DAX 40",        "Actions"),
    ("^GSPC",     "SPX",    "S&P 500",       "Actions"),
    ("^NDX",      "NDX",    "Nasdaq 100",    "Actions"),
    ("BZ=F",      "Brent",  "Pétrole Brent", "Commodités"),
    ("GC=F",      "Or",     "Or",            "Commodités"),
    ("EURUSD=X",  "EURUSD", "EUR/USD",       "FX"),
]

PERIOD = "2y"   # historique recupere (donne de la marge pour les fenetres 1A / Max)

syms = [a[0] for a in ASSETS]

raw = yf.download(syms, period=PERIOD, interval="1d",
                  auto_adjust=True, progress=False)
close = raw["Close"]

present = [a for a in ASSETS if a[0] in close.columns]
close = close[[a[0] for a in present]].dropna(how="all")
close.columns = [a[1] for a in present]
shorts = list(close.columns)

corr = close.pct_change().corr().reindex(index=shorts, columns=shorts)


def nz(v):
    return None if pd.isna(v) else round(float(v), 4)


out = {
    "asof": close.dropna(how="all").index[-1].strftime("%Y-%m-%d"),
    "generated": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "shorts": shorts,
    "names": [a[2] for a in present],
    "classes": [a[3] for a in present],
    "dates": [d.strftime("%Y-%m-%d") for d in close.index],
    "corr": [[nz(v) for v in row] for row in corr.values],
    "prices": {s: [nz(v) for v in close[s].values] for s in shorts},
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)

print(f"data.json ecrit — {len(shorts)} actifs, arrete au {out['asof']}")
