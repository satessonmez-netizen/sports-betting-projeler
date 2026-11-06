"""Yaklaşan maçlar için tahmin üretir ve predictions/log.csv'ye ekler (paper trading).
Maç sonuçları geldikten sonra `python predict.py --settle` ile skorlar işlenir.
"""
import argparse
import io

import numpy as np
import pandas as pd
import requests

from config import LEAGUES, PRED
from data import download, load
from metrics import brier, implied, outcome, rps
from model import DixonColes

LOG = PRED / "log.csv"
FIX_URL = "https://football-data.co.uk/fixtures.csv"
# fixtures.csv'deki takım adları sonuç dosyalarıyla aynı kaynaktan geliyor
COLS = ["date", "div", "home", "away", "mH", "mD", "mA", "mOver25", "mBTTS",
        "oH", "oD", "oA", "hg", "ag"]


def upcoming() -> pd.DataFrame:
    r = requests.get(FIX_URL, timeout=60)
    df = pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")))
    df = df[df["Div"].isin(LEAGUES)].copy()
    df["date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed")
    for k in "HDA":
        df[f"o{k}"] = pd.to_numeric(df.get(f"Avg{k}"), errors="coerce")
    return df.rename(columns={"Div": "div", "HomeTeam": "home", "AwayTeam": "away"})


def make() -> None:
    download()
    hist = load()
    hist = hist[hist.hg.notna()]
    now = pd.Timestamp.today().normalize()
    fx = upcoming()
    rows = []
    for dv, g in fx.groupby("div"):
        tr = hist[(hist["div"] == dv) & (hist.date >= now - pd.Timedelta(days=365 * 4))]
        m = DixonColes().fit(tr, now)
        for r in g.itertuples():
            if not (m.known(r.home) and m.known(r.away)):
                print("bilinmeyen takım, atlandı:", r.home, r.away)
                continue
            p = m.predict(r.home, r.away)
            rows.append(dict(date=r.date.date(), div=dv, home=r.home, away=r.away,
                             mH=p["pH"], mD=p["pD"], mA=p["pA"], mOver25=p["pOver25"],
                             mBTTS=p["pBTTS"], oH=r.oH, oD=r.oD, oA=r.oA, hg=np.nan, ag=np.nan))
    new = pd.DataFrame(rows, columns=COLS)
    PRED.mkdir(exist_ok=True)
    if LOG.exists():
        old = pd.read_csv(LOG)
        key = ["date", "div", "home", "away"]
        new["date"] = new["date"].astype(str)
        new = new.merge(old[key], on=key, how="left", indicator=True)
        new = new[new["_merge"] == "left_only"].drop(columns="_merge")  # tahmin sonradan değişmesin
        out = pd.concat([old, new], ignore_index=True)
    else:
        out = new
    out.to_csv(LOG, index=False)
    print(f"{len(new)} yeni tahmin eklendi, toplam {len(out)}")
    show = new.copy()
    show["fark_H"] = show.mH - implied(show.oH, show.oD, show.oA)[:, 0] if len(show) else []
    print(show[["date", "home", "away", "mH", "mD", "mA", "fark_H"]].round(2).head(30).to_string(index=False))


def settle() -> None:
    download()
    hist = load()
    hist = hist[hist.hg.notna()]
    log = pd.read_csv(LOG)
    log["date"] = pd.to_datetime(log["date"])
    key = ["date", "div", "home", "away"]
    res = hist[key + ["hg", "ag"]].rename(columns={"hg": "hg_", "ag": "ag_"})
    log = log.merge(res, on=key, how="left")
    log["hg"] = log["hg"].fillna(log["hg_"])
    log["ag"] = log["ag"].fillna(log["ag_"])
    log = log.drop(columns=["hg_", "ag_"])
    log.to_csv(LOG, index=False)
    s = log[log.hg.notna() & log.oH.notna()]
    if s.empty:
        print("henüz sonuçlanmış maç yok")
        return
    y = outcome(s.hg.to_numpy(), s.ag.to_numpy())
    M = s[["mH", "mD", "mA"]].to_numpy()
    B = implied(s.oH.to_numpy(), s.oD.to_numpy(), s.oA.to_numpy())
    print(f"{len(s)} maç | model RPS {rps(M, y):.4f} vs piyasa {rps(B, y):.4f} | "
          f"Brier {brier(M, y):.4f} vs {brier(B, y):.4f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--settle", action="store_true")
    a = ap.parse_args()
    settle() if a.settle else make()
