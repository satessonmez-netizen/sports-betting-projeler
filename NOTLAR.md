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

### İleride satın alma adayı ücretli kaynaklar (kullanıcı: "aklımızda kalsın, zamanla en uygununu alırız")
Adaylar: **FootyStats** ve **API-Football**. Henüz hiçbiri alınmadı. Fiyat/plan bilgisi doğrulanmadı, karar anında resmi sitelerden kontrol edilecek.
- **FootyStats** (ücretli): maç bazlı CSV (xG, şut, topa sahip olma, korner, kart, hakem, oranlar, 1X2/ÜST/KG), lig ve sezon başına indirme.
  Faydası: geçmiş çoklu sezon xG ile xG'nin tahmini iyileştirip iyileştirmediğini TEST etmeyi sağlar. Dosya biçimi bozuk (satır tek tırnakta), ayrıştırma notu yukarıda.
- **API-Football** (ücretsiz plan işe yaramadı; ücretli plan gerekir): güncel sezon, sakatlık/ceza, ilk 11, fikstür, API ile otomasyon.
  Faydası: bugün elle ve kullanıcının PC'sinden çektiğimiz Transfermarkt bilgisini otomatikleştirir. Hesap geçmişte askıya alınmıştı (sebep bilinmiyor).
- **Ne zaman karar verilir:** defterde 10+ hafta (100+ geçerli maç) birikince. Soru: tahminlerim hangi tür maçta yanlış, eksik olan bilgi xG mi, sakatlık/ilk 11 mi?
  Hangisi eksikse o kaynak alınır. İki bilgi de şu an KANITSIZ (xG tek sezon testte gollerden iyi çıkmadı, eksik oyuncu değeri iyileştirmedi).
- Ücretsiz alternatif (elle, olasılığa katmadan risk notu): FotMob ve Statz.ai takım xG sayfaları.

### FotMob xG hattı (kuruldu, 2026-11-06)
- `src/fotmob_stats.py`: tarihli anlık görüntü + `data/fotmob/history.csv` (uzun biçim). Süper Lig (lig 71, sezon 42167) aktif.
- Diğer ligler için FotMob istatistik sayfası adresi `--add-url` ile eklenir (adreste lig ve sezon kimliği var).
- 'sub_value': xG için GERÇEK gol, yenilen xG için yenilen gol, xG farkı için gol farkı (CSV ile doğrulandı).
- Kullanım: olasılığa katılmaz, `fotmob_xg_notu` olarak risk notu. 10+ hafta birikince defterde faydasına bakılacak.
- Şans göstergesi: (attığı gol - xG). Örn. 6 Kasım 2026: Çorum +8.0 (xG 13.0, gol 21), Konyaspor -5.6, Eyüpspor -5.0. Büyük pozitif şans sürdürülemez olabilir.

### FotMob haber ve takım sayfası (2026-11-06 incelendi)
- `src/fotmob_news.py`: genel haber akışı (www.fotmob.com/api/worldnews, 20 haber/sayfa, İngilizce). Takım filtresi yok, ad aliaslarıyla biz filtreliyoruz.
  Avrupa büyük takımları için iyi (muhtemel 11, hoca açıklaması, sakatlık süresi), **Süper Lig kapsamı zayıf** (Galatasaray son ~2 günde 0 haber).
  Türk kulüpleri için web araması ya da kullanıcı notu gerekir.
- FotMob takım sayfası: kadro, form, sıradaki maç, transferler, hoca geçmişi var. **Sakat/cezalı alanı güvenilmez** (son maç kadrosuna göre, eski):
  Osimhen sakatlığı FotMob'da yoktu, Transfermarkt'ta vardı. Sakatlık kaynağı Transfermarkt olarak kalır.
- Haberler olasılığa katılmaz, `haber_basliklari` olarak risk notu.

## Kullanıcıdan gelen yerel bilgiler (doğrulanmamış, kullanıcı bildirdi)
Biçim: tarih | takım | bilgi | tahmine etkisi. Haber/teknik direktör/motivasyon gibi benim erişemediğim bilgiler buraya yazılır.
- 2026-11-07 | Fenerbahçe | Teknik direktör değişti, Emre Belözoğlu geldi | Etkisi bilinmiyor. Yeni hoca etkisini geçmiş veride test etmedik. İlk maçı Çorum - Fenerbahçe (8 Kasım). Model hoca değişikliğini bilmez: son 4 yıllık güce bakar.

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
