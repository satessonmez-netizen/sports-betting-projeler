"""FotMob takım istatistikleri: her çalıştırmada TARİHLİ anlık görüntü alır ve geçmişe ekler.

Kullanım:
  python fotmob_stats.py                       # leagues.csv'deki tüm aktif ligler
  python fotmob_stats.py --div T1              # tek lig
  python fotmob_stats.py --add-url "<FotMob istatistik sayfası adresi>" --div SP1 --name "La Liga"
  python fotmob_stats.py --div T1 --excel      # ayrıca .xlsx de yazar (openpyxl gerekir)

Çıktılar (data/fotmob/):
  snapshots/<lig>_<tarih>.csv   o günün tablosu (okunaklı, türetilmiş sütunlarla)
  history.csv                   tüm tarihler, uzun biçim (maç başına xG vb. geçmişi buradan çıkar)
  leagues.csv                   div, league_id, season_id, name, enabled
  team_names.csv                FotMob adı -> football-data adı (elle düzeltilebilir)

NOT: FotMob'un resmi API'si yok. Bu dosyalar sitenin kendi kullandığı JSON'lar; değişebilir, kullanım şartları
kısıtlayabilir. Haftada 1-2 çalıştırmak yeterli, her çalıştırma lig başına ~24 küçük istektir.
Sezon değişince leagues.csv'deki season_id'yi güncelle.
"""
import argparse
import re
import time
import unicodedata
from datetime import date

import pandas as pd
import requests

from config import ROOT

DIR = ROOT / "data" / "fotmob"
LEAGUES = DIR / "leagues.csv"
NAMES = DIR / "team_names.csv"
HISTORY = DIR / "history.csv"
SNAPS = DIR / "snapshots"
URL = "https://data.fotmob.com/stats/{lig}/season/{sezon}/{stat}.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; kisisel-arastirma-betigi)"}
DELAY = 0.6

# FotMob dosya adı -> sütun adı. xG ve gol farkı için 'sub' değeri GERÇEK gol (doğrulandı: Galatasaray 23 gol).
STATLAR = {
    "rating_team": "FotMob Puanı",
    "expected_goals_team": "xG",
    "expected_goals_conceded_team": "Yenilen xG",
    "_xg_diff_team": "xG Farkı",
    "clean_sheet_team": "Gol Yemeden",
    "ontarget_scoring_att_team": "İsabetli Şut",
    "big_chance_team": "Büyük Fırsat",
    "big_chance_missed_team": "Kaçan Büyük Fırsat",
    "touches_in_opp_box_team": "Ceza Sahası Dokunuş",
    "corner_taken_team": "Korner",
    "_set_piece_goals_team": "Duran Top Gol",
    "_set_piece_goals_conceded_team": "Duran Top Yenilen",
    "penalty_won_team": "Kazanılan Penaltı",
    "penalty_conceded_team": "Yapılan Penaltı",
    "possession_percentage_team": "Topa Sahip Olma %",
    "accurate_pass_team": "Başarılı Pas",
    "accurate_cross_team": "İsabetli Kros",
    "interception_team": "Top Kapma",
    "total_tackle_team": "Top Çalma",
    "poss_won_att_3rd_team": "Rakip Alanda Top Kazanma",
    "saves_team": "Kurtarış",
    "fk_foul_lost_team": "Faul",
    "total_yel_card_team": "Sarı Kart",
    "total_red_card_team": "Kırmızı Kart",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s).replace("ı", "i").replace("İ", "I")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(fk|sk|fc|cf|afc|ac|sc)\b", " ", s)
    return re.sub(r"[^a-z0-9]", "", s)


def fetch(lig, sezon, stat, tries=2):
    last = None
    for k in range(tries):
        try:
            r = requests.get(URL.format(lig=lig, sezon=sezon, stat=stat), headers=HEADERS, timeout=20)
            r.raise_for_status()
            return r.json()["TopLists"][0]["StatList"]
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5)
    raise last


def collect(div, lig, sezon, today):
    rows, hatalar = [], []
    for stat, ad in STATLAR.items():
        try:
            for t in fetch(lig, sezon, stat):
                rows.append({"date": today, "div": div, "season_id": sezon, "team": t["ParticipantName"],
                             "stat": ad, "value": t["StatValue"], "sub_value": t.get("SubStatValue"),
                             "matches": t["MatchesPlayed"]})
            print("  ✓", ad)
        except Exception as e:  # noqa: BLE001
            hatalar.append(ad)
            print("  ✗", ad, "->", type(e).__name__, str(e)[:80])
        time.sleep(DELAY)
    return pd.DataFrame(rows), hatalar


def fd_names(div):
    """Bizim (football-data) takım adları, eşleştirme için."""
    try:
        from data import load
        d = load()
        d = d[(d["div"] == div) & (d.date >= pd.Timestamp.today() - pd.Timedelta(days=500))]
        return sorted(set(d.home) | set(d.away))
    except Exception:  # noqa: BLE001
        return []


