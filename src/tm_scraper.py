"""Transfermarkt'tan kadro değerleri ve sakatlık/ceza listesi çeker.

ÖNEMLİ:
- KENDİ bilgisayarından çalıştır. Bulut ortamından Transfermarkt'a erişilemiyor.
- Transfermarkt kullanım şartları otomatik çekimi kısıtlayabilir. Az istek at, aralara bekleme koy
  (varsayılan 4-7 sn) ve sonuçları önbelleğe al (data/tm_cache/, 12 saat geçerli).
- Sayfa yapısı değişirse seçiciler tutmayabilir. O durumda ham HTML data/tm_debug/ altına kaydedilir,
  o dosyayı bana gönder, seçicileri düzeltirim.
"""
import json
import random
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import ROOT

BASE = "https://www.transfermarkt.com"
CACHE = ROOT / "data" / "tm_cache"
DEBUG = ROOT / "data" / "tm_debug"
CLUBS_CSV = ROOT / "data" / "tm_clubs.csv"
MANUAL_CSV = ROOT / "data" / "tm_clubs_manual.csv"   # arama ile bulunanlar buraya kaydedilir
TTL_HOURS = 12
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


class TMBlocked(Exception):
    pass


def _sleep(lo=4.0, hi=7.0):
    time.sleep(random.uniform(lo, hi))


def fetch(url: str, key: str) -> str:
    """Önbellekli GET. 403/429 gelirse TMBlocked fırlatır (israr etmez)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (re.sub(r"[^a-z0-9]+", "_", key.lower()) + ".html")
    if p.exists() and (time.time() - p.stat().st_mtime) < TTL_HOURS * 3600:
        return p.read_text(encoding="utf-8")
    _sleep()
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code in (403, 429, 503):
        raise TMBlocked(f"HTTP {r.status_code} ({url}). Bir süre bekle ya da başka ağ dene.")
    r.raise_for_status()
    p.write_text(r.text, encoding="utf-8")
    return r.text


def parse_value(txt: str):
    """'€45.00m' -> 45_000_000, '€800k' -> 800_000, '-' -> None."""
    t = (txt or "").replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*(bn|m|k|th\.)?", t, re.I)
    if not m or "€" not in t and "£" not in t and "$" not in t:
        return None
    mult = {"bn": 1e9, "m": 1e6, "k": 1e3, "th.": 1e3}.get((m.group(2) or "").lower(), 1)
    return float(m.group(1)) * mult


def _debug(name: str, html: str):
    DEBUG.mkdir(parents=True, exist_ok=True)
    (DEBUG / f"{name}.html").write_text(html, encoding="utf-8")


def parse_squad(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    table = soup.select_one("table.items")
    out = []
    if not table:
        return out
    for tr in table.select("tbody > tr"):
        a = tr.select_one("td.hauptlink a")
        if not a:
            continue
        val = tr.select_one("td.rechts.hauptlink")
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td", recursive=False)]
        pos = tr.select_one("td.posrela table tr:nth-of-type(2) td")
        age = next((int(c) for c in cells if re.fullmatch(r"\d{2}", c)), None)
        out.append({"name": a.get_text(strip=True), "position": pos.get_text(strip=True) if pos else None,
                    "age": age, "value": parse_value(val.get_text(strip=True)) if val else None})
    return out


def parse_injuries(html: str) -> list[dict]:
    """Sakatlık ve ceza satırlarını ham hücre metinleriyle döndürür (sütun sırası siteye göre değişebilir)."""
    soup = BeautifulSoup(html, "lxml")
    out = []
    for table in soup.select("table.items"):
        for tr in table.select("tbody > tr"):
            a = tr.select_one("td.hauptlink a")
            if not a:
                continue
            cells = [c.get_text(" ", strip=True) for c in tr.find_all("td", recursive=False)]
            cells = [c for c in cells if c]
            # Gerçek sakatlık/ceza satırlarında tarih (başlangıç/bitiş) olur. Tarihi olmayan satırlar
            # farklı bir tablodan geliyor (ör. 3 sarı kart uyarısı gibi sayaçlar): 'diğer' olarak ayır.
            n_dates = sum(bool(re.search(r"\d{2}/\d{2}/\d{4}|[A-Z][a-z]{2} \d{1,2}, \d{4}", c)) for c in cells)
            out.append({"name": a.get_text(strip=True), "cells": cells,
                        "tür": "sakat_ceza" if n_dates >= 1 else "diğer"})
    return out


def _clubs() -> pd.DataFrame:
    frames = [pd.read_csv(CLUBS_CSV)]
    if MANUAL_CSV.exists():
        frames.append(pd.read_csv(MANUAL_CSV))
    return pd.concat(frames, ignore_index=True)


def find_club(fd_name: str, div: str):
    """(slug, id) döndürür. Tabloda yoksa Transfermarkt'ta arar ve ilk sonucu manuel tabloya yazar."""
    c = _clubs()
    hit = c[(c.fd_name == fd_name) & (c["div"] == div)]
    if len(hit):
        r = hit.iloc[0]
        return r.tm_slug, int(r.tm_id)
    q = fd_name.replace(".", "")
    html = fetch(f"{BASE}/schnellsuche/ergebnis/schnellsuche?query={requests.utils.quote(q)}", f"search_{q}")
    soup = BeautifulSoup(html, "lxml")
    for a in soup.select("table.items td.hauptlink a[href*='/verein/']"):
        m = re.search(r"/([^/]+)/startseite/verein/(\d+)", a["href"])
        if m:
            print(f"  [uyarı] '{fd_name}' aramayla bulundu: {a.get_text(strip=True)} -> {m.group(1)}/{m.group(2)}. "
                  f"Yanlışsa data/tm_clubs_manual.csv içinde düzelt.")
            row = pd.DataFrame([{"div": div, "fd_name": fd_name, "tm_slug": m.group(1),
                                 "tm_id": int(m.group(2)), "tm_name": a.get_text(strip=True)}])
            row.to_csv(MANUAL_CSV, mode="a", header=not MANUAL_CSV.exists(), index=False)
            return m.group(1), int(m.group(2))
    raise LookupError(f"'{fd_name}' Transfermarkt'ta bulunamadı. data/tm_clubs_manual.csv'ye elle ekle "
                      f"(sütunlar: div,fd_name,tm_slug,tm_id,tm_name).")


