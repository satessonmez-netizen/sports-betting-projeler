"""Zaman ağırlıklı Dixon-Coles modeli (lig bazında fit)."""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

MAXG = 10  # skor matrisi 0..MAXG


def _tau(x, y, lh, la, rho):
    t = np.ones_like(lh)
    t = np.where((x == 0) & (y == 0), 1 - lh * la * rho, t)
    t = np.where((x == 0) & (y == 1), 1 + lh * rho, t)
    t = np.where((x == 1) & (y == 0), 1 + la * rho, t)
    t = np.where((x == 1) & (y == 1), 1 - rho, t)
    return t


class DixonColes:
    def __init__(self, half_life_days: float = 365.0, reg: float = 0.02):
        self.hl = half_life_days
        self.reg = reg

    def fit(self, df: pd.DataFrame, ref_date: pd.Timestamp):
        teams = sorted(set(df.home) | set(df.away))
        self.idx = {t: i for i, t in enumerate(teams)}
        n = len(teams)
        h = df.home.map(self.idx).to_numpy()
        a = df.away.map(self.idx).to_numpy()
        x = df.hg.to_numpy(float)
        y = df.ag.to_numpy(float)
        age = (ref_date - df.date).dt.days.to_numpy(float)
        w = 0.5 ** (age / self.hl)
        reg = self.reg

        def nll(p):
            att, dfn = p[:n], p[n:2 * n]
            ha, rho = p[2 * n], p[2 * n + 1]
            lh = np.exp(att[h] - dfn[a] + ha)
            la = np.exp(att[a] - dfn[h])
            ll = (np.log(np.maximum(_tau(x, y, lh, la, rho), 1e-9))
                  + x * np.log(lh) - lh - gammaln(x + 1)
                  + y * np.log(la) - la - gammaln(y + 1))
            pen = reg * (np.sum(att ** 2) + np.sum(dfn ** 2))
            return -(w * ll).sum() + pen

        p0 = np.zeros(2 * n + 2)
        p0[2 * n] = 0.25
        cons = {"type": "eq", "fun": lambda p: np.mean(p[:n])}  # kimlik için
        res = minimize(nll, p0, method="SLSQP", constraints=[cons],
                       options={"maxiter": 200, "ftol": 1e-7})
        p = res.x
        self.att, self.dfn = p[:n], p[n:2 * n]
        self.ha, self.rho = p[2 * n], np.clip(p[2 * n + 1], -0.3, 0.3)
        return self

    def known(self, t):
        return t in self.idx

    def score_matrix(self, home: str, away: str) -> np.ndarray:
        i, j = self.idx[home], self.idx[away]
        lh = np.exp(self.att[i] - self.dfn[j] + self.ha)
        la = np.exp(self.att[j] - self.dfn[i])
        g = np.arange(MAXG + 1)
        from scipy.stats import poisson
        m = np.outer(poisson.pmf(g, lh), poisson.pmf(g, la))
        m[0, 0] *= 1 - lh * la * self.rho
        m[0, 1] *= 1 + lh * self.rho
        m[1, 0] *= 1 + la * self.rho
        m[1, 1] *= 1 - self.rho
        return m / m.sum()

    def predict(self, home: str, away: str) -> dict:
        m = self.score_matrix(home, away)
        ph = np.tril(m, -1).sum()
        pd_ = np.trace(m)
        pa = np.triu(m, 1).sum()
        g = np.arange(MAXG + 1)
        tot = np.add.outer(g, g)
        return {
            "pH": ph, "pD": pd_, "pA": pa,
            "pOver25": m[tot > 2.5].sum(),
            "pBTTS": m[1:, 1:].sum(),
            "xgH": (m.sum(1) * g).sum(), "xgA": (m.sum(0) * g).sum(),
        }
