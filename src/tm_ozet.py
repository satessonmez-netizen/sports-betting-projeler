"""Transfermarkt KOMPAKT özeti (kulüp maçları): takım başına kadro değeri + sakat/ceza listesi. KENDİ bilgisayarından çalıştır.

Kullanım:  py tm_ozet.py ..\\matches_2026-11-21b.txt
match_pack.py'nin yüzlerce satırlık çıktısı yerine takım başına 1-3 satır üretir (yapıştırması kolay).
Çıktı: ekrana ve output\\tm_ozet_<tarih>.txt dosyasına. Kimlik kontrolü: sayfa başlığı takım adıyla uyuşmuyorsa UYARI yazar.
"""
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

import tm_scraper
from config import ROOT


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def title_of(info):
    m = re.search(r"verein/(\d+)", info.get("tm", ""))
    if not m:
        return ""
    p = tm_scraper.CACHE / f"squad_{m.group(1)}.html"
    if not p.exists():
        return ""
    soup = BeautifulSoup(p.read_text(encoding="utf-8"), "lxml")
    return soup.title.get_text(strip=True) if soup.title else ""


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Kullanım: py tm_ozet.py ..\\matches_2026-11-21b.txt")
    div_of = {}
    d = tm_scraper._clubs()
    for r in d.itertuples():
        div_of.setdefault(r.fd_name, r.div)
    teams = []
    for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rest = line.split("|", 1)[1].strip() if "|" in line else line
        for t in re.split(r"\s+-\s+", rest):
            if t.strip() not in teams:
                teams.append(t.strip())
    print(f"{len(teams)} takım. Her takım ~10-15 sn, toplam {len(teams) * 12 // 60} dk civarı. Ctrl+C yapma.\n")
    out = []
    for t in teams:
        info = tm_scraper.club_info(t, div_of.get(t, "?"))
        if info.get("hata"):
            line = f"{t} | HATA: {info['hata']}"
        else:
            ti = title_of(info)
            warn = "" if (not ti or norm(t)[:5] in norm(ti) or norm(info.get("takım", ""))[:5] in norm(ti)) else f" | UYARI_kimlik: sayfa '{ti}'"
            inj = []
            for i in info.get("sakat_ceza_listesi", []):
                cells = [c for c in i["cells"][1:] if c]
                inj.append(f"{i['name']} ({i.get('mevki') or ''} {round((i.get('değer') or 0) / 1e6, 1)}M€: {', '.join(cells)})")
            line = (f"{t} | kadro {info.get('kadro_değeri_milyon_€')}M€ | eksik %{info.get('eksiklerin_kadro_payı_%')} "
                    f"(ağırlıklı {info.get('ağırlıklı_eksik_payı')}) | " + ("; ".join(inj) if inj else "eksik yok") + warn)
        print(line)
        out.append(line)
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    f = out_dir / f"tm_ozet_{date.today()}.txt"
    f.write_text("\n".join(out), encoding="utf-8")
    print(f"\nHazır: {f}\nBu dosyanın içeriğini bana yapıştır.")


if __name__ == "__main__":
    main()
