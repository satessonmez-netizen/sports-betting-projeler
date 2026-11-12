import csv
rows={r["home"]:r for r in csv.DictReader(open("predictions/picks_2026-11-08_noTM.csv",encoding="utf-8"))}
# home:(o1,ox,o2, c1x,c12,cx2)
O={"Rizespor":(1.72,3.19,3.44,1.12,1.15,1.63),"Corum":(3.82,3.56,1.55,1.80,1.11,1.08),"Alanyaspor":(4.49,3.63,1.45,1.96,1.10,None),"Besiktas":(1.07,6.52,10.65,None,None,3.76),
"Brighton":(1.65,3.45,3.45,1.13,1.13,1.68),"Crystal Palace":(4.62,3.89,1.41,2.08,1.08,None),"Sunderland":(3.31,3.21,1.74,1.63,1.15,1.12),"Ipswich":(3.41,3.31,1.69,1.67,1.14,1.12),"Man United":(1.92,3.27,2.78,1.21,1.15,1.48),
"Elche":(3.04,3.26,1.81,1.56,1.15,1.16),"Sociedad":(1.56,3.56,3.75,1.09,1.11,1.79),"Villarreal":(1.27,4.15,6.30,None,1.06,2.40),"Celta":(1.67,3.18,3.66,1.10,1.15,1.67),"Ath Madrid":(3.27,3.84,1.61,1.74,1.08,1.14),
"Napoli":(2.06,3.17,2.59,1.25,1.15,1.41),"Monza":(2.91,3.31,1.85,1.54,1.14,1.19),"Genoa":(3.98,3.11,1.62,1.72,1.16,1.08),"Inter":(1.70,3.63,3.09,1.16,1.11,1.63),"Fiorentina":(2.96,3.07,1.91,1.49,1.17,1.18),
"FC Koln":(3.25,3.62,1.66,1.68,1.11,1.14),"Freiburg":(1.33,4.11,5.27,None,1.07,2.24),"Hoffenheim":(1.42,3.90,4.39,None,1.08,2.01),
"Rennes":(1.95,3.15,2.80,1.21,1.15,1.47),"Le Mans":(3.99,3.63,1.51,1.87,1.10,1.08),"Le Havre":(2.66,2.92,2.13,1.39,1.19,1.23),"Brest":(2.46,3.03,2.22,1.35,1.17,1.28),"Angers":(3.11,3.20,1.81,1.56,1.15,1.16),"Lens":(2.05,3.38,2.47,1.28,1.13,1.42)}
for h,(a,x,b,c1x,c12,cx2) in O.items():
    r=rows[h];me=[float(r["pH"]),float(r["pD"]),float(r["pA"])]
    inv=[1/a,1/x,1/b];s=sum(inv);mk=[i/s for i in inv];bl=[(m+k)/2 for m,k in zip(me,mk)]
    pk=r["pick"]
    if pk=="1": pt,ot,pd_,od=bl[0],a,bl[0]+bl[1],c1x
    else: pt,ot,pd_,od=bl[2],b,bl[1]+bl[2],cx2
    et=pt*ot-1; ed=(pd_*od-1) if od else None
    p12=bl[0]+bl[2]; e12=p12*c12-1 if c12 else None
    print(f"{h}|{r['away']}|{pk}|{r['conf']}|tek {ot:.2f} EV{et:+.2f}|dc {od} EV{'%+.2f'%ed if ed is not None else '-'}|12 {c12} EV{'%+.2f'%e12 if e12 is not None else '-'}| me {[round(v*100) for v in me]} mk {[round(v*100) for v in mk]}")
