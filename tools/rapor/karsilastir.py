import json,csv,html,sys
src=open("tools/rapor/mkpdf2.py").read().split('body="";cur=None')[0]
exec(src)
alias={"Caykur Rizespor":"Rizespor","Çorum FK":"Corum","Brighton & Hove Albion":"Brighton","Ipswich Town":"Ipswich","AFC Bournemouth":"Bournemouth","Manchester United":"Man United","Real Betis":"Betis","Real Sociedad":"Sociedad","Rayo Vallecano":"Vallecano","Celta Vigo":"Celta","Atlético Madrid":"Ath Madrid","AC Milan":"Milan","Internazionale":"Inter","FC Cologne":"FC Koln","Bayer Leverkusen":"Leverkusen","SC Freiburg":"Freiburg","1. FC Union Berlin":"Union Berlin","TSG Hoffenheim":"Hoffenheim","Stade Rennais":"Rennes","AS Monaco":"Monaco","Le Havre AC":"Le Havre","Erzurum BB":"Erzurumspor"}
ev=json.load(open("/tmp/d8.json"))["data"]["events"]
R={}
for e in ev:
    if e.get("competition",{}).get("id") not in ('super-lig','premier-league','la-liga','serie-a','bundesliga','ligue-1'): continue
    c=e["competitors"];h=c[0]["team"]["name"];h=alias.get(h,h)
    R[h]=(e["status"],int(c[0]["score"]),int(c[1]["score"]))
LEG={"Brighton":"1X","Napoli":"X2","Monza":"X2","Inter":"1X","Rennes":"X2"}
def res(o): return "1" if o[1]>o[2] else "X" if o[1]==o[2] else "2"
def ok(sel,r): return r in sel
body="";cur=None;cnt={"n":0,"yon":0,"tercih":0,"cs":0}
for h,(lg,t,o,k) in C.items():
    r=rows[h]
    if lg!=cur:
        if cur: body+="</table>"
        body+=f"<h2>{lg}</h2><table><tr><th>Maç</th><th>Tahmin</th><th>Güven</th><th>Skor tah.</th><th>Gerçek skor</th><th>Yön</th><th>Tercih</th><th>Oran</th><th>Tercih sonucu</th><th>Kupon</th></tr>";cur=lg
    st,hg,ag=R[h]
    cls="hi" if r["conf"]=="Yüksek" else ("mid" if r["conf"]=="Orta" else "lo")
    if st=="closed":
        o_=res((st,hg,ag));y=ok(r["pick"],o_);tc=ok(t,o_);cs=ok("1X" if r["pick"]=="1" else "X2",o_)
        cnt["n"]+=1;cnt["yon"]+=y;cnt["tercih"]+=tc;cnt["cs"]+=cs
        score=f"<b>{hg}-{ag}</b>";yon="✅" if y else "❌";tc_="✅" if tc else "❌"
    elif st=="not_started":
        score="–";yon="oynanmadı";tc_="–"
    else:
        score=f"{hg}-{ag} (canlı)";yon="devam";tc_="–"
    kup=""
    if h in LEG:
        if st=="closed": kup=f"⭐ {LEG[h]} "+("✅" if ok(LEG[h],res((st,hg,ag))) else "❌")
        else: kup=f"⭐ {LEG[h]}"
    body+=f"<tr><td>{html.escape(n(h))} – {html.escape(n(r['away']))}</td><td class='c k'>{r['pick']}</td><td class='c {cls}'>{r['conf']}</td><td class=c>{r['score']}</td><td class=c>{score}</td><td class=c>{yon}</td><td class='c k'>{t}</td><td class=c>{o:.2f}</td><td class=c>{tc_}</td><td class=c>{kup}</td></tr>"
body+="</table>"
n_=cnt["n"]
ozet=f"Biten maç: {n_}/28 · Yön tuttu: {cnt['yon']}/{n_} · Çifte şans (tahmin+beraberlik) tuttu: {cnt['cs']}/{n_} · Tercihim tuttu: {cnt['tercih']}/{n_}"
doc=f"""<!doctype html><html lang=tr><meta charset=utf-8><title>Tahmin ve sonuç</title><style>
body{{font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;font-size:10.5px;margin:0}} h1{{font-size:17px;margin:0 0 4px}} h2{{font-size:12.5px;margin:12px 0 4px;color:#1f4e79}}
.sub{{color:#555;margin-bottom:6px}} table{{width:100%;border-collapse:collapse;break-inside:avoid}}
th{{background:#1f4e79;color:#fff;text-align:left;padding:4px 5px;font-size:9.5px}} td{{padding:4px 5px;border-bottom:1px solid #ddd}}
.c{{text-align:center;white-space:nowrap}} .k{{font-weight:bold;background:#eef4fa}} .hi{{color:#0b7a2b;font-weight:bold}} .mid{{color:#9a6a00}} .lo{{color:#b00020}}
.box{{margin:8px 0;padding:8px 10px;border:1px solid #1f4e79;background:#f5f9fd;line-height:1.5}} .note{{margin-top:10px;font-size:10px;color:#444;border-top:1px solid #ccc;padding-top:6px}}
</style><h1>8 Kasım 2026 · Tahmin ve gerçekleşen sonuçlar</h1>
<div class=sub>Skorlar ESPN (sports-skills). Biten maçlar kesin, canlı olanlar değişebilir. Yön: benim tek tahminim. Tercih: oranlı listedeki tek/çifte şans seçimim.</div>
<div class=box><b>{ozet}</b></div>
{body}
<div class=note><b>Dürüst not:</b> Bu tablo anlık görüntüdür, biten maç sayısı küçük. Birkaç maçtan sonuç çıkarılmaz. Resmi doğrulama Salı sabahı football-data CSV'siyle yapılır.</div></html>"""
open(sys.argv[1],"w",encoding="utf-8").write(doc);print(ozet)
