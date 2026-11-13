"""Zaman ağırlıklı Dixon-Coles modeli (lig bazında fit).

v2 eklemeleri:
- Yeni terfi eden / az maçı olan takımlar için lig ortalamasının altında başlangıç değeri (newcomer).
- Takıma özel ev sahibi avantajı (güçlü düzenlemeyle lig ortalamasına çekilir).
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import poisson

MAXG = 10  # skor matrisi 0..MAXG
NEWCOMER_MATCHES = 30  # eğitim penceresinde bundan az maçı olan takım "yeni" sayılır


def _tau(x, y, lh, la, rho):
    t = np.ones_like(lh)
    t = np.where((x == 0) & (y == 0), 1 - lh * la * rho, t)
    t = np.where((x == 0) & (y == 1), 1 + lh * rho, t)
    t = np.where((x == 1) & (y == 0), 1 + la * rho, t)
    t = np.where((x == 1) & (y == 1), 1 - rho, t)
    return t


class DixonColes:
    def __init__(self, half_life_days: float = 250.0, reg: float = 5.0,
                 newcomer_shift: float = 0.0, team_ha_reg: float | None = None):
        self.hl = half_life_days
        self.reg = reg
        self.shift = newcomer_shift          # >0: yeni takım ortalamanın bu kadar altında başlar
        self.ha_reg = team_ha_reg            # None: takım bazlı ev avantajı kapalı

    def fit(self, df: pd.DataFrame, ref_date: pd.Timestamp):
        teams = sorted(set(df.home) | set(df.away))
        self.idx = {t: i for i, t in enumerate(teams)}
        n = len(teams)
        h = df.home.map(self.idx).to_numpy()
        a = df.away.map(self.idx).to_numpy()
        x = df.hg.to_numpy(float)
        y = df.ag.to_numpy(float)
        # Poisson kısmında 'etkin gol' (gol ile şut-bazlı xG proxy karışımı) kullanılabilir
        xe = df["hg_eff"].to_numpy(float) if "hg_eff" in df else x
        ye = df["ag_eff"].to_numpy(float) if "ag_eff" in df else y
        w = 0.5 ** ((ref_date - df.date).dt.days.to_numpy(float) / self.hl)
        reg, ha_reg, use_ha = self.reg, self.ha_reg, self.ha_reg is not None

        counts = np.bincount(np.r_[h, a], minlength=n)
        mu = np.where(counts < NEWCOMER_MATCHES, -self.shift, 0.0)  # hücum/savunma önsel ortalaması

        def unpack(p):
            att, dfn = p[:n], p[n:2 * n]
            ha, rho = p[2 * n], p[2 * n + 1]
            tha = p[2 * n + 2:3 * n + 2] if use_ha else np.zeros(n)
            return att, dfn, ha, rho, tha

        def nll(p):
            att, dfn, ha, rho, tha = unpack(p)
            lh = np.exp(att[h] - dfn[a] + ha + tha[h])
            la = np.exp(att[a] - dfn[h])
            ll = (np.log(np.maximum(_tau(x, y, lh, la, rho), 1e-9))
                  + xe * np.log(lh) - lh
                  + ye * np.log(la) - la)
            pen = reg * (np.sum((att - mu) ** 2) + np.sum((dfn - mu) ** 2))
            if use_ha:
                pen += ha_reg * np.sum(tha ** 2)
            return -(w * ll).sum() + pen

        p0 = np.zeros(2 * n + 2 + (n if use_ha else 0))
        p0[:2 * n] = np.r_[mu, mu]
        p0[2 * n] = 0.25
        cons = {"type": "eq", "fun": lambda p: np.mean(p[:n]) - np.mean(mu)}
        res = minimize(nll, p0, method="SLSQP", constraints=[cons],
                       options={"maxiter": 200, "ftol": 1e-7})
        att, dfn, ha, rho, tha = unpack(res.x)
        self.att, self.dfn, self.ha, self.tha = att, dfn, ha, tha
        self.rho = float(np.clip(rho, -0.3, 0.3))
        self.new_mu = -self.shift            # bilinmeyen takımlar için varsayılan değer
        return self

    def known(self, t):
        return t in self.idx

    def _rates(self, home, away):
        def get(t):
            if t in self.idx:
                i = self.idx[t]
                return self.att[i], self.dfn[i], self.tha[i]
            return self.new_mu, self.new_mu, 0.0     # tamamen yeni takım
        ah, dh, th = get(home)
        aa, da, _ = get(away)
        return np.exp(ah - da + self.ha + th), np.exp(aa - dh)

    def score_matrix(self, home: str, away: str) -> np.ndarray:
        lh, la = self._rates(home, away)
        g = np.arange(MAXG + 1)
        m = np.outer(poisson.pmf(g, lh), poisson.pmf(g, la))
        m[0, 0] *= 1 - lh * la * self.rho
        m[0, 1] *= 1 + lh * self.rho
        m[1, 0] *= 1 + la * self.rho
        m[1, 1] *= 1 - self.rho
        return m / m.sum()

    def predict(self, home: str, away: str) -> dict:
        m = self.score_matrix(home, away)
        g = np.arange(MAXG + 1)
        tot = np.add.outer(g, g)
        return {
            "pH": np.tril(m, -1).sum(), "pD": np.trace(m), "pA": np.triu(m, 1).sum(),
            "pOver25": m[tot > 2.5].sum(), "pBTTS": m[1:, 1:].sum(),
            "xgH": (m.sum(1) * g).sum(), "xgA": (m.sum(0) * g).sum(),
        }
