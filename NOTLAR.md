# NOTLAR: oturumlar arası hafıza

> **ÖNCE `CLAUDE.md` dosyasını oku** (kullanıcı kuralları, haftalık akış, zamanlanmış görevler, oturum uyarısı).
> Bu dosya detay: deney sonuçları, kullanıcı notları, kararlar. Kurallar `CLAUDE.md` ve aşağıdaki 'Kurallar' bölümünde.

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
- 2026-11-07 | Atlético Madrid - Barcelona | Kullanıcı görüşü (futbol bilgisiyle): (1) Atlético kazanırsa liderliğe oturur, moral/motivasyon faktörü. (2) Atlético 5/5 formda. (3) Barça daha atak oynuyor, xG üstünlüğü mantıklı. (4) Barça uzun süredir aralıksız oynuyor, Rodri ve Olmo gibi kilit oyuncular yok (TM: Olmo 21 Ekim'den, Rodri 3 Kasım'dan beri sakat). (5) Barça favori ama ÇOK GÜÇLÜ değil, sakatlıklar endişe verici. (6) Simeone bu maçı almak isteyecek. Karar: tahmin %40'ta KALSIN (benim görüşüm %45 civarıydı; defter hangimizin haklı olduğunu gösterecek).
- 2026-11-08 | Fenerbahçe | Kullanıcı: Fener 3 gün önce Liverpool'u yendi, moral/motivasyon faktörü. Doğrulandı: 4 Kasım 2026, Şampiyonlar Ligi, Fener 3-2 Liverpool (Kadıköy). Çorum maçı 8 Kasım = 4 gün sonra (Çorum 8 gün dinlendi). | Etki iki yönlü (moral yukarı, yorgunluk/rotasyon aşağı); test edilmedi, olasılığa elle katılmadı. EKSİK: paketteki `takvim` Avrupa/kupa maçlarını görmüyor, yanlış '8 gün' dedi.
  Gelecekte denenecek fikirler: mevkiye göre sakatlık (eksik savunmacı sayısı -> yenilen gol), 'lider/zirve maçı motivasyonu', bu sezon verisine (xG) daha çok ağırlık.

## Karar: sakatlık formülü ve hava (2026-11-08)
- Kullanıcı itirazı: sakat oyuncu veri, neden katmıyorsun. Cevap: elle ayarlıyordum (tutarsız); testte kaba ölçümle fayda çıkmamıştı.
  Karar: sabit formül (`injury_tilt`), mevki ağırlıklı, deftere ayrı kolon (`inj_p*`). Test: 100+ maç sonra. Mevki testi (geçmiş veri) ileride.
- Hava: web aramasıyla maç günü bakılır, gerekçede risk notu. Etki küçük beklenir (yağmur/rüzgar/soğuk -> az gol).

## Kullanıcının bildirdiği sonuçlar (CSV gelene kadar; Salı settle sırasında CSV ile doğrula)
- 2026-11-07 | Göztepe 1-2 Başakşehir (kullanıcı bildirdi). Tahminim: 1 (%48, Düşük), çifte şans 1X: İKİSİ DE TUTMADI. Defterde henüz sonuçlanmadı (CSV bekleniyor).

- 2026-11-07 sonuçları (ESPN, sports-skills; CSV gelince Salı settle ile doğrula): Eyüpspor 0-2 Kocaelispor, Samsunspor 1-0 Konyaspor, Galatasaray 4-3 Amedspor, Göztepe 1-2 Başakşehir, Stuttgart 1-0 Bremen, Valencia 0-3 Real Madrid. Yön: 5/6 doğru (sadece Göztepe yanlış). n=6, sonuç çıkarılmaz.

- 2026-11-08 | Napoli 1-1 Lazio (kullanıcı bildirdi). Tahmin 2 (Lazio) Düşük: yön TUTMADI, skor 1-1 TUTTU. X2 çifte şans tuttu. Kupon tercihi tek 2 @2.59 tutmadı. Varsayımsal 5 tekli bahiste bu bacak −100$. Kombine (43.6) bu maçta bozuldu. 5'li çifte şans kuponunda Napoli X2 bacağı tuttu.

