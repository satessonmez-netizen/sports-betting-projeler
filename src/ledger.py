"""Tahmin defteri: tahmini maçtan ÖNCE kilitler, sonra sonuçlarla karşılaştırır.

Komutlar:
  python ledger.py add   --picks ../predictions/picks_2026-11-06.csv --pack ../output/match_pack_2026-11-06.json
  python ledger.py add   ... --revise      # başlamamış maçın tahminini güncelle (ilk tahmin ayrıca saklanır)
  python ledger.py settle                  # biten maçların sonucunu ve kapanış oranlarını işle
  python ledger.py report                  # sayılarla rapor (reports/weekly_<tarih>.md)
  python ledger.py errors                  # yanıldığım maçlar ve nedenleri
  python ledger.py dc                      # bekleyen maçlar için çifte şans tablosu

Kurallar (dürüstlük için):
- Maç başladıktan sonra kaydedilen tahmin 'late=1' olur ve hiçbir istatistiğe girmez.
- Sonuçlanmış satırın tahmini değiştirilemez.
- 100 maçtan az örnekte rapor 'yorum yapma' uyarısı verir.
- KURALLAR (kullanıcı kararı): Yüksek güvenli tahminde çifte şans verilmez (tek tahmin). Orta/Düşük güvende çifte şans = tahmin + beraberlik (1X/X2). 'PAS' yok: her maç için en güçlü tahmin yazılır.
"""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from config import PRED, REPORTS, ROOT
from data import load
from metrics import brier, implied, logloss, outcome, rps

LEDGER = Path(os.environ.get("LEDGER_PATH", PRED / "ledger.csv"))
SNAP = ROOT / "data" / "fixtures_snapshot.csv"
COLS = ["id", "made_at", "date", "time_uk", "div", "home", "away", "late", "revision",
        "pick", "pH", "pD", "pA", "score", "conf", "note",
        "first_pH", "first_pD", "first_pA", "first_pick",
        "model_pH", "model_pD", "model_pA", "xgH", "xgA",
        "open_oH", "open_oD", "open_oA", "bo_H", "bo_D", "bo_A",
        "inj_pH", "inj_pD", "inj_pA", "hg", "ag", "bc_H", "bc_D", "bc_A", "cl_oH", "cl_oD", "cl_oA", "settled_at"]
SEG_MIN = 100


def read() -> pd.DataFrame:
    text = ["id", "made_at", "date", "time_uk", "div", "home", "away", "pick", "score", "conf", "note",
            "first_pick", "settled_at"]
    if LEDGER.exists():
        return pd.read_csv(LEDGER, dtype={c: "object" for c in text})
    return pd.DataFrame(columns=COLS).astype({c: "object" for c in text})


def write(df: pd.DataFrame):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    df.reindex(columns=COLS).to_csv(LEDGER, index=False)


def now_uk():
    return datetime.now(ZoneInfo("Europe/London")).replace(tzinfo=None)


