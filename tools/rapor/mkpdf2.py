import csv, html, sys
rows={r["home"]:r for r in csv.DictReader(open("predictions/picks_2026-11-08_noTM.csv",encoding="utf-8"))}
C={ # home: (liga, tercih, oran, kupon)
"Rizespor":("Süper Lig","1X",1.12,""),"Corum":("Süper Lig","X2",1.08,""),"Alanyaspor":("Süper Lig","2",1.45,""),"Besiktas":("Süper Lig","1",1.07,""),
"Brighton":("İngiltere","1X",1.13,""),"Crystal Palace":("İngiltere","2",1.41,""),"Sunderland":("İngiltere","2",1.74,""),"Ipswich":("İngiltere","2",1.69,""),"Man United":("İngiltere","1X",1.21,""),
"Elche":("İspanya","X2",1.16,""),"Sociedad":("İspanya","1X",1.09,""),"Villarreal":("İspanya","1",1.27,""),"Celta":("İspanya","1X",1.10,""),"Ath Madrid":("İspanya","X2",1.14,""),
"Napoli":("İtalya","2",2.59,"✅"),"Monza":("İtalya","2",1.85,"yedek"),"Genoa":("İtalya","X2",1.08,""),"Inter":("İtalya","1",1.70,""),"Fiorentina":("İtalya","2",1.91,""),
"FC Koln":("Almanya","X2",1.14,""),"Freiburg":("Almanya","1",1.33,""),"Hoffenheim":("Almanya","1",1.42,""),
"Rennes":("Fransa","2",2.80,"✅"),"Le Mans":("Fransa","X2",1.08,""),"Le Havre":("Fransa","X2",1.23,""),"Brest":("Fransa","X2",1.28,""),"Angers":("Fransa","X2",1.16,""),"Lens":("Fransa","1X",1.28,"")}
nice={"Corum":"Çorum","Besiktas":"Beşiktaş","Genclerbirligi":"Gençlerbirliği","Fenerbahce":"Fenerbahçe","FC Koln":"Köln","Ath Madrid":"Atlético Madrid","Sociedad":"Real Sociedad","Vallecano":"Rayo Vallecano","Betis":"Real Betis","Celta":"Celta Vigo","Milan":"AC Milan","Monza":"AC Monza"}
n=lambda x:nice.get(x,x)
body="";cur=None
for h,(lg,t,o,k) in C.items():
    r=rows[h]
    if lg!=cur:
        if cur: body+="</table>"
        body+=f"<h2>{lg}</h2><table><tr><th>Maç</th><th>Tek tahmin</th><th>Güven</th><th>Tercih</th><th>Oran</th><th>Kupon</th></tr>";cur=lg
    cls="hi" if r["conf"]=="Yüksek" else ("mid" if r["conf"]=="Orta" else "lo")
    body+=f"<tr><td>{html.escape(n(h))} – {html.escape(n(r['away']))}</td><td class=c>{r['pick']}</td><td class='c {cls}'>{r['conf']}</td><td class='c k'>{t}</td><td class=c>{o:.2f}</td><td class='c k'>{k}</td></tr>"
body+="</table>"
doc=f"""<!doctype html><html lang=tr><meta charset=utf-8><title>Kupon tercihleri</title><style>
body{{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;font-size:11px;margin:0}}
h1{{font-size:18px;margin:0 0 4px}} h2{{font-size:13px;margin:14px 0 4px;color:#1f4e79}}
.sub{{color:#555;margin-bottom:8px}} table{{width:100%;border-collapse:collapse;break-inside:avoid}}
th{{background:#1f4e79;color:#fff;text-align:left;padding:4px 6px;font-size:10px}} td{{padding:4px 6px;border-bottom:1px solid #ddd}}
.c{{text-align:center}} .k{{font-weight:bold;background:#eef4fa}} .hi{{color:#0b7a2b;font-weight:bold}} .mid{{color:#9a6a00}} .lo{{color:#b00020}}
.box{{margin-top:14px;padding:8px 10px;border:1px solid #1f4e79;background:#f5f9fd}} .note{{margin-top:10px;font-size:10px;color:#444;border-top:1px solid #ccc;padding-top:6px}}
</style><h1>8 Kasım 2026 · Kupon tercihleri (oranlı)</h1>
<div class=sub>28 maç (Süper Lig + 5 büyük lig). Tercih: tek ya da çifte şans, beklenen getirisi daha iyi olan. Oranlar ekran görüntüsündeki canlı bülten değerleri.</div>
{body}
<div class=box><b>Kuponum:</b> Napoli – Lazio: 2 (2.59) + Rennes – Lille: 2 (2.80) · toplam oran ≈ 7.2 · yedek: Monza – Atalanta 2 (1.85).</div>
<div class=note><b>Dürüst notlar:</b> (1) Bu oranlarda bahisçi payı yaklaşık %15-18, her seçeneğin beklenen getirisi en az −%7, çoğu −%15 ve altı. Artıya geçen bahis yok. (2) Çifte şans oranları 1.05-1.30 civarı, payı tekliden büyük. (3) Seçtiğim iki maçta piyasadan farklı düşünüyorum, piyasa tarihsel olarak benden iyi. (4) Gerçek parayla oynamazdım, bu bir kâğıt üstü egzersizdir. Örnek sayısı küçüktür, sonuç çıkarılamaz.</div></html>"""
open(sys.argv[1],"w",encoding="utf-8").write(doc)
