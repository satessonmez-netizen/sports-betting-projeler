"""football-data.co.uk CSV'lerini indirir ve tek bir temiz tabloya çevirir."""
import io
import sys

import numpy as np
import pandas as pd
import requests

from config import BASE_URL, LEAGUES, RAW, SEASONS


def download(force_current: bool = True) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    current = SEASONS[-1]
    for season in SEASONS:
        for div in LEAGUES:
            path = RAW / f"{season}_{div}.csv"
            if path.exists() and not (force_current and season == current):
                continue
            r = requests.get(BASE_URL.format(season=season, div=div), timeout=60)
            if r.status_code != 200 or len(r.content) < 200:
                print(f"atlandı {season} {div} ({r.status_code})", file=sys.stderr)
                continue
            path.write_bytes(r.content)
            print(f"indirildi {season} {div} ({len(r.content)//1024} KB)")


def _odds_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Kapanış oranı varsa onu (Pinnacle > Bet365 > ortalama), yoksa açılış oranını seç."""
    out = pd.DataFrame(index=df.index)
    prefs = ["PSC", "B365C", "AvgC", "PS", "B365", "Avg"]
    for side, k in zip("HDA", "HDA"):
        out[f"o{side}"] = np.nan
    for p in prefs:
        cols = [f"{p}{k}" for k in "HDA"]
        if all(c in df for c in cols):
            ok = out["oH"].isna()
            for side, c in zip("HDA", cols):
                out.loc[ok, f"o{side}"] = pd.to_numeric(df.loc[ok, c], errors="coerce")
    return out


def load() -> pd.DataFrame:
    frames = []
    for path in sorted(RAW.glob("*.csv")):
        season, div = path.stem.split("_")
        try:
            df = pd.read_csv(io.BytesIO(path.read_bytes()), encoding="latin-1",
                             on_bad_lines="skip")
        except Exception as e:  # bozuk dosya
            print("okunamadı", path.name, e, file=sys.stderr)
            continue
        df = df.dropna(subset=["HomeTeam", "AwayTeam"])
        d = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce", format="mixed")
        o = _odds_cols(df)
        res = pd.DataFrame({
            "date": d, "div": div, "season": season,
            "home": df["HomeTeam"].str.strip(), "away": df["AwayTeam"].str.strip(),
            "hg": pd.to_numeric(df.get("FTHG"), errors="coerce"),
            "ag": pd.to_numeric(df.get("FTAG"), errors="coerce"),
            "oH": o["oH"], "oD": o["oD"], "oA": o["oA"],
        })
        frames.append(res.dropna(subset=["date"]))
    all_ = pd.concat(frames, ignore_index=True).sort_values("date").reset_index(drop=True)
    return all_


if __name__ == "__main__":
    download()
    d = load()
    print(d.groupby("div").size())
    print("oynanmış:", d["hg"].notna().sum(), "oranlı:", d["oH"].notna().sum())