## Bekleyen işler
**Salı 10 Kasım 2026 sabahı (Pazartesi'den ertelendi): kupon değerlendirme görüşmesi (kullanıcı ile).** Hazırlık:
1. `cd src && python3 refresh_data.py` (güncel sonuçlar; football-data CSV'leri 1-2 gün gecikebilir, sonuç gelmediyse kullanıcıdan sonuçları iste).
2. `python3 ledger.py settle`, sonra `report`, `errors`, `dc`.
3. Maç maç konuş: tahmin vs sonuç, ilk tahmin ile revize tahmin farkı (özellikle Atlético-Barça: analist %45, kullanıcı kararı %40), Yüksek güvenli 3 maçın (Galatasaray, Real Madrid, Beşiktaş) tutup tutmadığı, çifte şans isabeti.
4. n=14 (Gaziantep-Kasımpaşa 'geç' kayıt, sayılmaz) çok az: sonuç çıkarma, sadece dersleri not al.
5. Salı 08:47 otomatik rapor görevi ve Perşembe 09:41 FotMob çekimi ayrıca çalışıyor.

## Canlı defterden dersler (güncellenecek)
(Henüz yok. İlk 14 geçerli tahmin 6-9 Kasım 2026 haftasında kaydedildi.)

## Kurallar
- Tahmin maç başlamadan kaydedilir. Başlamış maçın tahmini 'late' sayılır.
- Piyasadan >=8 puan ayrıştığımda nedenini yaz; güçlü takım maçlarında piyasaya yaklaş (model hafife alıyor).
- **Kullanıcının kararı (6 Kasım 2026): tahminleri BEN araştırıp kendi analizimle yazarım.** Bahisçi oranları sadece KARNE (kıyas) olarak kullanılır, tahmin oradan kopyalanmaz. 'Piyasa tabanlı' öneri geri çekildi.
- Amaç: bahisçiyi geçmek değil; kendi tahminimin kalitesini dürüstçe ölçmek ve zayıf yanları düzeltmek. Gerçek sonuçlar defterde piyasa ile kıyaslanır.
- **Kullanıcı kuralları (7 Kasım 2026):**
  1. **Güçlü tahmin (Yüksek güven) tek yazılır; çifte şans verilmez.** Kendini garantiye almak, ödemeyi aynı oranda düşürür ve bilgi katmaz.
  2. **'PAS' yok.** Düşük güvenli maçta da en güçlü tahmin yazılır (güven etiketiyle).
  3. **Çifte şans seçeneği kalır** (`python ledger.py dc`): Orta/Düşük güvenli maçlarda HER ZAMAN 'tahmin + beraberlik' (1X veya X2). Kullanıcı: 'favoriye güvenmiyorsan çifte şansı değerlendir', örnek Çorum-Fenerbahçe için X2. ('12' vermek tahmin yönünü bozduğu için bırakıldı.)
  4. Proje 'emekleme aşamasında'; kullanıcı şu an benim maç hakkındaki fikrimi merak ediyor, ileride yönü değiştirecek. Para/oran bazlı ölçüt şimdilik istenmedi (öneri: kağıt üstü getiri, onay bekliyor).
- **İlk 11 istenmez (kullanıcı, 7 Kasım 2026):** İlk 11 maçtan ~1 saat önce açıklanıyor, tahminler ondan önce yazılıyor.
  Tahminler SAKAT ve CEZALI durumuna göre güncellenir (Transfermarkt, `match_pack.py`). Kullanıcıdan 'ilk 11 çıkınca yaz' diye istekte bulunma.
  Hatırlatma: sakatlığa göre yaptığım ayarların faydası geçmiş testte kanıtlanmadı (NOTLAR'daki deney bölümü).
- Güven etiketleri: Yüksek (>=%60 ve piyasayla uyumlu), Orta, Düşük (yazı-tura).

## Denenip bırakılan veri kaynakları (ileride yeniden düşünülecek)
- **API-Football:** ücretsiz planda sadece 2022-2024 sezonları, güncel sezon kapalı. Hesap askıya alındı (sebep bilinmiyor).
  Güncel sezon + sakatlık/ilk 11 için ücretli plan gerekir. Fiyatı sitesinden kontrol et. Kullanıcı: "işimize yarayacağı zaman tekrar düşüneceğiz."
- **Bigballsdata:** Süper Lig kapsamında yok, futbolda sakatlık alanları boş döndü. Bırakıldı.
- **football-data.org:** Süper Lig büyük ihtimalle ücretsiz katmanda yok, sakatlık yok. Denenmedi.
- **Transfermarkt veri seti (dcaribou):** güncellemeler durmuş (Temmuz 2026), 2026/27 kadroları yok. Geriye dönük deney için uygun.
- **Transfermarkt'ın canlı sayfası:** kullanıcının kendi bilgisayarından çalışıyor (bulut ortamından kapalı).
  Sakatlık sayfasındaki tarihsiz satırların (3, 10, 0.30 gibi) kart uyarısı olduğu henüz DOĞRULANMADI.