def cmd_add(a):
    picks = pd.read_csv(a.picks)
    pack = {e["maç"]: e for e in json.load(open(a.pack))}
    fx = pd.read_csv(SNAP)
    res = load()
    res = res[res.hg.notna()]
    led = read()
    now = now_uk()
    added = revised = late = 0
    for r in picks.itertuples():
        key = f"{r.home} - {r.away}"
        if key not in pack:
            print(f"  [atlandı] pakette yok: {key}")
            continue
        e = pack[key]
        f = fx[(fx.home == r.home) & (fx.away == r.away)]
        if f.empty:
            print(f"  [atlandı] fikstürde yok (oynanmış olabilir): {key}")
            continue
        f = f.iloc[0]
        mid = f"{f['date']}|{e['lig']}|{r.home}|{r.away}"
        kick = pd.Timestamp(f"{f['date']} {f['time'] if pd.notna(f.get('time')) else '00:00'}")
        is_late = int(kick <= now or not res[(res["div"] == e["lig"]) & (res.home == r.home)
                                              & (res.away == r.away) & (res.date >= pd.Timestamp(f["date"]))].empty)
        m = e["model"]
        row = {"id": mid, "made_at": now.strftime("%Y-%m-%d %H:%M"), "date": f["date"], "time_uk": f["time"],
               "div": e["lig"], "home": r.home, "away": r.away, "late": is_late, "revision": 0,
               "pick": r.pick, "pH": r.pH, "pD": r.pD, "pA": r.pA, "score": r.score, "conf": r.conf,
               "note": getattr(r, "note", ""), "first_pH": r.pH, "first_pD": r.pD, "first_pA": r.pA,
               "first_pick": r.pick, "model_pH": m["1"], "model_pD": m["X"], "model_pA": m["2"],
               "xgH": m["beklenen_gol"][0], "xgA": m["beklenen_gol"][1],
               "open_oH": f["oH"], "open_oD": f["oD"], "open_oA": f["oA"],
               "bo_H": f["boH"], "bo_D": f["boD"], "bo_A": f["boA"]}
        ij = e.get("model_sakatlık_ayarlı")
        if ij:
            row.update({"inj_pH": ij["1"], "inj_pD": ij["X"], "inj_pA": ij["2"]})
        idx = led.index[led["id"] == mid]
        if len(idx):
            i = idx[0]
            if not a.revise:
                print(f"  [var] {key} zaten kayıtlı (güncellemek için --revise)")
                continue
            if pd.notna(led.at[i, "hg"]) or kick <= now:
                print(f"  [reddedildi] {key}: maç başlamış/bitmiş, tahmin değiştirilemez")
                continue
            for k in ("pick", "pH", "pD", "pA", "score", "conf", "note", "inj_pH", "inj_pD", "inj_pA"):
                if k not in row:
                    continue
                led.at[i, k] = row[k]
            led.at[i, "revision"] = int(led.at[i, "revision"]) + 1
            revised += 1
        else:
            led = pd.concat([led, pd.DataFrame([row])], ignore_index=True)
            added += 1
            late += is_late
            if is_late:
                print(f"  [GEÇ] {key}: maç başlamış, istatistiğe girmeyecek")
    write(led)
    print(f"{added} eklendi, {revised} güncellendi, {late} geç. Toplam {len(led)} satır.")


DRAW_RISK = 0.27  # sadece bilgi amaçlı işaret: beraberlik ihtimali bu değerin üstündeyse 'beraberlik riski yüksek'


def dc_label(pH, pD, pA, pick=None):
    """Çifte şans = benim tahminim + beraberlik (1X veya X2). Tahminle tutarlı: favoriyi korur, beraberliği kapsar.
    (Eski 'en çok kapsama' kuralı bazen '12' veriyordu: tahmin yönünü bozuyordu, kaldırıldı.)
    Döner: (etiket, kapsanan olasılık)."""
    if str(pick) == "1":
        return "1X", pH + pD
    if str(pick) == "2":
        return "X2", pD + pA
    p = {"1": pH, "X": pD, "2": pA}
    out = min(p, key=p.get)
    return {"2": "1X", "1": "X2", "X": "12"}[out], 1 - p[out]


def cmd_dc(a):
    led = read()
    u = led[led.hg.isna() & (led.late == 0)].sort_values(["date", "time_uk"])
    if u.empty:
        print("Bekleyen geçerli maç yok.")
        return
    tot, n = 0, 0
    for r in u.itertuples():
        if r.conf == "Yüksek":  # KURAL: güçlü tahmin tek yazılır, çifte şans verilmez
            print(f"{r.date} {r.time_uk} | {r.home} - {r.away} | tek: {r.pick} (%{max(r.pH, r.pA)*100:.0f}) | çifte şans: YOK (güçlü tahmin, tek yazılır)")
            continue
        lab, p = dc_label(r.pH, r.pD, r.pA, r.pick)
        tot += p
        n += 1
        risk = "  [beraberlik riski yüksek]" if r.pD >= DRAW_RISK else ""
        print(f"{r.date} {r.time_uk} | {r.home} - {r.away} | tek: {r.pick} | çifte şans: {lab} (%{p*100:.0f}, adil oran ~{1/p:.2f}){risk}")
    print(f"Çifte şans verilen {n} maç için beklenen isabet: %{100*tot/max(n, 1):.0f}")


