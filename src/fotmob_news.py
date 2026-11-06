"""FotMob haber akışı: son haberleri çeker, takım adına göre filtreler.

Kullanım:
  python fotmob_news.py                    # son ~10 sayfayı çek, data/fotmob/news_history.csv'ye ekle
  python fotmob_news.py --pages 20         # daha geriye git (sayfa başına 20 haber, ~5 saat)
  python fotmob_news.py --team "Man United"  # o takımın son haberlerini yazdır (tüm aliaslar)

NOT: Genel (dünya) haber akışı; takıma özel akış değil. Başlık + kısa özet tutulur. Haberler İngilizce.
Resmi olmayan uç nokta (www.fotmob.com/api/worldnews), değişebilir. Her çalıştırma 10 istektir.
"""
import argparse
import re
import time
import unicodedata

import pandas as pd
import requests

from config import ROOT

DIR = ROOT / "data" / "fotmob"
HISTORY = DIR / "news_history.csv"
URL = "https://www.fotmob.com/api/worldnews?lang=en&page={p}"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; kisisel-arastirma-betigi)"}

# Haberlerde sık geçen kısaltmalar (takım adı -> ek aliaslar)
EXTRA = {
    "man united": ["manchester united", "man utd", "red devils"], "man city": ["manchester city"],
    "tottenham": ["spurs", "tottenham hotspur"], "ath madrid": ["atletico madrid", "atletico", "atleti"],
    "barcelona": ["barca", "fc barcelona"], "bayern munich": ["bayern"], "paris sg": ["psg", "paris saint-germain"],
    "ein frankfurt": ["eintracht frankfurt"], "m'gladbach": ["monchengladbach", "gladbach"],
    "leverkusen": ["bayer leverkusen"], "dortmund": ["borussia dortmund"], "inter": ["inter milan", "internazionale"],
    "milan": ["ac milan"], "nott'm forest": ["nottingham forest"], "real madrid": ["real madrid", "los blancos"],
    "galatasaray": ["gala"], "fenerbahce": ["fener"], "besiktas": ["bjk"], "buyuksehyr": ["basaksehir", "istanbul basaksehir"],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s).replace("ı", "i").replace("İ", "I")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' -]", " ", s)).strip()


def fetch_pages(n):
    rows = []
    for p in range(1, n + 1):
        try:
            r = requests.get(URL.format(p=p), headers=HEADERS, timeout=20)
            r.raise_for_status()
            rows += r.json()
        except Exception as e:  # noqa: BLE001
            print(f"  sayfa {p} alınamadı: {type(e).__name__}")
            break
        time.sleep(0.8)
    return rows


def update(n=10):
    DIR.mkdir(parents=True, exist_ok=True)
    rows = fetch_pages(n)
    new = pd.DataFrame([{"id": x["id"], "gmtTime": x["gmtTime"], "source": x.get("sourceStr"), "title": x["title"],
                         "lead": x.get("lead")} for x in rows])
    old = pd.read_csv(HISTORY) if HISTORY.exists() else pd.DataFrame()
    h = pd.concat([old, new], ignore_index=True).drop_duplicates(subset=["id"], keep="last")
    h = h.sort_values("gmtTime", ascending=False)
    h.to_csv(HISTORY, index=False)
    return h, len(new)


def aliases(team: str):
    """Bir takım için aranacak ifadeler (hepsi normalize). Çok kısa/belirsizler dışarıda."""
    t = norm(team)
    out = {t, *EXTRA.get(t, [])}
    return sorted(a for a in (norm(x) for x in out) if len(a) >= 4)


def for_team(h: pd.DataFrame, team: str, days=5, limit=6):
    cut = (pd.Timestamp.utcnow() - pd.Timedelta(days=days)).tz_localize(None) if pd.Timestamp.utcnow().tzinfo else pd.Timestamp.utcnow() - pd.Timedelta(days=days)
    al = aliases(team)
    res = []
    for r in h.itertuples():
        if pd.Timestamp(r.gmtTime).tz_localize(None) < cut:
            continue
        text = norm(f"{r.title} {r.lead if isinstance(r.lead, str) else ''}")
        if any(re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", text) for a in al):
            res.append({"zaman": str(r.gmtTime)[:16], "kaynak": r.source, "baslik": r.title,
                        "ozet": r.lead if isinstance(r.lead, str) else ""})
        if len(res) >= limit:
            break
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=10)
    ap.add_argument("--team")
    a = ap.parse_args()
    h, n = update(a.pages)
    print(f"{n} haber çekildi, geçmişte toplam {len(h)}; en yeni {h.gmtTime.iloc[0]}, en eski {h.gmtTime.iloc[-1]}")
    if a.team:
        for x in for_team(h, a.team):
            print(f"- [{x['zaman']}] {x['kaynak']}: {x['baslik']}\n    {x['ozet'][:200]}")
