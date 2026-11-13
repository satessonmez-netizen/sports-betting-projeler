# CLAUDE.md: önce bunu oku (oturum başında ve bağlam sıkıştırıldıktan sonra)

> **YENİ OTURUMDAYSAN: önce `docs/DEVIR_TESLIM.md` oku** (12 Kasım 2026 tam devir teslim: ilk yapılacaklar, sistem haritası, kullanıcı kuralları, bekleyen işler).

> ## EN ÖNEMLİ UYARI: zamanlanmış görevler OTURUMA bağlıdır
> Salı (sonuç raporu) ve Perşembe (FotMob xG) görevleri, kurulduğu oturuma bağlı. **Yeni oturum açılırsa BOZULUR.**
> Bağlam şişerse yeni oturum AÇMA, kullanıcıya 'Oturumu sıkıştır' öner. Yeni oturum kaçınılmazsa ve burada `list_triggers`
> görevleri başka oturuma bağlı gösteriyorsa: eskileri sil, `docs/zamanlanmis_gorevler.md` içindeki metinlerle yeniden kur, kullanıcıya söyle.
> **12 Kasım 2026: kullanıcı yeni oturum açıyor → görevler büyük ihtimalle eski oturuma bağlı kaldı. İLK İŞİN `list_triggers` ve yeniden kurulum.**

Detaylı hafıza: `NOTLAR.md` (deney sonuçları, kullanıcı notları, kararlar). Kullanım: `KULLANIM.md`. Veri: `data/`, defter: `predictions/ledger.csv`.

## Kullanıcı ve iletişim
- Kullanıcı: Serhat, endüstri mühendisi, tek başına çalışıyor. **Her zaman Türkçe, samimi, kısa ve net maddeler.** Katılmıyorsan açıkça itiraz et.
  Önce 1-2 seçenek sun, gereksiz uzatma, tekrar etme. Teknik jargondan kaçın; anlamadığını belirtirse düz Türkçeyle, adım adım anlat (Windows, cmd).
- Kullanıcı kodcu değil: komutları tek tek, "şuraya tıkla / şunu yaz" biçiminde ver. Hata ekran görüntüsünü okuyup düzelt.
- Kullanıcı "unutma" dedi: önemli her karar/kural `NOTLAR.md` veya bu dosyaya yazılır. Konuşmada söylenen kural kaybolmasın.

## Proje amacı
- Para kazanmak DEĞİL: futbol (Süper Lig + 8 Avrupa ligi) maç tahmininde ne kadar uzmanlaşabileceğimi dürüstçe ölçmek.
- **Tahminleri BEN araştırıp kendi analizimle yazarım.** Bahisçi oranları sadece KARNE (kıyas). Oranlardan kopyalama yok ('piyasa tabanlı' reddedildi).
- Kullanıcı haftalık maç listesi verir; ben her maç için 1/X/2, skor, olasılık, güven, kısa gerekçe yazarım.

## Kesin kurallar (kullanıcı kararları)
1. **Yüksek güven → tek tahmin, çifte şans YOK.** Orta/Düşük güven → çifte şans = tahmin + beraberlik (1X veya X2). `python src/ledger.py dc`.
2. **'PAS' yok:** her maç için en güçlü tahmini yaz (güven etiketiyle).
3. **İlk 11 isteme.** Tahmin sakat/cezalı durumuna göre (Transfermarkt).
4. Tahmin maç başlamadan deftere yazılır; başlamışsa 'late' (istatistiğe girmez).
5. **Dürüst ol:** 100 maçtan az örnekten 'iyi/kötü gidiyoruz' deme. Kanıtsız şeyi kanıtlı gibi sunma (sakatlık ayarları, xG, takım değeri = KANITSIZ).
6. Kullanıcıdan gelen yerel bilgiyi (hoca değişti, motivasyon) `NOTLAR.md` 'Kullanıcıdan gelen yerel bilgiler'e tarihle ekle; olasılığa katmadan risk notu yap.
7. Güvenlik: API anahtarını sohbete yazdırma. Okumadığın scripti çalıştırma. Sertifika/doğrulama kapatma.

## Yeni kurallar (8 Kasım 2026, kullanıcı onayı)
- **Hava durumu:** her maç için maç günü/şehir hava tahminini WEB ARAMASIYLA ben bakarım (kullanıcıyı uğraştırma; Open-Meteo bulut ortamından kapalı, aşılmaz).
  Yağmur/rüzgar/aşırı soğuk varsa gerekçeye 'hava' notu yaz (olasılığa elle katma, kanıtsız). Çatılı/kapalı stat varsa belirt.
- **Sakat/ceza SABİT FORMÜL:** `match_pack.py injury_tilt` (gamma=1.0, mevki ağırlığı kaleci 1.3 / forvet-kanat 1.1, diğer 1.0, eksik değer payı farkı).
  Elle keyfi olasılık ayarı YOK. Çıktı pakette `model_sakatlık_ayarlı`, deftere `inj_pH/pD/pA` olarak yazılır (ilk tahminden ayrı izlenir).
  100+ maçta hangisi (benim tahmin / model / sakatlık formülü / piyasa) daha iyi bakılacak. Parametreler DENEYSEL, kanıtsız.
