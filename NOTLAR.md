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

## Deney sonuçları: piyasa karşısında model ve sakatlık (2026-11-06, ~2700 test maçı, güvenilir)
Veri: 9 lig, fit 2024-08→2025-06, test 2025-07→2026-06, test RPS (düşük iyi).
- **Model, piyasanın üstüne bilgi eklemiyor.** Logloss'a göre en iyi karışımda model payı %0 (hem kapanış hem açılış oranına karşı).
  Test RPS: piyasa 0.1946-0.1952, model 0.2001-0.2007. Karışım = piyasa.
- **Açılış oranı ≈ kapanış oranı** (0.1948 vs 0.1946): piyasa ilk günden neredeyse "doğru". Tahmin günler önce yazılsa bile açılış oranı yeterli.
- **'Eksik oyuncu değeri' (kadroda olmayan değerli oyuncular) tahmini iyileştirmedi.** Katsayı beklenen yönde (+0.3..0.7)
  ama test RPS farkı ~+0.0001 (%95 aralık sıfırı kapsıyor), hem model hem piyasa üstünde. Ölçüm kadro dışını (rotasyon dahil)
  sayar, gerçek sakatlığı ayırmaz; yani 'sakatlık etkisiz' demek için KESİN kanıt değil, ama iyileşme göstermedi.
- Sonuç: sakatlığa göre elle yaptığım olasılık ayarları **kanıtsız**. Defterde ayrıca izleniyor (ilk tahmin ve revize ayrı).

### Yeni özellikler, MODEL üstünde (aynı test)
- **Takım değeri oranı** (log, aktif kadro piyasa değeri toplamı): model test RPS 0.2007 → 0.2001 (fark -0.0007, %95 [-0.0016, +0.0002]).
  Yön doğru, etki küçük ve istatistiksel olarak kesin değil. Canlı hatta DENEYSEL olarak eklendi (`model_değer_ayarlı`, beta=0.098).
- **Yorgunluk (son maça kaç gün, tüm turnuvalar):** etki yok (beta ≈ -0.01, RPS değişmedi). Eklenmedi.

### xG (beklenen gol) araştırması
- FootyStats maç CSV'si (Premier Lig 2018/19, 380 maç) incelendi: xG var, ama indirme ÜCRETLİ, çoklu sezon/lig alınamıyor.
- Tek sezon testi (330 maç): geçmiş 8 maç xG farkı ile sonraki maç gol farkı korelasyonu 0.456; gol farkı 0.458, isabetli şut 0.456. xG daha iyi değil.
- FBref Ocak 2026'da xG verilerini kaldırdı. Understat Süper Lig'i kapsamıyor (üçüncü taraf bilgi). Ücretsiz toplu Süper Lig xG verisi bulunamadı.
- Karar: xG için ödeme yapılmıyor. İsteğe bağlı: FotMob/Statz.ai'dan elle bakılıp 'risk notu' olarak kullanılır, olasılığa katılmaz.
- Not: FootyStats CSV'sinin her satırı tek tırnak içinde (bozuk biçim). Ayrıştırma: önce satırı csv ile oku, sonra içindeki tek alanı tekrar ayrıştır.

### İleride değerlendirilecek xG kaynakları (kullanıcı: "aklımızda kalsın, zamanla en uygununu alırız")
- **FotMob** (fotmob.com/teams/<id>/stats): takım/oyuncu xG, xGA, xGOT, xA. Resmi API yok, kullanım şartlarını kontrol et.
- **Statz.ai** (statz.ai/competitions/super-lig/stats): 2026/27 takım tablosu, xG, xGA, xG farkı.
- Plan: önce haftalık elle xG notu (risk notu olarak), 10+ hafta birikince defterde faydasına bak. Fayda görülürse
  en uygun kaynak seçilir; otomatik çekimden önce kullanım şartları ve erişim (bulut/PC) kontrol edilir.

## Canlı defterden dersler (güncellenecek)
(Henüz yok. İlk 14 geçerli tahmin 6-9 Kasım 2026 haftasında kaydedildi.)

## Kurallar
- Tahmin maç başlamadan kaydedilir. Başlamış maçın tahmini 'late' sayılır.
- Piyasadan >=8 puan ayrıştığımda nedenini yaz; güçlü takım maçlarında piyasaya yaklaş (model hafife alıyor).
- **Kullanıcının kararı (6 Kasım 2026): tahminleri BEN araştırıp kendi analizimle yazarım.** Bahisçi oranları sadece KARNE (kıyas) olarak kullanılır, tahmin oradan kopyalanmaz. 'Piyasa tabanlı' öneri geri çekildi.
- Amaç: bahisçiyi geçmek değil; kendi tahminimin kalitesini dürüstçe ölçmek ve zayıf yanları düzeltmek. Gerçek sonuçlar defterde piyasa ile kıyaslanır.
- Güven etiketleri: Yüksek (>=%60 ve piyasayla uyumlu), Orta, Düşük (yazı-tura).

## Denenip bırakılan veri kaynakları (ileride yeniden düşünülecek)
- **API-Football:** ücretsiz planda sadece 2022-2024 sezonları, güncel sezon kapalı. Hesap askıya alındı (sebep bilinmiyor).
  Güncel sezon + sakatlık/ilk 11 için ücretli plan gerekir. Fiyatı sitesinden kontrol et. Kullanıcı: "işimize yarayacağı zaman tekrar düşüneceğiz."
- **Bigballsdata:** Süper Lig kapsamında yok, futbolda sakatlık alanları boş döndü. Bırakıldı.
- **football-data.org:** Süper Lig büyük ihtimalle ücretsiz katmanda yok, sakatlık yok. Denenmedi.
- **Transfermarkt veri seti (dcaribou):** güncellemeler durmuş (Temmuz 2026), 2026/27 kadroları yok. Geriye dönük deney için uygun.
- **Transfermarkt'ın canlı sayfası:** kullanıcının kendi bilgisayarından çalışıyor (bulut ortamından kapalı).
  Sakatlık sayfasındaki tarihsiz satırların (3, 10, 0.30 gibi) kart uyarısı olduğu henüz DOĞRULANMADI.
