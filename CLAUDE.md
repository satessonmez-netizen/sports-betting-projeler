# CLAUDE.md: önce bunu oku (oturum başında ve bağlam sıkıştırıldıktan sonra)

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
- Oturum: `session_013GrRe5XCnSDLBzoVtDLj2c`. Bağlam şişerse yeni oturum AÇMA: 'Oturumu sıkıştır' kullan. Yeni oturum şart olursa görevleri yeniden kur.

## Veri kaynakları (durum)
- football-data CSV (skor, oran): sürekli. FotMob (xG, haber): bulut ortamından çalışıyor, resmi olmayan uç nokta.
- Transfermarkt canlı: sadece kullanıcının PC'si. API-Football/Bigballsdata/FootyStats: bırakıldı/ücretli (NOTLAR'a bak).
- Model: Dixon-Coles + Elo, bahisçinin gerisinde (RPS +0.005..0.011). Deneylerde model piyasaya bilgi eklemedi.

## Bekleyen
- **Pazartesi 9 Kasım 2026:** kullanıcı ile 14 maçlık kuponun değerlendirmesi (hazırlık adımları `NOTLAR.md` 'Bekleyen işler').
- 50 maçlık ek liste kullanıcıdan gelecek (beklemeye alındı).
