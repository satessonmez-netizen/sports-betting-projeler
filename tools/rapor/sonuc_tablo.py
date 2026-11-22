"""Defterdeki bekleyen maçları ESPN skorlarıyla karşılaştırır (resmi CSV gelene kadar hızlı bakış).
Kullanım (repo kökünden):  python3 tools/rapor/sonuc_tablo.py 2026-11-21 2026-11-22
Önce:  sports-skills football get_daily_schedule --date=YYYY-MM-DD > /tmp/e_YYYY-MM-DD.json
"""
import json, re, sys, unicodedata
import pandas as pd
def norm(s):
    s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]","",s)
AL={"rizespor":["caykurrizespor"],"corum":["corumfk"],"manunited":["manchesterunited"],"athmadrid":["atleticomadrid"],"buyuksehyr":["istanbulbasaksehir"],
"amedspor":["amedsfk","amedsportif"],"ekoln":[],"fckoln":["fccologne"],"einfrankfurt":["eintrachtfrankfurt"],"mgladbach":["borussiamonchengladbach","mgladbach"],
"nottmforest":["nottinghamforest"],"lacoruna":["deportivolacoruna","deportivoacoruna"],"parissg":["parissaintgermain"],"milan":["acmilan"],"inter":["internazionale"],
"bournemouth":["afcbournemouth"],"brighton":["brightonhovealbion"],"newcastle":["newcastleunited"],"vallecano":["rayovallecano"],"betis":["realbetis"],"sociedad":["realsociedad"],
"celta":["celtavigo"],"ipswich":["ipswichtown"],"tottenham":["tottenhamhotspur"],"leverkusen":["bayerleverkusen"],"rbleipzig":["rbleipzig"],"goztep":["goztepe"],
"genclerbirligi":["genclerbirligi"],"kasimpasa":["kasimpasa"],"strasbourg":["strasbourg","rcstrasbourg"],"nice":["nice","ogcnice"],"marseille":["marseille","olympiquedemarseille"],
"lecce":["lecce","uslecce"],"monza":["monza","acmonza"],"venezia":["venezia"],"frosinone":["frosinone"],"malaga":["malaga","malagacf"],"leeds":["leedsunited"],"coventry":["coventrycity"],
"hoffenheim":["tsghoffenheim"],"freiburg":["scfreiburg"],"unionberlin":["1fcunionberlin"],"paderborn":["scpaderborn07","paderborn"],"elversberg":["svelversberg","elversberg"],
"parisfc":["parisfc"],"lemans":["lemans"],"alanyaspor":["alanyaspor"],"samsunspor":["samsunspor"],"kocaelispor":["kocaelispor"]}
def match(name,espn):
    n=norm(name);e=norm(espn)
    return e==n or e in AL.get(n,[]) or (len(n)>=5 and (e.startswith(n[:6]) or n.startswith(e[:6])))
led=pd.read_csv("predictions/ledger.csv",dtype=str)
days=sys.argv[1:]
ev=[]
for d in days:
    try: ev+=json.load(open(f"/tmp/e_{d}.json"))["data"]["events"]
    except Exception as x: print("okunamadı",d,x)
def res(h,a): return "1" if h>a else "X" if h==a else "2"
rows=[];done=0;yon=0;dc=0;ydone=0
for r in led[led.date.isin(days)].itertuples():
    f=None
    for e in ev:
        c=e["competitors"]
        if match(r.home,c[0]["team"]["name"]) and match(r.away,c[1]["team"]["name"]): f=e;break
    if f is None: rows.append((r.date,r.home,r.away,r.pick,r.conf,r.score,"?","bulunamadı"));continue
    st=f["status"];c=f["competitors"];hg,ag=int(c[0]["score"]),int(c[1]["score"])
    if st=="closed":
        o=res(hg,ag);ok=o==r.pick;ds=(ok if r.conf=="Yüksek" else o in ("1X" if r.pick=="1" else "X2"))
        done+=1;yon+=ok;dc+=ds
        rows.append((r.date,r.home,r.away,r.pick,r.conf,r.score,f"{hg}-{ag}","✅" if ok else "❌",("✅" if ds else "❌")))
    elif st=="not_started": rows.append((r.date,r.home,r.away,r.pick,r.conf,r.score,"-","oynanmadı"))
    else: rows.append((r.date,r.home,r.away,r.pick,r.conf,r.score,f"{hg}-{ag} (canlı)","devam"))
for x in rows: print(" | ".join(str(i) for i in x))
print(f"\nBiten {done}: yön {yon}/{done}, çifte şans(Yüksek tek) {dc}/{done}")
