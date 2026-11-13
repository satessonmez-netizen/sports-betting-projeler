"""Transfermarkt veri setinden (dcaribou/transfermarkt-datasets) takım kadro değeri özelliği.

Veri /tmp/tmdata/ex altında açılmış zip'ten okunur (indirme: bkz. README).
Not: veri seti 2026-06-12'den sonrasını içermiyor.
"""
import difflib
import re
import unicodedata

import numpy as np
import pandas as pd

EX = "/tmp/tmdata/ex"
DOM = {"T1": "TR1", "E0": "GB1", "SP1": "ES1", "D1": "L1", "I1": "IT1",
       "F1": "FR1", "N1": "NL1", "P1": "PO1", "B1": "BE1"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(fc|sk|sv|cf|afc|ac|as|ssc|rc|us|cd|ud|sc|fk|kv|krc|rsc|vfl|vfb|tsg|fsv|1\.)\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# football-data adı -> Transfermarkt kulüp adı (otomatik kuralın bulamadığı / yanlış bulduğu takımlar)
OVERRIDES = {
    "Man City": "Manchester City", "Wolves": "Wolverhampton Wanderers", "Coventry": "Coventry City",
    "Ath Madrid": "Atlético de Madrid", "La Coruna": "Deportivo de La Coruña", "Espanol": "RCD Espanyol Barcelona",
    "Santander": "Racing Santander", "M'gladbach": "Borussia Mönchengladbach", "Elversberg": "SV Elversberg",
    "Paris SG": "Paris Saint-Germain", "Le Mans": "Le Mans FC", "Rennes": "Stade Rennais", "Brest": "Stade Brestois 29",
    "For Sittard": "Fortuna Sittardia Combinatie", "Sp Lisbon": "Sporting CP", "Academico Viseu": "Académico de Viseu FC",
    "Lommel SK": "Lommel SK", "Bodrumspor": "Bodrum FK", "Amedspor": "Amed SK", "Corum": "Çorum FK",
    "Man United": "Manchester United", "Nott'm Forest": "Nottingham Forest", "Barcelona": "FC Barcelona",
    "Ath Bilbao": "Athletic Bilbao", "Ein Frankfurt": "Eintracht Frankfurt", "Milan": "AC Milan",
    "Verona": "Hellas Verona", "St Etienne": "AS Saint-Étienne", "Den Haag": "ADO Den Haag",
    "Sp Braga": "SC Braga", "St Truiden": "Sint-Truidense VV", "St. Gilloise": "Union Saint-Gilloise",
    "Ad. Demirspor": "Adana Demirspor", "Buyuksehyr": "Basaksehir FK", "Gaziantep": "Gaziantep FK",
    "Paris FC": "Paris FC",
}


def club_map(fd_names, tm_clubs: pd.DataFrame) -> dict:
    """football-data adı -> TM club_id. Önce elle tablo, sonra tek-aday kuralı. Bulunamazsa eksik bırakır
    (bulanık tahmin YOK: yanlış eşleşme veriyi bozar)."""
    tm = {norm(n): cid for n, cid in zip(tm_clubs.name, tm_clubs.club_id)}
    out = {}
    for n in fd_names:
        if n in OVERRIDES:
            k = norm(OVERRIDES[n])
            if k in tm:
                out[n] = tm[k]
            continue
        k = norm(n)
        cand = [t for t in tm if t == k or t.startswith(k) or k in t.split()]
        if len(cand) == 1:
            out[n] = tm[cand[0]]
    return out


def load_tm():
    clubs = pd.read_csv(f"{EX}/clubs.csv.gz")
    val = pd.read_csv(f"{EX}/player_valuations.csv.gz", parse_dates=["date"])
    return clubs, val
