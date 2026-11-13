"""Model ile piyasa nerede ayrışıyor? Segment bazlı RPS karşılaştırması.

Kullanım: python segments.py [--div T1]   (önce backtest.py'nin ürettiği reports/backtest_*.csv gerekir)
"""
import argparse

import numpy as np
import pandas as pd

from config import REPORTS
from metrics import implied, outcome, rps


def per_match_rps(P, y):
    Y = np.eye(3)[y]
    return (((np.cumsum(P, 1) - np.cumsum(Y, 1)) ** 2)[:, :2].sum(1) / 2)


def segment(df: pd.DataFrame) -> pd.DataFrame:
    y = outcome(df.hg.to_numpy(), df.ag.to_numpy())
    B = implied(df.oH.to_numpy(), df.oD.to_numpy(), df.oA.to_numpy())
    M = df[["mH", "mD", "mA"]].to_numpy()
    df = df.assign(model=per_match_rps(M, y), piyasa=per_match_rps(B, y))
    df["fark"] = df.model - df.piyasa
    df["favori_olasilik"] = B.max(1)
    df["fav_taraf"] = np.where(B[:, 0] >= B[:, 2], "ev", "dep")
    df["model_piyasa_ayrisma"] = np.abs(M - B).max(1)
    df["ay"] = df.date.dt.month
    df["sezon_sonu"] = df.ay.isin([4, 5])
    df["sezon_basi"] = df.ay.isin([8, 9])
    df["bin"] = pd.cut(df.favori_olasilik, [0, .4, .5, .6, .7, 1],
                       labels=["<%40", "%40-50", "%50-60", "%60-70", ">%70"])
    return df


def table(df, col):
    g = df.groupby(col, observed=True).agg(maç=("fark", "size"), model=("model", "mean"),
                                           piyasa=("piyasa", "mean"), fark=("fark", "mean"))
    return g.round(4)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--div", default="T1")
    a = ap.parse_args()
    df = pd.read_csv(REPORTS / f"backtest_{a.div}.csv", parse_dates=["date"])
    df = df.dropna(subset=["oH", "oD", "oA"])
    s = segment(df)
    print(f"Toplam {len(s)} maç | model {s.model.mean():.4f} piyasa {s.piyasa.mean():.4f} fark {s.fark.mean():+.4f}\n")
    for col in ("bin", "fav_taraf", "sezon_sonu", "sezon_basi"):
        print(f"--- {col}")
        print(table(s, col).to_string(), "\n")
    # fark gürültü mü? bootstrap güven aralığı
    rng = np.random.default_rng(0)
    bs = [s.fark.sample(len(s), replace=True, random_state=int(rng.integers(1e9))).mean() for _ in range(500)]
    print("Genel fark %%95 aralık: [%.4f, %.4f]" % tuple(np.percentile(bs, [2.5, 97.5])))
