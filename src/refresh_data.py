"""CSV'leri indirir ve yaklaşan maç oranlarını data/fixtures_snapshot.csv'ye kaydeder.
Bu betiği football-data.co.uk'a erişebilen bir ortamda çalıştır, çıktıları repoya commit'le.
"""
from config import ROOT
from data import download
from predict import upcoming

if __name__ == "__main__":
    download()
    fx = upcoming()
    fx.to_csv(ROOT / "data" / "fixtures_snapshot.csv", index=False)
    print("fixtures_snapshot.csv:", len(fx), "maç")
