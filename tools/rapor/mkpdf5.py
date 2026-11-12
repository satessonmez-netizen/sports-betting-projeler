import sys, html
src=open("tools/rapor/mkpdf2.py").read().split('body="";cur=None')[0]
exec(src)
LEG={"Brighton":("1X",1.13,"%76"),"Napoli":("X2",1.41,"%63"),"Monza":("X2",1.19,"%73"),"Inter":("1X",1.16,"%74"),"Rennes":("X2",1.47,"%60")}
body="";cur=None
for h,(lg,t,o,k) in C.items():
    r=rows[h]
    if lg!=cur:
        if cur: body+="</table>"
        body+=f"<h2>{lg}</h2><table><tr><th>Maç</th><th>Tahmin</th><th>Güven</th><th>Olasılık 1/X/2</th><th>Skor</th><th>Tercih</th><th>Oran</th><th>Kupon</th></tr>";cur=lg
    cls="hi" if r["conf"]=="Yüksek" else ("mid" if r["conf"]=="Orta" else "lo")
    mark=("⭐ "+LEG[h][0]) if h in LEG else ""
    body+=f"<tr><td>{html.escape(n(h))} – {html.escape(n(r['away']))}</td><td class='c k'>{r['pick']}</td><td class='c {cls}'>{r['conf']}</td><td class=c>%{'/'.join(str(round(float(r[x])*100)) for x in ('pH','pD','pA'))}</td><td class=c>{r['score']}</td><td class='c k'>{t}</td><td class=c>{o:.2f}</td><td class='c k'>{mark}</td></tr>"
body+="</table>"
tot=1.0
legrows=""
names={"Brighton":"Brighton – Brentford","Napoli":"Napoli – Lazio","Monza":"AC Monza – Atalanta","Inter":"Inter – Como","Rennes":"Rennes – Lille"}
why={"Brighton":"Brighton formda (12 puan), Brentford 8; hata payı yüksek ama beraberlik de kapsanıyor.","Napoli":"Lazio lider, Napoli Avrupa'da 1-4 yedi; Lazio ya da beraberlik.","Monza":"Monza 18., Atalanta kadro kalitesi; Atalanta ya da beraberlik.","Inter":"Inter xG +1.65 ama Avrupa'da kaybetti, Como formda; Inter ya da beraberlik.","Rennes":"Lille 2., Rennes 5.; Lille ya da beraberlik."}
for h,(s,o,p) in LEG.items():
    tot*=o
    legrows+=f"<tr><td>{names[h]}</td><td class='c k'>{s}</td><td class=c>{o:.2f}</td><td class=c>{p}</td><td>{why[h]}</td></tr>"
doc=f"""<!doctype html><html lang=tr><meta charset=utf-8><title>Tahminler ve kupon</title><style>
body{{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;font-size:11px;margin:0}}
h1{{font-size:18px;margin:0 0 4px}} h2{{font-size:13px;margin:14px 0 4px;color:#1f4e79}}
.sub{{color:#555;margin-bottom:8px}} table{{width:100%;border-collapse:collapse;break-inside:avoid}}
th{{background:#1f4e79;color:#fff;text-align:left;padding:4px 6px;font-size:10px}} td{{padding:4px 6px;border-bottom:1px solid #ddd;vertical-align:top}}
.c{{text-align:center;white-space:nowrap}} .k{{font-weight:bold;background:#eef4fa}} .hi{{color:#0b7a2b;font-weight:bold}} .mid{{color:#9a6a00}} .lo{{color:#b00020}}
.box{{margin-top:12px;padding:9px 11px;border:1px solid #1f4e79;background:#f5f9fd;line-height:1.5}} .warn{{margin-top:10px;padding:9px 11px;border:1px solid #b00020;background:#fff6f6;line-height:1.5;font-size:10.5px}}
.pb{{break-before:page}}
</style><h1>8 Kasım 2026 · Kupon tercihleri (oranlı, 28 maç)</h1>
<div class=sub>Tercih: tek ya da çifte şans, beklenen getirisi daha iyi olan. Oranlar ekran görüntüsündeki canlı bülten değerleri. ⭐ = 5 maçlık kuponda yer alıyor (yanındaki seçim, kuponda oynanan çifte şans).</div>
{body}
<div class=pb></div>
<h1>5 maçlık kupon · risk ve getiri dengesi</h1>
<div class=sub>Kural: her bacakta olasılığım %55 üstü, toplam kazanma ihtimali en az %15 olacak şekilde, beklenen getirisi en yüksek 5 bacak.</div>
<table><tr><th>Maç</th><th>Seçim</th><th>Oran</th><th>İhtimal</th><th>Gerekçe</th></tr>{legrows}</table>
<div class=box><b>Toplam oran:</b> {tot:.2f} · <b>Tutma ihtimali:</b> yaklaşık %16 (6'da 1) · <b>100 dolar yatırılırsa:</b> tutarsa ≈ {100*tot:.0f} dolar döner (+{100*tot-100:.0f}), tutmazsa 100 dolar gider.<br>
<b>Beklenen sonuç:</b> yaklaşık −%49 (100 dolarlık kuponda ortalama −49 dolar).</div>
<div class=box><b>Neden çifte şanslar?</b> Beş bacağın hepsi birden tutmalı. Tekli seçimlerde (örn. Napoli – Lazio 2 @2.59) ihtimal çok düşer (%1-2). Çifte şansta bacak başına ihtimal %60-76, kupon ihtimali %16. Oranlar düşük olduğu için getiri de küçük (3.23).<br>
<b>Daha riskli alternatif:</b> Brighton yerine Angers – Nice 1X (1.56) koyarsam oran 4.46, ihtimal %12, beklenen getiri −%48. Pek fark etmiyor.</div>
<div class=warn><b>Dürüst uyarı:</b> Bahisçi payı bu oranlarda yaklaşık %15-18 ve her bacakta çarpılıyor. Hangi 5 maçı seçersem seçeyim, beklenen getiri −%45 civarı. En güvendiğim maçları seçmek bile bunu değiştirmiyor, sadece kupon tutma ihtimalini artırıyor. Gerçek parayla oynamazdım. Bu bir bahis önerisi değil, tahmin kalitesini ölçen projenin kağıt üstü bir parçası. 5 maç sonucu hiçbir şeyi ispatlamaz.</div></html>"""
open(sys.argv[1],"w",encoding="utf-8").write(doc)
print(round(tot,2))
