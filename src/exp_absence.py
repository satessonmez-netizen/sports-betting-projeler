"""Deney: 'maçta kadroda olmayan değerli oyuncular' tahmini iyileştiriyor mu?

Geçmiş veriden (Transfermarkt veri seti, kadro/ilk 11 kayıtları) her takım-maç için eksik oyuncu değeri payı
hesaplar, sonra bunun model ve piyasa olasılıklarına eklenince RPS'i değiştirip değiştirmediğine bakar.
UYARI: 'eksik' = kadroda (ilk 11 + yedekler) yer almayan. Gerçek sakatlıkla rotasyonu/cezayı ayırmaz.
Kadro bilgisi maçta bilinir; açılış oranı bunu bilmez, kapanış oranı kısmen bilir.
Kullanım: python exp_absence.py
"""
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from config import LEAGUES, REPORTS
from data import load
from metrics import implied, logloss, outcome, rps
from tm_value import DOM, EX, club_map

warnings.filterwarnings("ignore")
START, SPLIT, END = pd.Timestamp("2024-08-01"), pd.Timestamp("2025-07-01"), pd.Timestamp("2026-06-12")


def build_abs():
    """Aktif kadro = takımın son 60 günde (herhangi bir turnuvada) oynadığı maç kadrolarında yer alan oyuncular.
    Eksik = aktif kadroda olup bu maç kadrosunda (ilk 11 + yedek) olmayanlar. Değer: son piyasa değeri."""
    clubs = pd.read_csv(f"{EX}/clubs.csv.gz")
    games = pd.read_csv(f"{EX}/games.csv.gz", parse_dates=["date"])
    games = games[(games.date >= START - pd.Timedelta(days=130)) & (games.date <= END)]
    lu = pd.read_csv(f"{EX}/game_lineups.csv.gz", usecols=["game_id", "club_id", "player_id"])
    lu = lu[lu.game_id.isin(games.game_id)]
    gdate = games.set_index("game_id").date
    lu["date"] = lu.game_id.map(gdate)
    per_club = {}
    for (cid, gid), g in lu.groupby(["club_id", "game_id"]):
        per_club.setdefault(cid, []).append((gdate[gid], gid, set(g.player_id)))
    for c in per_club:
        per_club[c].sort(key=lambda t: t[0])
    val = pd.read_csv(f"{EX}/player_valuations.csv.gz", parse_dates=["date"])
    val = val[val.market_value_in_eur.notna() & (val.date <= END)].sort_values("date")
    pv = {p: (g.date.to_numpy(), g.market_value_in_eur.to_numpy()) for p, g in val.groupby("player_id")}

    def value(p, d):
        t = pv.get(p)
        if t is None:
            return np.nan
        i = np.searchsorted(t[0], np.datetime64(d), side="right") - 1
        return t[1][i] if i >= 0 else np.nan

    target = games[(games.competition_id.isin(DOM.values())) & (games.date >= START - pd.Timedelta(days=3))]
    rows = []
    for g in target.itertuples():
        for side, cid in (("home", g.home_club_id), ("away", g.away_club_id)):
            hist = [t for t in per_club.get(cid, []) if g.date - pd.Timedelta(days=60) <= t[0] < g.date][-6:]
            cur = next((t[2] for t in per_club.get(cid, []) if t[1] == g.game_id), None)
            if len(hist) < 3 or not cur:
                rows.append((g.game_id, side, np.nan, np.nan, np.nan, np.nan))
                continue
            prev = [t for t in per_club.get(cid, []) if t[0] < g.date]
            rest = min((g.date - prev[-1][0]).days, 14) if prev else np.nan
            active = set().union(*[t[2] for t in hist])
            vals = {p: value(p, g.date) for p in active}
            vals = {p: v for p, v in vals.items() if v == v and v > 0}
            tot = sum(vals.values())
            if tot <= 0:
                rows.append((g.game_id, side, np.nan, np.nan, np.nan, np.nan))
                continue
            ab = sorted([v for p, v in vals.items() if p not in cur])
            rows.append((g.game_id, side, sum(ab) / tot, sum(ab[-3:]) / tot, tot, rest))
    a = pd.DataFrame(rows, columns=["game_id", "side", "abs_share", "abs_top3", "val", "rest"])
    h = a[a.side == "home"].set_index("game_id")[["abs_share", "abs_top3", "val", "rest"]].add_prefix("h_")
    w = a[a.side == "away"].set_index("game_id")[["abs_share", "abs_top3", "val", "rest"]].add_prefix("a_")
    return target.set_index("game_id")[["date", "home_club_id", "away_club_id"]].join(h).join(w).reset_index(), clubs