def cmd_settle(a):
    led = read()
    res = load()
    res = res[res.hg.notna()]
    n = 0
    for i, r in led[led.hg.isna()].iterrows():
        d0 = pd.Timestamp(r["date"])
        m = res[(res["div"] == r["div"]) & (res.home == r["home"]) & (res.away == r["away"])
                & (res.date >= d0 - pd.Timedelta(days=1)) & (res.date <= d0 + pd.Timedelta(days=2))]
        if m.empty:
            continue
        m = m.iloc[0]
        led.at[i, "hg"], led.at[i, "ag"] = m.hg, m.ag
        for k in "HDA":
            led.at[i, f"bc_{k}"] = m[f"bc{k}"]
            led.at[i, f"cl_o{k}"] = m[f"o{k}"]   # en iyi kapanış (Pinnacle > Bet365 > ort.)
        led.at[i, "settled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        n += 1
    write(led)
    print(f"{n} maç sonuçlandırıldı. Bekleyen: {int(led.hg.isna().sum())}")


def _probs(df, pre):
    return df[[f"{pre}H", f"{pre}D", f"{pre}A"]].to_numpy(float)


def _eval(df):
    """df: sonuçlanmış, geç olmayan satırlar."""
    y = outcome(df.hg.to_numpy(), df.ag.to_numpy())
    mine = _probs(df.assign(**{"pH": df.pH, "pD": df.pD, "pA": df.pA}), "p")
    mdl = _probs(df, "model_p")
    ok = df[["cl_oH", "cl_oD", "cl_oA"]].notna().all(axis=1).to_numpy()
    mk = implied(df.cl_oH.to_numpy(float), df.cl_oD.to_numpy(float), df.cl_oA.to_numpy(float)) if ok.any() else None
    out = {"n": len(df), "isabet_benim": float((mine.argmax(1) == y).mean()),
           "rps_benim": rps(mine, y), "brier_benim": brier(mine, y), "ll_benim": logloss(mine, y),
           "rps_model": rps(mdl, y), "isabet_model": float((mdl.argmax(1) == y).mean())}
    if mk is not None and ok.all():
        out.update({"rps_piyasa": rps(mk, y), "brier_piyasa": brier(mk, y), "ll_piyasa": logloss(mk, y),
                    "isabet_piyasa": float((mk.argmax(1) == y).mean())})
    return out, y, mine, mk


def _fmt(o):
    t = f"n={o['n']} | isabet: ben %{o['isabet_benim']*100:.0f}"
    if "isabet_piyasa" in o:
        t += f", piyasa %{o['isabet_piyasa']*100:.0f}"
    t += f", model %{o['isabet_model']*100:.0f} | RPS: ben {o['rps_benim']:.4f}"
    if "rps_piyasa" in o:
        t += f", piyasa {o['rps_piyasa']:.4f}"
    t += f", model {o['rps_model']:.4f}"
    return t


def cmd_report(a):
    led = read()
    s = led[led.hg.notna() & (led.late == 0)].copy()
    lines = [f"# Tahmin defteri raporu {datetime.now().date()}", ""]
    lines.append(f"Toplam kayıt: {len(led)} | sonuçlanan (geçerli): {len(s)} | bekleyen: {int(led.hg.isna().sum())} | "
                 f"geç kaydedilen: {int((led.late == 1).sum())}")
    if s.empty:
        lines.append("\nHenüz sonuçlanmış geçerli maç yok.")
    else:
        o, y, mine, mk = _eval(s)
        lines += ["", "## Genel", _fmt(o)]
        hit, exp = [], []
        for r in s[s.conf != "Yüksek"].itertuples():  # güçlü tahminlerde çifte şans yok
            lab, p = dc_label(r.pH, r.pD, r.pA, r.pick)
            res = "1" if r.hg > r.ag else "X" if r.hg == r.ag else "2"
            hit.append(res in lab)
            exp.append(p)
        lines.append(f"Çifte şans: isabet %{100*np.mean(hit):.0f}, beklenen %{100*np.mean(exp):.0f} (n={len(hit)})")
        if o["n"] < SEG_MIN:
            lines.append(f"\n⚠ n={o['n']} < {SEG_MIN}: bu sayılardan 'iyi/kötü gidiyoruz' sonucu ÇIKARMA. Gürültü büyük.")
        # açılıştan kapanışa piyasa hareketi (aynı şirket: Bet365)
        mv = s[s[["bo_H", "bo_D", "bo_A", "bc_H", "bc_D", "bc_A"]].notna().all(axis=1)]
        if len(mv):
            op = implied(mv.bo_H.to_numpy(float), mv.bo_D.to_numpy(float), mv.bo_A.to_numpy(float))
            cl = implied(mv.bc_H.to_numpy(float), mv.bc_D.to_numpy(float), mv.bc_A.to_numpy(float))
            k = _probs(mv, "p").argmax(1)
            d = cl[np.arange(len(mv)), k] - op[np.arange(len(mv)), k]
            lines += ["", "## Piyasa hareketi (CLV benzeri)",
                      f"Seçtiğim sonuç için kapanış olasılığı açılıştan ort. {d.mean()*100:+.1f} puan farklı; "
                      f"maçların %{(d > 0).mean()*100:.0f}'inde piyasa benim seçtiğim yöne kaydı (n={len(mv)}).",
                      "Pozitif ve süreklilik gösteriyorsa tahminim piyasadan önce doğru bilgiyi yakalıyor demektir."]
        # segmentler
        s["conf_"] = s.conf
        s["lig"] = s["div"]
        cl_p = implied(s.cl_oH.to_numpy(float), s.cl_oD.to_numpy(float), s.cl_oA.to_numpy(float))
        s["dep_fav"] = np.where(cl_p[:, 2] > cl_p[:, 0], "deplasman favori", "ev/dengeli")
        s["ayrisma"] = np.where(np.abs(_probs(s, "p") - cl_p).max(1) >= 0.08, "piyasadan >=8 puan farklı", "piyasaya yakın")
        for col, title in (("conf_", "Güven düzeyine göre"), ("lig", "Lige göre"),
                           ("dep_fav", "Favori tarafa göre"), ("ayrisma", "Piyasadan ayrışmaya göre")):
            lines += ["", f"## {title}"]
            for key, g in s.groupby(col):
                oo, *_ = _eval(g)
                lines.append(f"- {key}: {_fmt(oo)}")
    txt = "\n".join(lines)
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / f"weekly_{datetime.now().date()}.md").write_text(txt, encoding="utf-8")
    print(txt)


