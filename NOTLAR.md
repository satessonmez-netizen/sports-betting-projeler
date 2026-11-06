# NOTLAR: oturumlar arası hafıza

Bu dosya, yeni bir oturumda "hangi dersleri öğrendik" sorusunun tek cevabıdır. Her hafta raporun ardından
güncellenir. Kural: **100 maçtan az örnekten sonuç çıkarma.** Bir ders eklerken kaç maça dayandığını yaz.

## Kurulu sistem
- Model: Dixon-Coles + Elo (%50/%50), son 4 yıl, yarı ömür 250 gün. Kod: `src/model.py`, `src/elo.py`.
- Veri: football-data.co.uk CSV (skor, oran). Transfermarkt: sakatlık/ceza/kadro değeri (kullanıcının PC'sinde çalışır).
- Defter: `predictions/ledger.csv`. Komutlar `src/ledger.py` (add / settle / report / errors).
- Haftalık rapor: `reports/weekly_<tarih>.md`.

## Backtest'ten bilinenler (2024-08 sonrası, ~7000 maç, güvenilir)
- Model 9 ligin hepsinde bahisçinin gerisinde (RPS farkı +0.005..+0.011, Süper Lig en büyük).
- Elo karışımı küçük ama tutarlı iyileşme verdi. Terfi eden takım cezası ve takıma özel ev avantajı işe yaramadı.
- Şut verisi (xG proxy) iyileştirme vermedi. `reg` 0.5-5 arası sonucu neredeyse değiştirmedi.
- Model güçlü takımları, özellikle deplasmandakileri, hafife alıyor (9 ligde de). Piyasa da bir miktar.
- Yeni terfi eden takımlarda (örn. Amedspor, Çorum) veri çok az (10 maç): belirsizlik büyük.

## Canlı defterden dersler (güncellenecek)
(Henüz yok. İlk 14 geçerli tahmin 6-9 Kasım 2026 haftasında kaydedildi.)

## Kurallar
- Tahmin maç başlamadan kaydedilir. Başlamış maçın tahmini 'late' sayılır.
- Piyasadan >=8 puan ayrıştığımda nedenini yaz; güçlü takım maçlarında piyasaya yaklaş (model hafife alıyor).
- Güven etiketleri: Yüksek (>=%60 ve piyasayla uyumlu), Orta, Düşük (yazı-tura).

## Denenip bırakılan veri kaynakları (ileride yeniden düşünülecek)
- **API-Football:** ücretsiz planda sadece 2022-2024 sezonları, güncel sezon kapalı. Hesap askıya alındı (sebep bilinmiyor).
  Güncel sezon + sakatlık/ilk 11 için ücretli plan gerekir. Fiyatı sitesinden kontrol et. Kullanıcı: "işimize yarayacağı zaman tekrar düşüneceğiz."
- **Bigballsdata:** Süper Lig kapsamında yok, futbolda sakatlık alanları boş döndü. Bırakıldı.
- **football-data.org:** Süper Lig büyük ihtimalle ücretsiz katmanda yok, sakatlık yok. Denenmedi.
- **Transfermarkt veri seti (dcaribou):** güncellemeler durmuş (Temmuz 2026), 2026/27 kadroları yok. Geriye dönük deney için uygun.
- **Transfermarkt'ın canlı sayfası:** kullanıcının kendi bilgisayarından çalışıyor (bulut ortamından kapalı).
  Sakatlık sayfasındaki tarihsiz satırların (3, 10, 0.30 gibi) kart uyarısı olduğu henüz DOĞRULANMADI.
