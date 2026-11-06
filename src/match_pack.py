"""Haftalık maç paketi hazırlayıcı.

Kullanım (kendi bilgisayarında):
    python match_pack.py ../matches.txt            # CSV + model + Transfermarkt
    python match_pack.py ../matches.txt --no-tm    # Transfermarkt'sız (sadece CSV ve model)

matches.txt: her satıra bir maç, "Ev Sahibi - Deplasman" biçiminde (football-data'daki takım adları,
örn. "Galatasaray - Amedspor"). İsteğe bağlı tarih: "2026-11-07 | Galatasaray - Amedspor".
Çıktı: output/match_pack_<tarih>.md  (bu dosyanın içeriğini bana yapıştır)
"""
import argparse
import difflib
import json
import re
import sys
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

import elo
from config import ROOT
from data import load
from metrics import outcome
from model import DixonColes

warnings.filterwarnings("ignore")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("ı", "i").replace("ş", "s").replace("ğ", "g")
                  .replace("ü", "u").replace("ö", "o").replace("ç", "c"))


def resolve(name: str, names: list[str]) -> str:
    n = norm(name)
    exact = [x for x in names if norm(x) == n]
    if exact:
        return exact[0]
    part = [x for x in names if n in norm(x) or norm(x) in n]
    if len(part) == 1:
        return part[0]
    close = difflib.get_close_matches(name, names, n=3, cutoff=0.5)
    raise SystemExit(f"Takım bulunamadı/belirsiz: '{name}'. Yakın adaylar: {close or part[:5]}")


def parse_matches(path: str, names: list[str]) -> list[dict]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        when = None
        if "|" in line:
            when, line = [x.strip() for x in line.split("|", 1)]
        parts = re.split(r"\s+-\s+|\s+vs\.?\s+|\s*[;,]\s*|\s*–\s*", line)
        if len(parts) != 2:
            raise SystemExit(f"Satır anlaşılamadı: '{line}'. Biçim: Ev - Deplasman")
        out.append({"date": when, "home": resolve(parts[0], names), "away": resolve(parts[1], names)})
    return out


def form(h: pd.DataFrame, team: str, now: pd.Timestamp, n: int):
    g = h[((h.home == team) | (h.away == team)) & (h.date < now)].tail(n)
    s, gf, ga, pts = "", 0, 0, 0
    for r in g.itertuples():
        mine, opp = (r.hg, r.ag) if r.home == team else (r.ag, r.hg)
        gf += mine; ga += opp
        res = "G" if mine > opp else "B" if mine == opp else "M"
        pts += 3 if res == "G" else 1 if res == "B" else 0
        s += res
    return {"son": s, "puan": pts, "atılan": int(gf), "yenen": int(ga), "maç": len(g)}


def record(h, team, now, years=5):
    g = h[((h.home == team) | (h.away == team)) & (h.date < now) & (h.date >= now - pd.Timedelta(days=365 * years))]
    w = d = l = gf = ga = 0
    for r in g.itertuples():
        mine, opp = (r.hg, r.ag) if r.home == team else (r.ag, r.hg)
        gf += mine; ga += opp
        w += mine > opp; d += mine == opp; l += mine < opp
    return {"maç": len(g), "G": int(w), "B": int(d), "M": int(l), "atılan": int(gf), "yenen": int(ga)}


def h2h(h, a, b, now, years=5):
    g = h[(((h.home == a) & (h.away == b)) | ((h.home == b) & (h.away == a)))
          & (h.date < now) & (h.date >= now - pd.Timedelta(days=365 * years))]
    return [f"{r.date.date()} {r.home} {int(r.hg)}-{int(r.ag)} {r.away}" for r in g.itertuples()]