def cmd_errors(a):
    led = read()
    s = led[led.hg.notna() & (led.late == 0)].copy()
    if s.empty:
        print("Henüz sonuçlanmış geçerli maç yok.")
        return
    y = outcome(s.hg.to_numpy(), s.ag.to_numpy())
    P = _probs(s, "p")
    cl = implied(s.cl_oH.to_numpy(float), s.cl_oD.to_numpy(float), s.cl_oA.to_numpy(float))
    names = ["1", "X", "2"]
    for i, (idx, r) in enumerate(s.iterrows()):
        pk = P[i].argmax()
        if pk == y[i]:
            continue
        tags = []
        if cl[i, 2] > cl[i, 0]:
            tags.append("deplasman favorisi")
        if abs(P[i] - cl[i]).max() >= 0.08:
            tags.append("piyasadan ayrışmıştım")
        if r["conf"] == "Düşük":
            tags.append("düşük güvenli tahmin")
        print(f"{r['date']} {r['home']} {int(r.hg)}-{int(r.ag)} {r['away']} | tahmin {names[pk]} (%{P[i, pk]*100:.0f}) "
              f"gerçek {names[y[i]]} | benim p={P[i, y[i]]*100:.0f}% piyasa p={cl[i, y[i]]*100:.0f}% | {', '.join(tags) or '-'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add"); p.add_argument("--picks", required=True); p.add_argument("--pack", required=True)
    p.add_argument("--revise", action="store_true"); p.set_defaults(f=cmd_add)
    sub.add_parser("settle").set_defaults(f=cmd_settle)
    sub.add_parser("report").set_defaults(f=cmd_report)
    sub.add_parser("errors").set_defaults(f=cmd_errors)
    sub.add_parser("dc").set_defaults(f=cmd_dc)
    a = ap.parse_args()
    a.f(a)
