# Haftalık maç paketi: kendi bilgisayarında kullanım

## Bir kerelik kurulum
```bash
git clone https://github.com/satessonmez-netizen/sports-betting-projeler
cd sports-betting-projeler
git checkout ccr-53ccebd7-15qd1c
pip install numpy pandas scipy requests beautifulsoup4 lxml
```
(Python 3.10+ önerilir.)

## Her hafta
1. `matches.txt` dosyası oluştur (örnek: `matches.example.txt`). Her satıra bir maç:
   ```
   2026-11-07 | Galatasaray - Amedspor
   Fenerbahce - Corum
   ```
   Takım adları football-data'daki yazımla aynı olmalı (Fenerbahce, Besiktas, Buyuksehyr, Ein Frankfurt...).
   Bulamazsa yakın adayları söyler.
2. Çalıştır:
   ```bash
   cd src
   python match_pack.py ../matches.txt
   ```
3. `output/match_pack_<tarih>.md` dosyasının içeriğini bana yapıştır.

Transfermarkt olmadan denemek için: `python match_pack.py ../matches.txt --no-tm`

## Neler çıkar
Model tahmini (1/X/2, beklenen gol, olası skorlar), son 5 maç formu, son 10 haftanın formu, 5 yıllık
G/B/M ve gol toplamı, karşılıklı son 5 yıl maçları, piyasa oranları, Transfermarkt kadro değeri,
en değerli 5 oyuncu, sakat/cezalı listesi ve eksik oyuncuların kadro değerindeki payı.

## Dikkat
- Transfermarkt kısmı **canlı sitede test edilmedi.** Sayfa yapısı beklediğimden farklıysa çıktıda
  "hata" yazar ve ham sayfa `data/tm_debug/` altına kaydedilir. O dosyayı bana gönder.
- İstekler arasında 4-7 sn beklenir, sonuçlar 12 saat önbelleğe alınır. Fazla istek atma, IP'n engellenebilir.
- Transfermarkt'ın kullanım şartları otomatik çekimi kısıtlayabilir. Sorumluluk sende.
- Amedspor, Çorum gibi Transfermarkt veri setinde olmayan takımlar siteden aranır. İlk sonuç otomatik
  kaydedilir. Yanlışsa `data/tm_clubs_manual.csv` dosyasında düzelt.

## Tahmin defteri (her hafta)
```bash
cd src
python ledger.py add --picks ../predictions/picks_<tarih>.csv --pack ../output/match_pack_<tarih>.json
python ledger.py settle     # maçlar bitince
python ledger.py report     # sayılarla rapor
python ledger.py errors     # yanıldığım maçlar
```
Ayrıntılar `src/ledger.py` başındaki açıklamada.
