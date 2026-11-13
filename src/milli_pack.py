"""Milli takım maçları için Transfermarkt paketi (kadro değeri + sakat/cezalı). KENDİ bilgisayarından çalıştır.

Kullanım:  py milli_pack.py ..\\matches_2026-11-13_milli.txt
Model yok: milli takımlar için geçmiş veri/güç puanı sistemde bulunmuyor. Sadece Transfermarkt bilgisi toplanır.
Takım adları data/tm_clubs.csv içindeki 'NT' satırlarındaki gibi yazılmalı (France, Turkey, Czech Republic ...).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

import tm_scraper
from config import ROOT


def check_identity(team: str, info: dict) -> None:
    """Çekilen sayfanın gerçekten bu milli takıma ait olduğunu doğrula (yanlış kimlik = yanlış veri)."""
    c = tm_scraper._clubs()
    r = c[(c.fd_name == team) & (c["div"] == "NT")].iloc[0]
    p = tm_scraper.CACHE / f"squad_{int(r.tm_id)}.html"
    if not p.exists():
        return
    soup = BeautifulSoup(p.read_text(encoding="utf-8"), "lxml")
    title = (soup.title.get_text(strip=True) if soup.title else "")
    info["tm_sayfa_başlığı"] = title
    if not any(k.lower() in title.lower() for k in str(r.tm_name).split("|")):
        info["UYARI_kimlik"] = f"Sayfa başlığı '{title}' beklenen '{r.tm_name}' ile uyuşmuyor: veriyi KULLANMA, bana bildir."


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Kullanım: py milli_pack.py ..\\matches_2026-11-13_milli.txt")
    known = set(tm_scraper._clubs().query("div == 'NT'").fd_name)
    pack = []
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        when, rest = ([x.strip() for x in line.split("|", 1)] if "|" in line else (None, line))
        parts = re.split(r"\s+-\s+", rest)
        if len(parts) != 2:
            raise SystemExit(f"Satır anlaşılamadı: '{line}'. Biçim: 2026-11-15 | France - Turkey")
        for t in parts:
            if t not in known:
                raise SystemExit(f"Milli takım tabloda yok: '{t}'. Bilinenler: {sorted(known)}")
        print(f"→ {parts[0]} - {parts[1]}")
        entry = {"maç": f"{parts[0]} - {parts[1]}", "tarih": when, "transfermarkt": {}}
        for t in parts:
            info = tm_scraper.club_info(t, "NT")
            check_identity(t, info)
            entry["transfermarkt"][t] = info
        pack.append(entry)
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    stem = out / f"milli_pack_{date.today()}"
    stem.with_suffix(".json").write_text(json.dumps(pack, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    stem.with_suffix(".md").write_text("# Milli maç paketi " + str(date.today()) + "\n\n```json\n"
                                       + json.dumps(pack, ensure_ascii=False, indent=1, default=str) + "\n```\n", encoding="utf-8")
    print(f"\nHazır: {stem.with_suffix('.md')}\nBu dosyanın içeriğini bana yapıştır.")


if __name__ == "__main__":
    main()
