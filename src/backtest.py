"""Walk-forward backtest: her test haftasında yalnızca o güne kadarki veriyle fit et.

Kullanım: python backtest.py [--div T1] [--from 2024-08-01] [--half-life 365]
"""
import argparse

import numpy as np
import pandas as pd

import elo

from config import LEAGUES, REPORTS
from data import load
from metrics import brier, implied, logloss, outcome, rps
from model import DixonColes


def run(div: str, start: str, half_life: float, reg: float = 5.0, shift: float = 0.0,
        ha_reg=None, window_years: int = 4, step_days: int = 14):
    d = load()
    d = d[d["div"] == div].reset_index(drop=True)
    d["elo_diff"] = elo.compute(d)[0]
    d = d[d.hg.notna()].reset_index(drop=True)
    yy = outcome(d.hg.to_numpy(), d.ag.to_numpy())
    start = pd.Timestamp(start)
    test = d[d.date >= start]
    rows = []
    cur = start
    end = d.date.max()
    while cur <= end:
        nxt = cur + pd.Timedelta(days=step_days)
        chunk = d[(d.date >= cur) & (d.date < nxt)]
        if len(chunk):
            train = d[(d.date < cur) & (d.date >= cur - pd.Timedelta(days=365 * window_years))]
            m = DixonColes(half_life, reg, shift, ha_reg).fit(train, cur)
            ti = train.index
            eb, ec = elo.fit_map(d.elo_diff[ti].to_numpy(), yy[ti])
            for r in chunk.itertuples():
                p = m.predict(r.home, r.away)
                e = elo.probs([r.elo_diff], eb, ec)[0]
                rows.append((r.date, r.home, r.away, r.hg, r.ag, p["pH"], p["pD"], p["pA"],
                             r.oH, r.oD, r.oA, *e))
        cur = nxt
    out = pd.DataFrame(rows, columns=["date", "home", "away", "hg", "ag", "mH", "mD", "mA",
                                      "oH", "oD", "oA", "eH", "eD", "eA"])
    return out


def report(out: pd.DataFrame, label: str) -> dict:
    y = outcome(out.hg.to_numpy(), out.ag.to_numpy())
    M = out[["mH", "mD", "mA"]].to_numpy()
    ok = out[["oH", "oD", "oA"]].notna().all(axis=1).to_numpy()
    B = implied(out.oH[ok].to_numpy(), out.oD[ok].to_numpy(), out.oA[ok].to_numpy())
    yo, Mo = y[ok], M[ok]
    base = np.tile(np.bincount(yo, minlength=3) / len(yo), (len(yo), 1))
    res = {"lig": label, "maç": int(ok.sum()),
           "model_RPS": rps(Mo, yo), "bahisçi_RPS": rps(B, yo), "baz_RPS": rps(base, yo),
           "model_logloss": logloss(Mo, yo), "bahisçi_logloss": logloss(B, yo),
           "model_brier": brier(Mo, yo), "bahisçi_brier": brier(B, yo),
           "isabet": (Mo.argmax(1) == yo).mean(), "bahisçi_isabet": (B.argmax(1) == yo).mean()}
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--div", default="T1")
    ap.add_argument("--from", dest="start", default="2024-08-01")
    ap.add_argument("--half-life", type=float, default=250)
    ap.add_argument("--w", type=float, default=0.5, help="Elo karışım ağırlığı")
    a = ap.parse_args()
    divs = list(LEAGUES) if a.div == "all" else [a.div]
    results = []
    for dv in divs:
        o = run(dv, a.start, a.half_life)
        for k in "HDA":
            o[f"m{k}"] = (1 - a.w) * o[f"m{k}"] + a.w * o[f"e{k}"]
        results.append(report(o, LEAGUES[dv]))
        o.to_csv(REPORTS / f"backtest_{dv}.csv", index=False)
        print(results[-1])
    r = pd.DataFrame(results)
    pd.set_option("display.width", 200)
    print(r.round(4).to_string(index=False))