def club_info(fd_name: str, div: str) -> dict:
    """Bir kulüp için kadro değeri + sakatlık/ceza. Hata durumunda 'hata' alanı döner (çökmez)."""
    res = {"takım": fd_name}
    try:
        slug, cid = find_club(fd_name, div)
        res["tm"] = f"{BASE}/{slug}/startseite/verein/{cid}"
        sq_html = fetch(f"{BASE}/{slug}/kader/verein/{cid}/plus/1", f"squad_{cid}")
        squad = parse_squad(sq_html)
        if not squad:
            _debug(f"squad_{cid}", sq_html)
            res["hata_kadro"] = f"Kadro tablosu okunamadı. Ham HTML: data/tm_debug/squad_{cid}.html"
        inj_html = fetch(f"{BASE}/{slug}/sperrenundverletzungen/verein/{cid}", f"inj_{cid}")
        inj = parse_injuries(inj_html)
        if not inj and "table" not in inj_html.lower():
            _debug(f"inj_{cid}", inj_html)
            res["hata_sakatlik"] = f"Sakatlık tablosu okunamadı. Ham HTML: data/tm_debug/inj_{cid}.html"
        vals = {p["name"]: p["value"] for p in squad}
        for i in inj:
            i["değer"] = vals.get(i["name"])
        total = sum(v for v in vals.values() if v)
        inj_real = [i for i in inj if i["tür"] == "sakat_ceza"]
        inj_other = [i for i in inj if i["tür"] != "sakat_ceza"]
        out_val = sum(i["değer"] for i in inj_real if i.get("değer"))
        res.update({
            "kadro_değeri_milyon_€": round(total / 1e6, 1) if total else None,
            "en_değerli_5": sorted(([p["name"], round(p["value"] / 1e6, 1)] for p in squad if p["value"]),
                                   key=lambda x: -x[1])[:5],
            "oyuncu_sayısı": len(squad),
            "sakat_ceza_listesi": inj_real,
            "diğer_tablo_satırları_(muhtemelen_kart_uyarısı)": inj_other,
            "eksiklerin_değeri_milyon_€": round(out_val / 1e6, 1),
            "eksiklerin_kadro_payı_%": round(100 * out_val / total, 1) if total else None,
        })
    except TMBlocked as e:
        res["hata"] = f"ENGELLENDİ: {e}"
    except Exception as e:  # noqa: BLE001 - kullanıcıya anlaşılır hata göster
        res["hata"] = f"{type(e).__name__}: {e}"
    return res


if __name__ == "__main__":
    import sys
    print(json.dumps(club_info(sys.argv[1], sys.argv[2]), ensure_ascii=False, indent=2))
