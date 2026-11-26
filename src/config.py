"""Proje ayarları: ligler, sezonlar, yollar."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PRED = ROOT / "predictions"
REPORTS = ROOT / "reports"

BASE_URL = "https://football-data.co.uk/mmz4281/{season}/{div}.csv"

LEAGUES = {
    "T1": "Süper Lig",
    "E0": "Premier Lig",
    "SP1": "La Liga",
    "D1": "Bundesliga",
    "I1": "Serie A",
    "F1": "Ligue 1",
    "N1": "Eredivisie",
    "P1": "Primeira Liga",
    "B1": "Pro League (Belçika)",
}

# football-data.co.uk sezon kodu: 2526 = 2025/26
SEASONS = ["1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526", "2627"]