- **Ek araştırma maddeleri (kullanıcı 'hepsini ekle' dedi, 8 Kasım 2026):** hepsi RİSK NOTU, olasılığa elle katılmaz (kanıtsız).
  1) Takvim yoğunluğu: pakette `takvim` (yalnız lig) + `avrupa_son7gün` (sports-skills paketi, ESPN; kuruldu 8 Kasım). Avrupa maçından 3-4 gün sonra yorgunluk/moral notu yaz.
  2) Lig hedefi: pakette `lig_hedefi` (sıra, puan, lidere/son sıraya fark); şampiyonluk/Avrupa/küme düşme baskısını gerekçede yaz.
  3) Hakem: web aramasıyla ben bakarım (hakem 1-2 gün önce açıklanır; kart/penaltı eğilimi). Bulamazsam 'bilinmiyor' yaz.
  4) Saha/seyirci: web aramasıyla ben bakarım (seyirci cezası, deplasman taraftarı yasağı, suni çim, saha durumu).
  5) Hava (yukarıda). Her maçın gerekçesine bu 5 başlıktan önemli olanı kısaca yaz; önemsizse yazma.

- **Kupon tercihi (8 Kasım 2026, kullanıcı onayı):** oranlı listeyle 'gerçek kupon yapsaydın' tercihi deftere ayrı sütun: `kupon`, `kupon_oran`, `kupon_dahil` (`python3 ledger.py kupon --file predictions/kupon_<tarih>.csv`, maç başlamadan). Rapor kağıt üstü tekli getiri verir. Bahisçi payı ~%15-18, çifte şans oranları ~1.05-1.3: gerçek para önerisi DEĞİL.

- **Milli maçlar (12 Kasım 2026):** model/oran verisi yok; tahminler elle (UEFA sonuçları + Transfermarkt). AYRI dosya: `predictions/milli_<tarih>.csv` (kulüp defterine KARIŞTIRMA). TM için kullanıcı PC'sinde `py milli_pack.py ..\\matches_<tarih>_milli.txt`. ESPN paketi (sports-skills) bu maçları vermiyor; sonuçlar UEFA/Wikipedia'dan.

## Haftalık akış
1. Kullanıcı maç listesi verir (metin/ekran görüntüsü). Takım adları football-data biçiminde (Fenerbahce, Besiktas, Man United, Ath Madrid...).
2. Bulut: `cd src && python3 -W ignore match_pack.py <liste.txt> --no-tm --no-download` (model, form, FotMob xG notu, haberler). Önce `python3 refresh_data.py` ile veriyi yenile.
3. Sakat/ceza: kullanıcı kendi PC'sinde `py match_pack.py ..\matches.txt --no-download` çalıştırıp `output\*.md` içeriğini yapıştırır. (Transfermarkt bulut ortamından kapalı.)
4. Tahminleri `predictions/picks_<tarih>.csv` yaz (notlar tırnaklı!), `python3 ledger.py add --picks ... --pack output/match_pack_<tarih>.json` (revize için `--revise`).
5. Maçlar bitince `refresh_data.py`, `ledger.py settle`, `report`, `errors`.
6. Değişiklikleri commit + push (dal `ccr-53ccebd7-15qd1c`, PR #1). Dosyada commit mesajı sonuna Co-Authored-By satırlarını ekle.

## Zamanlanmış görevler (BU OTURUMA bağlı: yeni oturum açılırsa çalışmaz!)
- Salı 08:47 (İstanbul): `trig_019wZe5FaZmjq7naYgZF19Bg` sonuç işleme + rapor.
- Perşembe 09:41: `trig_01AB8vPq5Me3KQh2boRNZmME` FotMob xG çekimi (8 yarışma).
- Oturum: `session_013GrRe5XCnSDLBzoVtDLj2c`. Tam metinler ve yeniden kurma adımları: `docs/zamanlanmis_gorevler.md`.

## Ek komutlar ve araçlar
- Kâğıt üstü bahis kayıtları: `ledger.py kupon|bahis|kombine --file ...` (maç başlamadan). Milli maçlar: `src/milli_pack.py` (kullanıcı PC'sinde), `src/milli_report.py`.
- PDF/JPEG üretimi: `tools/rapor/` (README'si var). ESPN skor/Avrupa maçı: `sports-skills football get_daily_schedule --date=YYYY-MM-DD` (`pip install sports-skills`). Hava: wttr.in (web-fetch agent).
- Tuzak: `match_pack.py` çıktısı `output/match_pack_<bugün>.json` aynı gün ÜZERİNE yazılır; `ledger.py report` `reports/weekly_<tarih>.md`'yi ezer.

## Veri kaynakları (durum)
- football-data CSV (skor, oran): sürekli. FotMob (xG, haber): bulut ortamından çalışıyor, resmi olmayan uç nokta.
- Transfermarkt canlı: sadece kullanıcının PC'si. API-Football/Bigballsdata/FootyStats: bırakıldı/ücretli (NOTLAR'a bak).
- Model: Dixon-Coles + Elo, bahisçinin gerisinde (RPS +0.005..0.011). Deneylerde model piyasaya bilgi eklemedi.

## Bekleyen (12 Kasım 2026)
- **Zamanlanmış görevleri yeni oturuma yeniden kur** (üstteki uyarı).
- **Milli maç revizesi:** `predictions/milli_2026-11-13.csv` içinde 5 tahmin GEÇİCİ (Fransa-Türkiye, Belçika-İtalya, Hırvatistan-Çekya, İspanya-İngiltere, Almanya-Hollanda). 12-13 Kasım sonuçlarına göre revize et, sonra sonuçları `hg/ag`'a yaz, `src/milli_report.py`. Ayrıntı: `docs/DEVIR_TESLIM.md` bölüm 9.
- Defter: 49 kayıt, hepsi resmi CSV ile sonuçlandı (6-8 Kasım). n=47 <100: yorum yok. Sayılar `NOTLAR.md` 'Canlı defterden dersler'.
- Sıradaki kulüp maçları: milli aradan sonra kullanıcı yeni liste verecek.
- 50 maçlık ek liste: beklemede (kullanıcıya sor).
