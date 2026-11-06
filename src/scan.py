"""9 ligde parametre taraması (paralel). Kullanım: python scan.py"""
import warnings
from multiprocessing import Pool

import numpy as np
import pandas as pd

from backtest import run
from config import LEAGUES
from metrics import implied, outcome, rps

warnings.filterwarnings("ignore")
START = "2024-08-01"


def job(args):
    dv, cfg = args
    o = run(dv, START, **cfg)
    o["div"] = dv
    return o


def summarize(o, w):
    y = outcome(o.hg.to_numpy(), o.ag.to_numpy())
    ok = o[["oH", "oD", "oA"]].notna().all(axis=1).to_numpy()
    P = (1 - w) * o[["mH", "mD", "mA"]].to_numpy() + w * o[["eH", "eD", "eA"]].to_numpy()
    B = implied(o.oH.to_numpy(), o.oD.to_numpy(), o.oA.to_numpy())
    d = (B[:, 2] > B[:, 0]) & ok
    return (rps(P[ok], y[ok]) - rps(B[ok], y[ok]),                 # genel fark (düşük iyi)
            (y[d] == 2).mean() - P[d, 2].mean())                    # dep favori sapması (0'a yakın iyi)


if __name__ == "__main__":
    cfgs = {f"reg={r}": dict(half_life=250, reg=r) for r in (0.5, 1.0, 2.0, 5.0)}
    cfgs["reg=1,hl=400"] = dict(half_life=400, reg=1.0)
    with Pool(4) as pool:
        for name, cfg in cfgs.items():
            outs = pd.concat(pool.map(job, [(dv, cfg) for dv in LEAGUES]), ignore_index=True)
            for w in (0.3, 0.5):
                gap, bias = summarize(outs, w)
                print(f"{name:14s} w={w}: RPS farkı {gap:+.4f} | dep-favori sapması {bias:+.3f}", flush=True)