def model_probs(h_all, div, home, away, now):
    lg = h_all[h_all["div"] == div].reset_index(drop=True)
    tr = lg[lg.date >= now - pd.Timedelta(days=365 * 4)]
    m = DixonColes().fit(tr, now)
    p = m.predict(home, away)
    diffs, r = elo.compute(lg)
    win = (lg.date >= now - pd.Timedelta(days=365 * 4)).to_numpy()
    eb, ec = elo.fit_map(diffs[win], outcome(lg.hg.to_numpy(), lg.ag.to_numpy())[win])
    e = elo.probs([r.get(home, elo.NEW_START) + elo.HFA - r.get(away, elo.NEW_START)], eb, ec)[0]
    mix = [0.5 * p[k] + 0.5 * v for k, v in zip(("pH", "pD", "pA"), e)]
    mx = m.score_matrix(home, away)
    idx = np.dstack(np.unravel_index(np.argsort(-mx.ravel())[:5], mx.shape))[0]
    return {
        "1": round(mix[0], 3), "X": round(mix[1], 3), "2": round(mix[2], 3),
        "dc": [round(p[k], 3) for k in ("pH", "pD", "pA")], "elo": [round(float(x), 3) for x in e],
        "beklenen_gol": [round(p["xgH"], 2), round(p["xgA"], 2)],
        "ust_2.5": round(p["pOver25"], 3), "kg_var": round(p["pBTTS"], 3),
        "en_olası_skorlar": [[int(i), int(j), round(float(mx[i, j]), 3)] for i, j in idx],
        "elo_puanı": [round(r.get(home, elo.NEW_START)), round(r.get(away, elo.NEW_START))],
        "takım_maç_sayısı_eğitimde": [int(((tr.home == t) | (tr.away == t)).sum()) for t in (home, away)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("matches")
    ap.add_argument("--no-tm", action="store_true")
    ap.add_argument("--no-download", action="store_true", help="CSV'leri yeniden indirme")
    a = ap.parse_args()
    if not a.no_download:
        from data import download
        download()
    d = load()
    played = d[d.hg.notna()]
    recent = d[d.date >= "2025-07-01"]
    names = sorted(set(recent.home) | set(recent.away))
    div_of = {}
    for r in recent.itertuples():
        div_of[r.home] = r.div; div_of[r.away] = r.div
    matches = parse_matches(a.matches, names)
    try:  # yaklaşan maçların oranları (football-data fixtures.csv); alınamazsa oransız devam
        from predict import upcoming
        fixtures = upcoming()
    except Exception as e:  # noqa: BLE001
        print("  [uyarı] yaklaşan maç oranları alınamadı:", type(e).__name__)
        fixtures = None
    pack = []
    for m in matches:
        div = div_of[m["home"]]
        if div_of[m["away"]] != div:
            raise SystemExit(f"{m['home']} ve {m['away']} farklı liglerde, desteklenmiyor.")
        now = pd.Timestamp(m["date"]) if m["date"] else pd.Timestamp.today().normalize()
        h = played[played["div"] == div]
        print(f"→ {m['home']} - {m['away']} ({div})")
        entry = {"maç": f"{m['home']} - {m['away']}", "lig": div, "tarih": str(now.date()),
                 "model": model_probs(played, div, m["home"], m["away"], now),
                 "form_son5": {t: form(h, t, now, 5) for t in (m["home"], m["away"])},
                 "form_son10_hafta": {t: form(h[h.date >= now - pd.Timedelta(days=70)], t, now, 99)
                                      for t in (m["home"], m["away"])},
                 "son5yıl": {t: record(h, t, now) for t in (m["home"], m["away"])},
                 "karşılıklı_son5yıl": h2h(h, m["home"], m["away"], now)}
        o = fixtures[(fixtures.home == m["home"]) & (fixtures.away == m["away"])] if fixtures is not None else []
        if len(o) and pd.notna(o.iloc[0].oH):
            r = o.iloc[0]
            inv = np.array([1 / r.oH, 1 / r.oD, 1 / r.oA]); inv = inv / inv.sum()
            entry["piyasa_oranları"] = [r.oH, r.oD, r.oA]
            entry["piyasa_olasılığı"] = [round(float(x), 3) for x in inv]
        if not a.no_tm:
            import tm_scraper
            entry["transfermarkt"] = {t: tm_scraper.club_info(t, div) for t in (m["home"], m["away"])}
        pack.append(entry)
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    stem = out_dir / f"match_pack_{date.today()}"
    stem.with_suffix(".json").write_text(json.dumps(pack, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    md = "# Maç paketi " + str(date.today()) + "\n\n```json\n" + json.dumps(pack, ensure_ascii=False, indent=1, default=str) + "\n```\n"
    stem.with_suffix(".md").write_text(md, encoding="utf-8")
    print(f"\nHazır: {stem.with_suffix('.md')}\nBu dosyanın içeriğini bana yapıştır.")


if __name__ == "__main__":
    main()
