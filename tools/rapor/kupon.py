import csv
O={ # home: (o1,ox,o2)
"Rizespor":(1.72,3.19,3.44),"Corum":(3.82,3.56,1.55),"Alanyaspor":(4.49,3.63,1.45),"Besiktas":(1.07,6.52,10.65),
"Brighton":(1.65,3.45,3.45),"Crystal Palace":(4.62,3.89,1.41),"Sunderland":(3.31,3.21,1.74),"Ipswich":(3.41,3.31,1.69),"Man United":(1.92,3.27,2.78),
"Elche":(3.04,3.26,1.81),"Sociedad":(1.56,3.56,3.75),"Villarreal":(1.27,4.15,6.30),"Celta":(1.67,3.18,3.66),"Ath Madrid":(3.27,3.84,1.61),
"Napoli":(2.06,3.17,2.59),"Monza":(2.91,3.31,1.85),"Genoa":(3.98,3.11,1.62),"Inter":(1.70,3.63,3.09),"Fiorentina":(2.96,3.07,1.91),
"FC Koln":(3.25,3.62,1.66),"Freiburg":(1.33,4.11,5.27),"Hoffenheim":(1.42,3.90,4.39),
"Rennes":(1.95,3.15,2.80),"Le Mans":(3.99,3.63,1.51),"Le Havre":(2.66,2.92,2.13),"Brest":(2.46,3.03,2.22),"Angers":(3.11,3.20,1.81),"Lens":(2.05,3.38,2.47),
"Heerenveen":(3.80,3.79,1.52),"Twente":(2.01,3.44,2.51),"Cambuur":(5.52,5.03,1.24),"AZ Alkmaar":(1.34,4.28,4.75),"Utrecht":(2.19,3.36,2.32),
"Club Brugge":(1.33,4.31,4.99),"Gent":(1.29,4.06,5.90),"St. Gilloise":(1.43,3.80,4.44),"St Truiden":(1.58,3.51,3.70),
"Nacional":(2.60,2.89,2.19),"Santa Clara":(2.00,2.74,3.09),"Guimaraes":(4.82,3.65,1.41),"Rio Ave":(5.22,3.82,1.36),"Estrela":(9.93,6.05,1.08)}
rows={r["home"]:r for r in csv.DictReader(open("predictions/picks_2026-11-08_noTM.csv",encoding="utf-8"))}
DCF=0.95
out=[]
for h,(a,x,b) in O.items():
    r=rows[h]; me=[float(r["pH"]),float(r["pD"]),float(r["pA"])]
    inv=[1/a,1/x,1/b]; s=sum(inv); mk=[i/s for i in inv]
    bl=[(m+k)/2 for m,k in zip(me,mk)]
    opts={"1":(bl[0],a),"2":(bl[2],b),"1X":(bl[0]+bl[1],DCF/(1/a+1/x)),"X2":(bl[1]+bl[2],DCF/(1/x+1/b))}
    ev={k:p*o-1 for k,(p,o) in opts.items()}
    best=max(ev,key=ev.get)
    evme={k:( (me[0] if k=="1" else me[2] if k=="2" else me[0]+me[1] if k=="1X" else me[1]+me[2])*opts[k][1]-1) for k in opts}
    out.append((h,r["away"],r["pick"],r["conf"],me,mk,best,opts[best][1],ev[best],evme[best],ev,evme))
    print(f"{h}-{r['away']} | mine {r['pick']} {r['conf']} {[round(v*100) for v in me]} | mkt {[round(v*100) for v in mk]} | best {best} @{opts[best][1]:.2f} EVblend {ev[best]:+.2f} EVme {evme[best]:+.2f} | all {{{', '.join(f'{k}:{v:+.2f}' for k,v in ev.items())}}}")
