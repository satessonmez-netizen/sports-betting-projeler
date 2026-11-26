import sys
B=[("Napoli – Lazio","14:30","2 (Lazio)",2.59,"Lazio lider, 5/5 formda. Napoli Avrupa'da 1-4 yedi. Bu listedeki en iyi beklenen getiri (−%7)."),
("Rennes – Lille","17:00","2 (Lille)",2.80,"Lille 2., Rennes 5. Beklenen getiri −%7. Piyasaya karşı seçim."),
("AC Monza – Atalanta","17:00","2 (Atalanta)",1.85,"Ben ve piyasa neredeyse aynı yerdeyiz. Beklenen getiri −%13."),
("Inter – Como","20:00","1 (Inter)",1.70,"Ben ve piyasa aynı (%50). Como formda, Inter Avrupa'da kaybetti. Beklenen getiri −%15."),
("Fiorentina – Juventus","22:45","2 (Juventus)",1.91,"Ben ve piyasa aynı (%45). Fiorentina 17., Juve daha iyi. Beklenen getiri −%15.")]
rows="".join(f"<tr><td>{m}</td><td class=c>{t}</td><td class='c k'>{s}</td><td class=c>{o:.2f}</td><td class=c>100 $</td><td class=c>{100*o:.0f} $</td><td>{n}</td></tr>" for m,t,s,o,n in B)
doc=f"""<!doctype html><html lang=tr><meta charset=utf-8><title>5 maç bahsi</title><style>
body{{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;font-size:12px;margin:0}} h1{{font-size:19px;margin:0 0 4px}}
.sub{{color:#555;margin-bottom:12px}} table{{width:100%;border-collapse:collapse}}
th{{background:#1f4e79;color:#fff;text-align:left;padding:6px;font-size:11px}} td{{padding:7px 6px;border-bottom:1px solid #ddd;vertical-align:top}}
.c{{text-align:center;white-space:nowrap}} .k{{font-weight:bold;background:#eef4fa}}
.box{{margin-top:14px;padding:10px 12px;border:1px solid #1f4e79;background:#f5f9fd;line-height:1.5}}
.warn{{margin-top:12px;padding:10px 12px;border:1px solid #b00020;background:#fff6f6;line-height:1.5}}
</style><h1>Varsayımsal 5 maç bahsi · 8 Kasım 2026</h1>
<div class=sub>"Zorunlu 5 maç" egzersizi: 10.000 dolarlık bütçeden tekli bahisler, kağıt üstü. Oranlar canlı bülten değerleri.</div>
<table><tr><th>Maç</th><th>Saat (TR)</th><th>Seçim</th><th>Oran</th><th>Tutar</th><th>Tutarsa dönüş</th><th>Gerekçe</th></tr>{rows}</table>
<div class=box><b>Toplam yatırım:</b> 500 dolar (bütçenin %5'i), geri kalanı kenarda. <b>Beklenen sonuç:</b> yaklaşık −55 dolar (−%11). Kombine yapılmadı, her maç ayrı.</div>
<div class=warn><b>Dürüst uyarı:</b> Bu oranlarda bahisçi payı yaklaşık %15-18. 28 maçın hiçbirinde beklenen getiri artıda değil, bu 5 maç "en az kötü" olanlar. Gerçekten karar verecek olsam oynamazdım. Bu bir bahis önerisi değil, tahmin kalitesini ölçen projenin kağıt üstü bir parçası. Beş maç çok küçük bir örnektir, sonuç ne olursa olsun bir şey ispatlamaz.</div></html>"""
open(sys.argv[1],"w",encoding="utf-8").write(doc)
