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

## Model (v2)
DC (Dixon-Coles, Poisson + düşük skor düzeltmesi, lig bazında, son 4 yıl, yarı ömür 250 gün) ile gol farkı ağırlıklı
**Elo** %50-%50 karışımı. Elo puanları sıralı logit ile 1X2 olasılığına çevriliyor.
Over 2.5 ve KG Var olasılıkları da loglanıyor (yalnızca DC'den).

## Backtest sonucu (2024-08 → bugün, her 14 günde yeniden fit, v2)
| Lig | Model RPS | Bahisçi RPS | Fark | v1 farkı |
|---|---|---|---|---|
| Süper Lig | 0.1962 | 0.1853 | +0.0109 | +0.0120 |
| Premier Lig | 0.2057 | 0.2012 | +0.0045 | +0.0057 |
| La Liga | 0.1977 | 0.1903 | +0.0074 | +0.0074 |
| Bundesliga | 0.2055 | 0.1985 | +0.0070 | +0.0080 |
| Serie A | 0.1967 | 0.1903 | +0.0064 | +0.0070 |
| Ligue 1 | 0.2058 | 0.2001 | +0.0057 | +0.0057 |
| Eredivisie | 0.1978 | 0.1914 | +0.0064 | +0.0076 |
| Primeira Liga | 0.1841 | 0.1782 | +0.0059 | +0.0069 |
| Belçika | 0.2067 | 0.2013 | +0.0054 | +0.0064 |

(Fark: modelin RPS'i − bahisçinin RPS'i. 0'a ne kadar yakınsa o kadar iyi. v1 sütunundaki rakamlar yaklaşık, v1'de
bilinmeyen takımlı maçlar dışarıda kalıyordu, küme biraz farklı.)

**Dürüst yorum:** Elo karışımı her ligde küçük ama tutarlı bir iyileşme verdi. Hâlâ hiçbir ligde piyasayı geçmiyoruz.
Süper Lig'de fark en büyük.

### Denenip işe yaramayanlar (Süper Lig, RPS)
| Deneme | RPS |
|---|---|
| Elo'suz DC | 0.1976 |
| + yeni terfi eden takım için negatif başlangıç (0.15) | 0.1981 (kötüleşti) |
| + takıma özel ev avantajı | 0.1983 (kötüleşti) |
| DC + Elo (%50) | **0.1962** |

Bu iki seçenek kodda duruyor (`newcomer_shift`, `team_ha_reg`) ama varsayılan olarak kapalı.

## Yol haritası
- [x] Yeni takımlar: bilinmeyen takım artık atlanmıyor, lig ortalaması alınıyor
- [x] Elo ile harman
- [ ] xG verisi (ücretsiz kaynak araştırılacak)
- [ ] Sakatlık/kadro bilgisi, piyasanın bizden iyi olduğu ana alan
- [ ] Piyasa oranını özellik olarak kullanan hibrit model
- [ ] Haftalık otomatik rapor, kalibrasyon grafiği