def adj(P, x, b):
    Q = P * np.column_stack([np.exp(b * x), np.ones_like(x), np.exp(-b * x)])
    return Q / Q.sum(1, keepdims=True)


def fit_beta(P, x, y):
    return minimize_scalar(lambda b: logloss(adj(P, x, b), y), bounds=(-15, 15), method="bounded").x


def per_rps(P, y):
    Y = np.eye(3)[y]
    return (((np.cumsum(P, 1) - np.cumsum(Y, 1)) ** 2)[:, :2].sum(1) / 2)


def boot(d, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    m = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)]
    return np.percentile(m, [2.5, 97.5])


def main():
    ab, clubs = build_abs()
    res = load()
    res = res[res.hg.notna()]
    parts = []
    for fd, dm in DOM.items():
        bt = pd.read_csv(REPORTS / f"backtest_{fd}.csv", parse_dates=["date"])
        names = sorted(set(bt.home) | set(bt.away))
        m = club_map(names, clubs[clubs.domestic_competition_id == dm])
        bt["h_id"] = bt.home.map(m)
        bt["a_id"] = bt.away.map(m)
        bt["div"] = fd
        parts.append(bt)
    bt = pd.concat(parts, ignore_index=True)
    bt = bt[(bt.date >= START) & (bt.date <= END)]
    bo = res[["date", "home", "away", "boH", "boD", "boA"]]
    bt = bt.merge(bo, on=["date", "home", "away"], how="left")
    # TM maçıyla eşleştir (tarih ±1 gün)
    out = []
    ab = ab.dropna(subset=["h_abs_share", "a_abs_share"])
    for r in bt.dropna(subset=["h_id", "a_id"]).itertuples():
        pass
    ab["key"] = list(zip(ab.home_club_id, ab.away_club_id))
    idx = {}
    for r in ab.itertuples():
        idx.setdefault(r.key, []).append(r)
    rows = []
    for r in bt.dropna(subset=["h_id", "a_id"]).itertuples():
        for c in idx.get((r.h_id, r.a_id), []):
            if abs((c.date - r.date).days) <= 1:
                rows.append({**r._asdict(), "h_abs": c.h_abs_share, "a_abs": c.a_abs_share,
                             "h_top3": c.h_abs_top3, "a_top3": c.a_abs_top3,
                             "h_val": c.h_val, "a_val": c.a_val, "h_rest": c.h_rest, "a_rest": c.a_rest})
                break
    d = pd.DataFrame(rows)
    print(f"Eşleşen maç: {len(d)} / {len(bt)} (kapsam %{100*len(d)/len(bt):.0f})")
    d = d.dropna(subset=["oH", "oD", "oA"])
    y = outcome(d.hg.to_numpy(), d.ag.to_numpy())
    fit = (d.date < SPLIT).to_numpy()
    test = ~fit
    print(f"Fit: {fit.sum()} maç (2024-08 → 2025-06) | Test: {test.sum()} maç (2025-07 → 2026-06)")
    print(f"Eksik değer payı ort.: ev {d.h_abs.mean():.3f}, dep {d.a_abs.mean():.3f}; top3 ort. ev {d.h_top3.mean():.3f}")
    x_all = (d.a_abs - d.h_abs).to_numpy()
    x_top = (d.a_top3 - d.h_top3).to_numpy()
    mk_close = implied(d.oH.to_numpy(), d.oD.to_numpy(), d.oA.to_numpy())
    ok_o = d[["boH", "boD", "boA"]].notna().all(axis=1).to_numpy()
    mk_open = np.where(ok_o[:, None], implied(d.boH.fillna(2).to_numpy(), d.boD.fillna(3).to_numpy(), d.boA.fillna(3).to_numpy()), np.nan)
    mdl = d[["mH", "mD", "mA"]].to_numpy()
    print("\n=== 1) Eksik oyuncu değeri tahmini iyileştiriyor mu? (test: RPS, düşük iyi) ===")
    for name, P, mask in (("model", mdl, np.ones(len(d), bool)), ("piyasa kapanış", mk_close, np.ones(len(d), bool)),
                          ("piyasa açılış (Bet365)", mk_open, ok_o)):
        for xn, x in (("eksik pay", x_all), ("en değerli 3 eksik", x_top)):
            f, t = fit & mask, test & mask
            b = fit_beta(P[f], x[f], y[f])
            base, new = per_rps(P[t], y[t]), per_rps(adj(P[t], x[t], b), y[t])
            diff = new - base
            lo, hi = boot(diff)
            print(f"{name:24s} | {xn:20s} | beta={b:+.2f} | RPS {base.mean():.4f} → {new.mean():.4f} "
                  f"(fark {diff.mean():+.5f}, %95 [{lo:+.5f}, {hi:+.5f}]) n_test={t.sum()}")
    print("\n=== 2) Model, piyasanın üstüne bilgi ekliyor mu? ===")
    w = minimize_scalar(lambda w: logloss((1 - w) * mk_close[fit] + w * mdl[fit], y[fit]), bounds=(0, 1), method="bounded").x
    mix = (1 - w) * mk_close + w * mdl
    dm_ = per_rps(mix[test], y[test]) - per_rps(mk_close[test], y[test])
    lo, hi = boot(dm_)
    print(f"En iyi karışım ağırlığı (model payı) w={w:.2f} (fit dönemi)")
    print(f"Test RPS: piyasa {per_rps(mk_close[test], y[test]).mean():.4f} | model {per_rps(mdl[test], y[test]).mean():.4f} | "
          f"karışım {per_rps(mix[test], y[test]).mean():.4f} (karışım-piyasa {dm_.mean():+.5f}, %95 [{lo:+.5f}, {hi:+.5f}])")
    # 3) Yeni özellikler model üstünde: takım değeri oranı ve dinlenme farkı
    print("\n=== 3) Takım değeri ve yorgunluk, MODELİ iyileştiriyor mu? (test RPS) ===")
    dd = d.dropna(subset=["h_val", "a_val", "h_rest", "a_rest"])
    yy = outcome(dd.hg.to_numpy(), dd.ag.to_numpy())
    fit2 = (dd.date < SPLIT).to_numpy()
    te2 = ~fit2
    Pm = dd[["mH", "mD", "mA"]].to_numpy()
    Pk = implied(dd.oH.to_numpy(), dd.oD.to_numpy(), dd.oA.to_numpy())
    feats = {
        "takım değeri (log oran)": (np.log(dd.h_val) - np.log(dd.a_val)).to_numpy(),
        "dinlenme farkı (gün, +-5)": (dd.h_rest.clip(2, 10) - dd.a_rest.clip(2, 10)).clip(-5, 5).to_numpy(),
    }
    feats["ikisi birlikte"] = np.column_stack([feats["takım değeri (log oran)"], feats["dinlenme farkı (gün, +-5)"]])

    def adjm(P, X, b):
        X = X.reshape(len(P), -1)
        s_ = X @ np.atleast_1d(b)
        Q = P * np.column_stack([np.exp(s_), np.ones(len(P)), np.exp(-s_)])
        return Q / Q.sum(1, keepdims=True)

    from scipy.optimize import minimize
    for name, X in feats.items():
        for bn, P in (("model", Pm), ("piyasa kapanış", Pk)):
            k = 1 if X.ndim == 1 else X.shape[1]
            r_ = minimize(lambda b: logloss(adjm(P[fit2], X[fit2], b), yy[fit2]), np.zeros(k), method="Nelder-Mead")
            base = per_rps(P[te2], yy[te2])
            new = per_rps(adjm(P[te2], X[te2], r_.x), yy[te2])
            lo, hi = boot(new - base)
            print(f"{bn:15s} | {name:26s} | beta={np.round(r_.x, 3)} | RPS {base.mean():.4f} → {new.mean():.4f} "
                  f"(fark {(new - base).mean():+.5f}, %95 [{lo:+.5f}, {hi:+.5f}]) n_test={te2.sum()}")
    d.to_csv(REPORTS / "exp_absence_data.csv", index=False)


if __name__ == "__main__":
    main()
