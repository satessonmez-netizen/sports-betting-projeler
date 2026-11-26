"""Gol farkı ağırlıklı Elo + sıralı logit ile 1X2 olasılığı."""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

K, HFA, NEW_START, REGRESS = 18.0, 60.0, 1400.0, 0.25


def compute(d: pd.DataFrame):
    """d: tek lig, tarihe göre sıralı. Her maç için maç ÖNCESİ (ev+HFA - dep) farkını ve
    güncel puanları döndürür."""
    r, diffs, season_prev = {}, np.zeros(len(d)), None
    first = d.season.iloc[0]
    for k, row in enumerate(d.itertuples()):
        if season_prev is not None and row.season != season_prev:
            m = np.mean(list(r.values()))
            r = {t: (1 - REGRESS) * v + REGRESS * m for t, v in r.items()}
        season_prev = row.season
        for t in (row.home, row.away):
            if t not in r:
                r[t] = 1500.0 if row.season == first else NEW_START
        diff = r[row.home] + HFA - r[row.away]
        diffs[k] = diff
        if pd.notna(row.hg):
            e = expit(diff * np.log(10) / 400)
            s = 1.0 if row.hg > row.ag else 0.5 if row.hg == row.ag else 0.0
            mult = 1 + np.log(1 + abs(row.hg - row.ag))
            delta = K * mult * (s - e)
            r[row.home] += delta
            r[row.away] -= delta
    return diffs, r


def probs(diff, b, c):
    x = b * np.asarray(diff) / 100
    pA, pH = expit(-c - x), expit(x - c)
    return np.column_stack([pH, 1 - pH - pA, pA])


def fit_map(diff, y):
    def nll(p):
        P = probs(diff, p[0], abs(p[1]))
        return -np.log(np.clip(P[np.arange(len(y)), y], 1e-9, 1)).mean()
    res = minimize(nll, [0.5, 0.5], method="Nelder-Mead")
    return res.x[0], abs(res.x[1])
