# sports-betting-projeler

Amaç para kazanmak değil: **bir modelin futbol sonuçlarını ne kadar iyi tahmin ettiğini dürüstçe ölçmek.**
Gerçek bahis yok, sadece paper trading (tahmin günlüğü).

Kapsam: Süper Lig + Premier Lig, La Liga, Bundesliga, Serie A, Ligue 1, Eredivisie, Primeira Liga, Belçika Pro League.
Veri: [football-data.co.uk](https://football-data.co.uk) ücretsiz CSV'leri (2018/19 → bugün).

## Başarı ölçütü
İsabet yüzdesine bakmıyoruz. Ölçütler: **RPS**, **log-loss**, **Brier** (düşük = iyi).
Kıyas noktası: bahisçinin marjı çıkarılmış kapanış oranı. Bu referansı geçemiyorsak "uzman" değiliz.

## Kullanım
```bash
pip install -r requirements.txt
cd src
python data.py                   # veriyi indir
python backtest.py --div all     # walk-forward test (T1, E0, ... veya all)
python predict.py                # yaklaşan maçlar -> predictions/log.csv
python predict.py --settle       # biten maçları işle, model vs piyasa skoru
```

## Model (v1)
Zaman ağırlıklı Dixon-Coles (Poisson + düşük skor düzeltmesi), lig bazında, son 4 yıl, yarı ömür 250 gün, L2 düzenleme.
Sonuçlar (1X2) dışında Over 2.5 ve KG Var olasılıkları da loglanıyor.

## Backtest sonucu (2024-08 → bugün, her 14 günde yeniden fit)
| Lig | Model RPS | Bahisçi RPS | Model isabet | Bahisçi isabet |
|---|---|---|---|---|
| Süper Lig | 0.1970 | 0.1850 | %53.1 | %58.2 |
| Premier Lig | 0.2068 | 0.2011 | %49.5 | %51.7 |
| La Liga | 0.1984 | 0.1910 | %53.9 | %55.4 |
| Bundesliga | 0.2057 | 0.1977 | %51.4 | %54.5 |
| Serie A | 0.1974 | 0.1904 | %53.9 | %55.3 |
| Ligue 1 | 0.2059 | 0.2002 | %53.8 | %54.8 |
| Eredivisie | 0.1996 | 0.1920 | %52.4 | %54.0 |
| Primeira Liga | 0.1849 | 0.1780 | %55.5 | %56.1 |
| Belçika | 0.2075 | 0.2011 | %48.9 | %51.4 |

**Dürüst yorum:** v1 her ligde piyasanın gerisinde. Süper Lig'de fark en büyük. Bu beklenen bir sonuç:
oranlar sakatlık, kadro, motivasyon gibi bizim görmediğimiz bilgiyi içeriyor.
Hedef: farkı kapatmak, sonra (varsa) hangi segmentte geçebildiğimizi bulmak.

## Yol haritası
- [ ] Yeni terfi eden takımlar için lig-seviyesi başlangıç değeri (şu an Hull gibi takımlar sapıyor)
- [ ] Ev sahibi avantajı takım bazlı, Elo ile harman
- [ ] xG verisi (ücretsiz kaynak araştırılacak)
- [ ] Piyasa oranını özellik olarak kullanan hibrit model
- [ ] Haftalık otomatik rapor, kalibrasyon grafiği