def map_names(df, div):
    manual = pd.read_csv(NAMES) if NAMES.exists() else pd.DataFrame(columns=["div", "fotmob_name", "fd_name"])
    man = {r.fotmob_name: r.fd_name for r in manual[manual["div"] == div].itertuples()}
    ours = {norm(n): n for n in fd_names(div)}
    out = {}
    for t in df.team.unique():
        out[t] = man.get(t) or ours.get(norm(t)) or next((v for k, v in ours.items() if k.startswith(norm(t)) or norm(t).startswith(k)), "")
    return out


def wide(df):
    """O günün okunaklı tablosu + türetilmiş sütunlar."""
    v = df.pivot(index="team", columns="stat", values="value")
    s = df.pivot(index="team", columns="stat", values="sub_value")
    m = df.groupby("team").matches.first().rename("Maç")
    out = pd.concat([m, v], axis=1)
    out["xG gerçek gol"] = s.get("xG")
    out["Yenilen xG gerçek gol"] = s.get("Yenilen xG")
    n = out["Maç"].replace(0, float("nan"))
    out["xG/maç"] = (out["xG"] / n).round(2)
    out["Yenilen xG/maç"] = (out["Yenilen xG"] / n).round(2)
    out["xG farkı/maç"] = ((out["xG"] - out["Yenilen xG"]) / n).round(2)
    out["Şans (gol - xG)"] = (out["xG gerçek gol"] - out["xG"]).round(1)
    out["Yenilen şans (xGA - yenilen gol)"] = (out["Yenilen xG"] - out["Yenilen xG gerçek gol"]).round(1)
    return out.sort_values("xG farkı/maç", ascending=False)


def add_url(url, div, name):
    m = re.search(r"/leagues/(\d+)/.*?season/(\d+)", url) or re.search(r"/leagues/(\d+)/stats/season/(\d+)", url)
    if not m:
        raise SystemExit("Adreste lig ve sezon kimliği bulunamadı. Örnek: fotmob.com/leagues/71/stats/season/42167/teams/...")
    lig, sezon = int(m.group(1)), int(m.group(2))
    cfg = pd.read_csv(LEAGUES) if LEAGUES.exists() else pd.DataFrame(columns=["div", "league_id", "season_id", "name", "enabled"])
    cfg = cfg[cfg["div"] != div]
    cfg = pd.concat([cfg, pd.DataFrame([{"div": div, "league_id": lig, "season_id": sezon, "name": name or div, "enabled": 1}])])
    DIR.mkdir(parents=True, exist_ok=True)
    cfg.to_csv(LEAGUES, index=False)
    print(f"Eklendi: {div} ({name}) lig={lig} sezon={sezon}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--div")
    ap.add_argument("--add-url")
    ap.add_argument("--name", default="")
    ap.add_argument("--excel", action="store_true")
    a = ap.parse_args()
    if a.add_url:
        if not a.div:
            raise SystemExit("--add-url ile birlikte --div (örn. SP1) ver")
        add_url(a.add_url, a.div, a.name)
        return
    cfg = pd.read_csv(LEAGUES)
    cfg = cfg[cfg.enabled == 1]
    if a.div:
        cfg = cfg[cfg["div"] == a.div]
    today = str(date.today())
    SNAPS.mkdir(parents=True, exist_ok=True)
    hist = pd.read_csv(HISTORY) if HISTORY.exists() else pd.DataFrame()
    for r in cfg.itertuples():
        print(f"{r.div} ({r.name}) lig={r.league_id} sezon={r.season_id}")
        df, hatalar = collect(r.div, r.league_id, r.season_id, today)
        if df.empty:
            print("  hiç veri gelmedi, atlandı")
            continue
        mp = map_names(df, r.div)
        df["fd_name"] = df.team.map(mp)
        eksik = sorted(t for t, f in mp.items() if not f)
        if eksik:
            print("  [uyarı] eşleşmeyen takımlar (data/fotmob/team_names.csv'ye ekle):", eksik)
        hist = pd.concat([hist, df], ignore_index=True).drop_duplicates(
            subset=["date", "div", "team", "stat"], keep="last")
        w = wide(df)
        w.insert(0, "fd_name", w.index.map(mp))
        w.to_csv(SNAPS / f"{r.div}_{today}.csv", encoding="utf-8-sig")
        if a.excel:
            w.to_excel(SNAPS / f"{r.div}_{today}.xlsx")
        print(f"  Tamam: {len(w)} takım, {len(hatalar)} istatistik alınamadı {hatalar or ''}")
    hist.to_csv(HISTORY, index=False)
    print("Geçmiş:", len(hist), "satır,", hist.date.nunique(), "farklı tarih")


if __name__ == "__main__":
    main()
