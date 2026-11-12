import json,csv,html,sys
import pandas as pd
src=open("tools/rapor/mkpdf2.py").read().split('body="";cur=None')[0]
exec(src)  # rows (8 Kasım noTM picks), C (liga,tercih,oran,kupon), n(), nice
alias={"Caykur Rizespor":"Rizespor","Çorum FK":"Corum","Brighton & Hove Albion":"Brighton","Ipswich Town":"Ipswich","AFC Bournemouth":"Bournemouth","Manchester United":"Man United","Real Betis":"Betis","Real Sociedad":"Sociedad","Rayo Vallecano":"Vallecano","Celta Vigo":"Celta","Atlético Madrid":"Ath Madrid","AC Milan":"Milan","Internazionale":"Inter","FC Cologne":"FC Koln","Bayer Leverkusen":"Leverkusen","SC Freiburg":"Freiburg","1. FC Union Berlin":"Union Berlin","TSG Hoffenheim":"Hoffenheim","Stade Rennais":"Rennes","AS Monaco":"Monaco","Le Havre AC":"Le Havre","Erzurum BB":"Erzurumspor","Amed SFK":"Amedspor","Goztepe":"Goztep","Istanbul Basaksehir":"Buyuksehyr","VfB Stuttgart":"Stuttgart"}
def load(day):
    R={}
    for e in json.load(open(f"/tmp/d_{day}.json"))["data"]["events"]:
        if e.get("competition",{}).get("id") not in ('super-lig','premier-league','la-liga','serie-a','bundesliga','ligue-1','bundesliga'): continue
        c=e["competitors"];h=alias.get(c[0]["team"]["name"],c[0]["team"]["name"])
        R[h]=(e["status"],int(c[0]["score"]),int(c[1]["score"]))
    return R
R8=load("2026-11-08");R7=load("2026-11-07")
led=pd.read_csv("predictions/ledger.csv",dtype=str)
def res(hg,ag): return "1" if hg>ag else "X" if hg==ag else "2"
def dcl(p): return "1X" if p=="1" else "X2"
def clsof(c): return "hi" if c=="Yüksek" else ("mid" if c=="Orta" else "lo")
def line(mac,pick,conf,sk,st,hg,ag,extra=""):
    if st=="closed":
        o=res(hg,ag);y=(pick==o);cs=(o in dcl(pick)) if conf!="Yüksek" else y
        sc=f"<b>{hg}-{ag}</b>";yon="✅" if y else "❌";csr="✅" if cs else "❌";ret=(y,cs)
    elif st=="not_started": sc="–";yon="oynanmadı";csr="–";ret=None
    else: sc=f"{hg}-{ag} (canlı)";yon="devam";csr="–";ret=None
    cdisp="tek" if conf=="Yüksek" else dcl(pick)
    return f"<tr><td>{mac}</td><td class='c k'>{pick}</td><td class='c {clsof(conf)}'>{conf}</td><td class=c>{sk}</td><td class=c>{sc}</td><td class=c>{yon}</td><td class=c>{cdisp}</td><td class=c>{csr}</td><td class=c>{extra}</td></tr>",ret
HEAD="<tr><th>Maç</th><th>Tahmin</th><th>Güven</th><th>Skor tah.</th><th>Gerçek</th><th>Yön</th><th>Çifte şans*</th><th>ÇŞ sonucu</th><th>Not</th></tr>"
tot={"7":[0,0,0],"8":[0,0,0]}
body="<h2>7 Kasım (Cumartesi)</h2><table>"+HEAD
L7=led[led.date=="2026-11-07"]
for r in L7.itertuples():
    if r.home not in R7: continue
    st,hg,ag=R7[r.home]
    row,ret=line(f"{html.escape(n(r.home) if r.home in nice else r.home)} – {html.escape(n(r.away) if r.away in nice else r.away)}",r.pick,r.conf,r.score,st,hg,ag)
    body+=row
    if ret: tot["7"][0]+=1;tot["7"][1]+=ret[0];tot["7"][2]+=ret[1]
body+="</table><h2>8 Kasım (Pazar)</h2><table>"+HEAD
for h,(lg,t,o,k) in C.items():
    r=rows[h];st,hg,ag=R8[h]
    ex=""
    if h in ("Napoli","Monza","Inter","Rennes","Brighton"): ex="⭐ kupon"
    row,ret=line(f"{html.escape(n(h))} – {html.escape(n(r['away']))}",r["pick"],r["conf"],r["score"],st,hg,ag,ex)
    body+=row
    if ret: tot["8"][0]+=1;tot["8"][1]+=ret[0];tot["8"][2]+=ret[1]
body+="</table>"
n7,y7,c7=tot["7"];n8,y8,c8=tot["8"]
N=n7+n8;Y=y7+y8;Cc=c7+c8
oz=f"7 Kasım: {n7} maç, yön {y7}/{n7}, çifte şans {c7}/{n7} · 8 Kasım (biten): {n8}/28, yön {y8}/{n8}, çifte şans {c8}/{n8} · <b>Toplam: {N} maç, yön {Y}/{N} (%{100*Y//max(N,1)}), çifte şans {Cc}/{N} (%{100*Cc//max(N,1)})</b>"
doc=f"""<!doctype html><html lang=tr><meta charset=utf-8><title>İki günlük karşılaştırma</title><style>
body{{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;font-size:10px;margin:0}} h1{{font-size:16px;margin:0 0 4px}} h2{{font-size:12.5px;margin:12px 0 4px;color:#1f4e79}}
.sub{{color:#555;margin-bottom:6px}} table{{width:100%;border-collapse:collapse}} tr{{break-inside:avoid}}
th{{background:#1f4e79;color:#fff;text-align:left;padding:4px 5px;font-size:9px}} td{{padding:3.5px 5px;border-bottom:1px solid #ddd}}
.c{{text-align:center;white-space:nowrap}} .k{{font-weight:bold;background:#eef4fa}} .hi{{color:#0b7a2b;font-weight:bold}} .mid{{color:#9a6a00}} .lo{{color:#b00020}}
.box{{margin:8px 0;padding:8px 10px;border:1px solid #1f4e79;background:#f5f9fd;line-height:1.5}} .note{{margin-top:10px;font-size:9.5px;color:#444;border-top:1px solid #ccc;padding-top:6px}}
</style><h1>7-8 Kasım 2026 · Tahminler ve gerçekleşen sonuçlar</h1>
<div class=sub>Skorlar ESPN (sports-skills). Tahmin: benim tek tahminim (son hali). *Çifte şans: Orta/Düşük güvende tahmin + beraberlik, Yüksek güvende tek.</div>
<div class=box>{oz}</div>
{body}
<div class=note><b>Dürüst not:</b> Örnek sayısı küçük (100 maçtan çok az). Çifte şans iki sonucu birden kapsadığı için daha çok tutar, oranları ise düşüktür. 8 Kasım'da oynanmamış/devam eden maçlar sayıma girmedi. Resmi doğrulama Salı sabahı football-data CSV'siyle yapılır.</div></html>"""
open(sys.argv[1],"w",encoding="utf-8").write(doc);print(oz.replace("<b>","").replace("</b>",""))
