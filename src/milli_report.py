"""Milli maç tahminlerinin sonuç özeti (kulüp defterinden AYRI).

predictions/milli_<tarih>.csv içindeki hg, ag sütunlarını (ev ve deplasman golü) maçlar bitince elle doldur
(kaynak: UEFA / Wikipedia; ESPN paketi bu maçları vermiyor). Sonra:
    python milli_report.py ../predictions/milli_2026-11-13.csv
Yön isabeti, çifte şans isabeti (Yüksek güvende tek) ve güvene göre dökümü yazar. 100 maçtan az örnekte yorum çıkarma.
"""
import sys

import pandas as pd

df = pd.read_csv(sys.argv[1], dtype={"pick": str, "oynanacak": str})
d = df[df.hg.notna() & df.ag.notna()].copy()
print(f"Toplam {len(df)} maç, sonuçlanan {len(d)}")
if d.empty:
    raise SystemExit("hg/ag sütunlarını doldur.")
d["res"] = d.apply(lambda r: "1" if r.hg > r.ag else "X" if r.hg == r.ag else "2", axis=1)
d["yon"] = d.res == d.pick
d["oy"] = d.apply(lambda r: r.res == r.pick if r.oynanacak == "tek" else r.res in r.oynanacak, axis=1)
print(f"Yön: {int(d.yon.sum())}/{len(d)} | Oynanacak seçim: {int(d.oy.sum())}/{len(d)}")
for c, g in d.groupby("conf"):
    print(f"  {c}: yön {int(g.yon.sum())}/{len(g)}, oynanacak {int(g.oy.sum())}/{len(g)}")
print(d[["home", "away", "pick", "conf", "oynanacak", "hg", "ag", "yon", "oy"]].to_string(index=False))
