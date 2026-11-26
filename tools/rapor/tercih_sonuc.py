import json,html,sys
import pandas as pd
src=open("tools/rapor/mkpdf2.py").read().split('body="";cur=None')[0]
exec(src)  # rows, C, n, nice
led=pd.read_csv("predictions/ledger.csv",dtype=str)
alias={"Caykur Rizespor":"Rizespor","Çorum FK":"Corum","Brighton & Hove Albion":"Brighton","Ipswich Town":"Ipswich","AFC Bournemouth":"Bournemouth","Manchester United":"Man United","Real Betis":"Betis","Real Sociedad":"Sociedad","Rayo Vallecano":"Vallecano","Celta Vigo":"Celta","Atlético Madrid":"Ath Madrid","AC Milan":"Milan","Internazionale":"Inter","FC Cologne":"FC Koln","Bayer Leverkusen":"Leverkusen","SC Freiburg":"Freiburg","1. FC Union Berlin":"Union Berlin","TSG Hoffenheim":"Hoffenheim","Stade Rennais":"Rennes","AS Monaco":"Monaco","Le Havre AC":"Le Havre","Erzurum BB":"Erzurumspor"}
esp={}
for e in json.load(open("/tmp/d_2026-11-08.json"))["data"]["events"]:
    c=e["competitors"];h=alias.get(c[0]["team"]["name"],c[0]["team"]["name"]);esp[h]=(int(c[0]["score"]),int(c[1]["score"]))
LEG={"Brighton":"1X","Napoli":"X2","Monza":"X2","Inter":"1X","Rennes":"X2"}
def res(hg,ag): return "1" if hg>ag else "X" if hg==ag else "2"
body="";cur=None;tot=hit=0;net=0.0;tek=[0,0,0.0];cs=[0,0,0.0];diff=[]
for h,(lg,t,o,k) in C.items():
    r=rows[h]
    L=led[(led.home==h)&(led.away==r["away"])&(led.date=="2026-11-08")].iloc[0]
    hg,ag=int(float(L.hg)),int(float(L.ag))
    if esp.get(h)!=(hg,ag): diff.append((h,esp.get(h),(hg,ag)))
    ok=res(hg,ag) in t
    pl=(o-1) if ok else -1.0
    tot+=1;hit+=ok;net+=pl
    g=tek if len(t)==1 else cs
    g[0]+=1;g[1]+=ok;g[2]+=pl
    if lg!=cur:
        if cur: body+="</table>"
        body+=f"<h2>{lg}</h2><table><tr><th>Maç</th><th>Tercih</th><th>Oran</th><th>Gerçek skor</th><th>Sonuç</th><th>Kâr/zarar (1 birim)</th><th>Kupon</th></tr>";cur=lg
    kup=""
    if h in LEG: kup=f"⭐ {LEG[h]} "+("✅" if res(hg,ag) in LEG[h] else "❌")
    body+=f"<tr><td>{html.escape(n(h))} – {html.escape(n(r['away']))}</td><td class='c k'>{t}</td><td class=c>{o:.2f}</td><td class=c><b>{hg}-{ag}</b></td><td class=c>{'✅' if ok else '❌'}</td><td class=c style='color:{'#0b7a2b' if ok else '#b00020'}'>{pl:+.2f}</td><td class=c>{kup}</td></tr>"
body+="</table>"
print("fark ESPN vs resmi:",diff)
oz=f"Tercihlerim: <b>{hit}/{tot} tuttu</b> · tek seçimler {tek[1]}/{tek[0]} (net {tek[2]:+.2f}), çifte şanslar {cs[1]}/{cs[0]} (net {cs[2]:+.2f}) · 1 birimlik tekli bahislerle toplam net <b>{net:+.2f} birim</b>"
doc=f"""<!doctype html><html lang=tr><meta charset=utf-8><title>Tercih ve gerçekleşen</title><style>
body{{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;font-size:10.5px;margin:0}} h1{{font-size:17px;margin:0 0 4px}} h2{{font-size:12.5px;margin:12px 0 4px;color:#1f4e79}}
.sub{{color:#555;margin-bottom:6px}} table{{width:100%;border-collapse:collapse}} tr{{break-inside:avoid}}
th{{background:#1f4e79;color:#fff;text-align:left;padding:4px 5px;font-size:9.5px}} td{{padding:4px 5px;border-bottom:1px solid #ddd}}
.c{{text-align:center;white-space:nowrap}} .k{{font-weight:bold;background:#eef4fa}}
.box{{margin:8px 0;padding:8px 10px;border:1px solid #1f4e79;background:#f5f9fd;line-height:1.55}} .note{{margin-top:10px;font-size:10px;color:#444;border-top:1px solid #ccc;padding-top:6px}}
</style><h1>8 Kasım 2026 · Tercihlerim ve gerçekleşen sonuçlar</h1>
<div class=sub>Skorlar football-data resmi CSV (ESPN ile aynı). Her tercih için 1 birim yatırılmış gibi kâğıt üstü hesap. ⭐ = 5'li kupon bacağı.</div>
<div class=box>{oz}<br><b>5'li çifte şans kuponu (oran 3.23): 5/5 TUTTU</b> · tekli 5 bahis (100 dolar): net +135 dolar · 43.6'lık kombine: tutmadı</div>
{body}
<div class=note><b>Dürüst not:</b> 28 maç çok az, şans payı büyük. Net kâr, tek haftalık bir tesadüf olabilir. Bahisçi payı yaklaşık %15-18 olduğu için uzun vadede beklenen sonuç eksidir. Çifte şans ödemeleri düşük olduğundan çok tutsa da toplam kâr küçük kalır. Gerçek bahis önerisi değildir.</div></html>"""
open(sys.argv[1],"w",encoding="utf-8").write(doc);print(oz.replace("<b>","").replace("</b>",""))
