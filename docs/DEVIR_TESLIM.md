# DEVİR TESLİM: yeni oturumda önce bunu oku (12 Kasım 2026 durumu)

Bu dosya, önceki oturumun (`session_013GrRe5XCnSDLBzoVtDLj2c`) tüm bilgisini taşır. Kısa kurallar için `CLAUDE.md`,
deney sonuçları ve kullanıcı notları için `NOTLAR.md`, kullanım komutları için `KULLANIM.md` var. Buradaki bilgiyle
kullanıcı sana ek açıklama yapmadan kaldığımız yerden devam edebilirsin.

## 0) Yeni oturumda İLK yapılacaklar (sırayla)
1. `CLAUDE.md`, bu dosya ve `NOTLAR.md` oku. Kullanıcıya Türkçe, kısa, samimi yaz (kuralları `CLAUDE.md`'de).
2. Ortamı kur (konteyner her oturumda sıfırdır; kurulumlar kaybolur):
   ```bash
   cd /home/user/sports-betting-projeler && git checkout ccr-53ccebd7-15qd1c && git pull origin ccr-53ccebd7-15qd1c
   pip install -r requirements.txt            # numpy pandas scipy requests beautifulsoup4 lxml sports-skills (+penaltyblog notu dosyada)
   cd src && python3 -W ignore refresh_data.py && python3 -W ignore ledger.py settle && python3 -W ignore ledger.py report | head -20
   ```
3. **ZAMANLANMIŞ GÖREVLER OTURUMA BAĞLIDIR.** `list_triggers` çağır. `persistent_session_id` eski oturum
   (`session_013GrRe5XCnSDLBzoVtDLj2c`) ise görevler yeni oturumda ÇALIŞMAZ. Çözüm:
   - `delete_trigger` ile iki eski görevi sil: `trig_019wZe5FaZmjq7naYgZF19Bg` (Salı) ve `trig_01AB8vPq5Me3KQh2boRNZmME` (Perşembe).
   - `docs/zamanlanmis_gorevler.md` içindeki iki metni `create_trigger` ile yeniden kur (varsayılan: bu oturuma bağlı, `initiation: human_request`).
   - Kullanıcıya söyle. (Listede alakasız başka görevler de var: "Goalserve API key kontrolü" x2 başka oturuma ait, "Sabah ürün adı…" başka projeye ait ve kapalı. Dokunma.)
   - Doğrulama: Salı 10 Kasım 08:47 ve Perşembe 12 Kasım 09:41 görevleri eski oturumda çalıştı (Salı'nın ilk iletisi yarıda kalmıştı, Perşembe sonradan tekrar çalıştırıldı).
4. Bekleyen işlere bak (bölüm 12). Özellikle **milli maç revizesi** (13-16 Kasım).

## 1) Proje ve kullanıcı
- Kullanıcı **Serhat**: endüstri mühendisi, tek başına çalışıyor, 5 yıldır pazaryerlerinde halı satıyor (bu projeyle ilgisiz), kodcu DEĞİL.
  Windows kullanıyor, komutları cmd'de tek tek, "şuraya tıkla / şunu yaz" biçiminde ister. Hata ekran görüntüsü atar, oku ve düzelt.
  İletişim: her zaman Türkçe, samimi, kısa ve net maddeler, katılmıyorsan açıkça itiraz et, önce 1-2 seçenek, gereksiz uzatma/tekrar yok.
- **Amaç:** para kazanmak DEĞİL. Futbol maç tahmininde ne kadar uzmanlaşabileceğimi dürüstçe ölçmek (öğrenme/ölçüm projesi, "emekleme aşaması").
  Kapsam: Süper Lig + 8 Avrupa ligi (Premier, La Liga, Bundesliga, Serie A, Ligue 1, Eredivisie, Primeira, Belçika) + (yeni) milli maçlar.
- **Tahminleri BEN araştırıp kendi analizimle yazarım.** Bahisçi oranları sadece karne/kıyas. ("Piyasa tabanlı tahmin" kullanıcıyla konuşulup REDDEDİLDİ.)
  Kullanıcı kuponda oranı açıkça verdiğinde (oranlı PDF) ona göre kupon tercihi yaptım; yine de tahmin oranlardan kopyalanmaz.
- Kullanıcı "konuştuklarımızı unutma" dedi: her karar/kural repoya yazılır.

## 2) Kesin kullanıcı kuralları
1. **Yüksek güven (>=%60 ve piyasayla uyumlu) → tek tahmin, çifte şans YOK.** Orta/Düşük → çifte şans = tahmin + beraberlik (1X/X2). `ledger.py dc`.
2. **'PAS' yok:** her maç için en güçlü tahmin, güven etiketiyle.
3. **İlk 11 isteme.** (Kullanıcı gönüllü verirse kullan.) Sakat/cezalı bilgisi Transfermarkt'tan.
4. Tahmin maç başlamadan deftere (başlamışsa `late`, istatistiğe girmez).
5. **Dürüst ol:** 100 maçtan az örnekle iyi/kötü deme. Kanıtsız şeyi (sakatlık ayarı, xG, takım değeri, yorgunluk, hava) kanıtlı gibi sunma; risk notu olarak yaz.
6. Kullanıcıdan gelen yerel bilgi (hoca değişti vb.) `NOTLAR.md` 'Kullanıcıdan gelen yerel bilgiler'e tarihle; olasılığa elle katma.
7. **Sakat/ceza SABİT FORMÜL** (`match_pack.py injury_tilt`, gamma=1.0, kaleci 1.3 / forvet-kanat 1.1): elle keyfi olasılık ayarı yok; çıktı `inj_p*` sütununda ayrı izlenir.
8. **Her maça bakılacaklar:** form, puan durumu/hedef, takvim + son 7 gündeki Avrupa maçı, sakat/ceza, hava (wttr.in), hakem (bulunursa), saha/seyirci. Hepsi risk notu.
9. Kupon/bahis kayıtları **kâğıt üstü**, gerçek bahis önerisi değil. Kullanıcı "hep tutacak hale getireceğiz" dediğinde itiraz ettim: hedef hatayı azaltmak ve güveni doğru kurmak.
10. Güvenlik: API anahtarını sohbete yazdırma (ortam 'network secrets' / `request_credential`), sertifika doğrulamasını kapatma, okumadığın scripti çalıştırma, engelli siteyi (Transfermarkt bulutta kapalı) aşmaya çalışma. Hesaptaki diğer beceri/uygulamalara (sosyal medya, Canva vb.) bu projede dokunma (kullanıcı: "proje dışı işin yok").

## 3) Sistem haritası (repo)
| Yol | Ne |
|---|---|
| `src/model.py`, `elo.py`, `data.py`, `metrics.py`, `backtest.py`, `predict.py`, `scan.py`, `segments.py` | Dixon-Coles + Elo model (50/50), RPS/Brier/logloss, walk-forward backtest |
| `src/refresh_data.py` | football-data CSV'lerini indirir, `data/fixtures_snapshot.csv` yazar (oranlı fikstür) |
| `src/match_pack.py` | Haftalık maç paketi: model, form, 5y kayıt, H2H, piyasa (sadece karne), `lig_hedefi`, `takvim`, `avrupa_son7gün`, FotMob xG notu, haber, TM (--no-tm ile kapatılır), `model_değer_ayarlı`, `model_sakatlık_ayarlı`. **Dikkat: çıktı adı `output/match_pack_<BUGÜNÜN tarihi>.json`; aynı gün ikinci çalıştırma ÜZERİNE YAZAR** (bir kez 8 maçlık paketi küçük testle ezdim). `output/` gitignore'da. |
| `src/tm_scraper.py` | Transfermarkt kadro/sakat (SADECE kullanıcının PC'sinde çalışır), önbellek 12 sa, 4-7 sn bekleme. `data/tm_clubs.csv` (+`NT` milli satırları), `tm_clubs_manual.csv` |
| `src/milli_pack.py` | Milli takımlar için TM paketi (kimlik doğrulamalı: sayfa başlığı kontrolü). Kullanıcı PC'sinde: `py milli_pack.py ..\matches_2026-11-13_milli.txt` |
| `src/milli_report.py` | `predictions/milli_*.csv` hg/ag doldurulunca isabet özeti |
| `src/fotmob_stats.py`, `fotmob_news.py` | FotMob xG anlık görüntüsü ve haberleri (`data/fotmob/`). Resmi olmayan uç nokta. Tam çekim ~2-4 dk sürebilir, arka planda çalıştır |
| `src/ledger.py` | Tahmin defteri (`predictions/ledger.csv`): add, settle, report, errors, dc, kupon, bahis, kombine |
| `src/exp_absence.py`, `tm_value.py` | Geçmiş deneyler (eksik oyuncu değeri, takım değeri) |
| `predictions/picks_*.csv` | Tahmin girdileri (notlar TIRNAKLI olmalı). `_rev1..8` revizeler, `_noTM` TM'siz 42 maçlık çalışma, `_new` ledger'a eklenen 34 yeni maç |
| `predictions/kupon_*.csv`, `bahis_*.csv`, `kombine_*.csv` | Kâğıt üstü kupon kayıtlarının girdileri |
| `predictions/milli_2026-11-13.csv` | 15 milli maç tahmini (AYRI, kulüp defterine karışmaz) |
| `reports/` | Haftalık rapor md (`ledger.py report` yazar), PDF/JPEG çıktılar, backtest csv |
| `tools/rapor/` | PDF/JPEG üreten tek seferlik betikler (README'si var) |
| `.agents/skills/football-data` (+`.claude/skills` symlink) | Kurulu beceri (machina-sports). `betting` becerisi KALDIRILDI |
| `docs/zamanlanmis_gorevler.md` | İki zamanlanmış görevin tam metni |

## 4) Haftalık akış (kulüp maçları)
1. Kullanıcı maç listesini (metin/ekran görüntüsü/PDF) verir. Takım adlarını football-data yazımına çevir (Fenerbahce, Besiktas, Man United, Ath Madrid, FC Koln, Sp Braga, Nijmegen...). `match_pack.resolve` uyarırsa adayları söyler.
2. Bulutta: `cd src && python3 -W ignore refresh_data.py && python3 -W ignore match_pack.py ../matches_<tarih>.txt --no-tm --no-download --no-news` (Avrupa kontrolü ilk maçta ~2 dk sürer; 110 sn'yi aşarsa arka plana al).
3. Sakat/ceza için kullanıcı kendi PC'sinde `py match_pack.py ..\matches.txt --no-download` çalıştırır, `output\*.md` içeriğini yapıştırır (bölüm 6).
4. Hava: `wttr.in/<Şehir>?format=j1` (web-fetch agent ile; Open-Meteo bulutta kapalı). Hakem/seyirci: web araması (çoğu zaman bulunamadı → "bilinmiyor").
5. Tahminleri yaz: `predictions/picks_<tarih>.csv` → `python3 -W ignore ledger.py add --picks ../predictions/picks_<tarih>.csv --pack ../output/match_pack_<tarih>.json` (revize: `--revise`; başlamış maç reddedilir). Sakat formülü yoksa pakete `injury_tilt` ile elle ekle (yaptım: bkz. NOTLAR).
6. Oranlı liste gelirse: kupon tercihini `predictions/kupon_<tarih>.csv`'ye yaz → `ledger.py kupon --file ...`; istenirse bahis/kombine.
7. Maçlar bitince: `refresh_data.py` → `ledger.py settle` → `report` → `errors`. CSV 1-2 gün gecikebilir; hızlı bakış için ESPN (`sports-skills football get_daily_schedule --date=...`), resmi doğrulama CSV ile.
8. NOTLAR.md "Canlı defterden dersler" güncelle (sadece sayılar, n<100 ise yorum yok). Commit + push (dal `ccr-53ccebd7-15qd1c`).

## 5) Defter ayrıntıları
- Satır kimliği: `<tarih>|<lig>|<ev>|<dep>`. İlk tahmin `first_p*` ve `first_pick`'te kalır; revizeler `pick/pH/pD/pA/score/conf/note`'u günceller (`revision` artar). `model_p*` model, `inj_p*` sakat formülü, `open_o*`/`bo_*` açılış, `cl_o*`/`bc_*` kapanış oranı.
- Ek sütunlar: `kupon,kupon_oran,kupon_dahil` (28 maçlık oranlı tercih; ✅ = 5'li kuponda, yedek), `bahis,bahis_oran,bahis_tutar` (5 tekli, 100$), `kombine,kombine_oran,kombine_tutar` (43.6'lık).
- Bilinen tuzaklar: pandas 3'te metin sütunları `object` okunmalı (kodda yapıldı); olasılıklar eşitse rapor `argmax` ile ilkini sayar (Rennes-Lille .36/.28/.36: pick 2 idi, rapor 1 saydı → isabet 1 maç eksik görünür, DÜZELTİLMEDİ); `report` her çalışınca `reports/weekly_<tarih>.md` dosyasının ÜZERİNE yazar (test için sahte ledger'la çalıştırırsan geri al: `git checkout reports/`); defterde 5'li çifte şans kuponu (Brighton 1X, Napoli X2, Monza X2, Inter 1X, Rennes X2; oran 3.23) kayıtlı DEĞİL, sadece PDF'te ve NOTLAR'da.
- Resmi sonuç sayıları (12 Kasım): 49 kayıt, 47 geçerli (2 `late`), hepsi sonuçlandı. İsabet ben %68, piyasa %70, model %68; RPS ben 0.1827, piyasa 0.1606, model 0.1790. Yüksek 7/7, Orta %77 (22), Düşük %44 (18). Çifte şans %82 (n=40). Kupon tercihi 23/28, net +2.71 birim; 5 tekli bahis +135$; 5'li çifte şans kuponu TUTTU; kombine tutmadı.

## 6) Kullanıcının PC'si (Windows) ve sık takılmalar
- Kullanıcı projeyi **GitHub'dan ZIP olarak** indiriyor (klasör adı `sports-betting-projeler-ccr-53ccebd7-15qd1c`, masaüstünde). ZIP'te `git pull` çalışmaz: yeni kod gerektiğinde YENİ ZIP indirmesini iste (GitHub'da dal `ccr-53ccebd7-15qd1c` → Code → Download ZIP → "Tümünü ayıkla"; çöp kutusu/New branch/Protect'e dokunmasın).
- Çalıştırma: klasörde adres çubuğuna `cmd` → `cd src` → `py match_pack.py ..\matches.txt --no-download` (TM ~4-7 sn/istek, dakikalar sürer, Ctrl+C yapma) → `output\match_pack_<tarih>.md` içeriğini Not Defteri'nden kopyalayıp yapıştırır.
- `matches.txt` her maç AYRI satırda olmalı (bir kez tek satıra yapıştırdı → "Satır anlaşılamadı"). Türkçe karakter yok, football-data yazımı.
- football-data.co.uk sitesine PC'sinden SSL hatası alıyor (self-signed) → `--no-download` kullan; CSV'leri repo taşıyor (bulutta indirilip commit'lenir).
- Milli takım programı (`milli_pack.py`) ilk gerçek denemede sorunsuz çalıştı (30 takım, 12 Kasım).
- Not: bir kez komut yerine `bulgaria bulgaristan` yazdı (zararsız). Komutları kopyalanabilir kod bloğunda ver.

## 7) Veri kaynakları: ne çalışıyor
| Kaynak | Durum |
|---|---|
| football-data.co.uk CSV (skor + oran) | Bulutta çalışır, 1-2 gün gecikir. Pinnacle/Bet365 kapanış oranı = "piyasa" karnesi |
| FotMob (xG, haber) | Bulutta çalışır, resmi olmayan uç nokta; haftalık çekim Perşembe. Süper Lig haber kapsamı zayıf |
| sports-skills (ESPN) | `pip install sports-skills`. Skor/fikstür/Avrupa maçı OK (`get_daily_schedule`); xG sadece büyük 5 lig; sakatlık sadece Premier; milli maçlarda scoreboard BOŞ döner |
| Transfermarkt | Bulutta KAPALI (aşmaya çalışma). Kullanıcının PC'sinden çalışır. Tarihsiz satırların kart uyarısı olduğu DOĞRULANMADI. Milli sayfalarında mevki alanı boş (`mevki: null`) → mevki ağırlığı uygulanmaz |
| wttr.in | Web-fetch agent ile çalışır (saatlik yağış/rüzgar/sıcaklık). Open-Meteo bulutta engelli |
| UEFA/Wikipedia (milli) | Web-fetch agent ile sonuç ve grup tabloları; Wikipedia tabloları kırpılabiliyor, UEFA fikstür sayfası tam |
| Web araması | Hakem/ilk 11/sakat haberi için çoğu zaman eski sezon sonuçları döner; güvenme, "bilinmiyor" yaz |
| API-Football, Bigballsdata, FootyStats, football-data.org | Bırakıldı/ücretli (NOTLAR'a bak). API-Football anahtarı ortam secret'ında duruyor olabilir; silmek kullanıcının kararı |
| `betting` becerisi | Kaldırıldı (yalnız hesap, projeye katkısı yok). `football-data` becerisi kaldı |

## 8) Başlıca bulgular (ayrıntı: NOTLAR.md)
- Backtest (~7000 maç): model 9 ligin hepsinde piyasanın gerisinde (RPS +0.005..0.011). Model güçlü takımları, özellikle deplasman favorilerini, hafife alıyor.
- Piyasaya bilgi eklemedi: eksik oyuncu değeri, yorgunluk (dinlenme günü), xG (tek sezon testi); takım değeri oranı çok küçük kazanç (deneysel, beta 0.098).
- Canlı (n=47): güven etiketleri işe yarıyor gibi (Yüksek 7/7) ama n küçük; kayıp yönlerin yarısından fazlası beraberlik.
- **Oranlı bahis analizi (8 Kasım):** kullanıcının bülteninde bahisçi payı %15-18 (Pinnacle ~%2-3). Çifte şans oranları 1.05-1.30, payı tekliden büyük; "güvenmiyorsan çifte şans" kuralı ödemede neredeyse değersiz. Her seçeneğin beklenen getirisi −%7..−%25; 5'li kombinelerde −%45..−%50. Kendi olasılığımı piyasaya çekince EV'yi maksimize eden seçim hep underdog çıkıyor (modelin favori hafife alma yanlılığı) → bu yola güvenme.
- Çorum-Fener 0-5, Fener'i Liverpool yorgunluğu/yeni hoca gerekçesiyle %45→%43'e çekmem hataydı (güçlü takımı hafife alma örneği).
- Avrupa kontrolü ilk kez kullanıcı Fener-Liverpool'u hatırlatınca gündeme geldi; sonra `avrupa_son7gün` pakete eklendi. Bilinen eksik: Milan'ın Perşembe Avrupa maçı pakette görünmedi (rekabet kimliği kapsamı).

## 9) Milli maç çalışması (12 Kasım 2026)
- Dosyalar: `matches_2026-11-13_milli.txt` (liste), `data/milli_tm_2026-11-12.csv` (TM özeti), `predictions/milli_2026-11-13.csv` (15 tahmin; hg/ag boş).
- Model/oran/ESPN verisi YOK; tahminler UEFA sonuçları + TM kadro değeri/sakat + kişisel yargı. Kullanıcının ekran görüntüsündeki yüzdeleri KOPYALAMADIM.
- Tahminler: Bulgaristan-İzlanda 2 (X2), Lihtenştayn-Azerbaycan 2 (Yüksek), Lüksemburg-Estonya X (X2), Slovakya-Faroe 1 (Yüksek), Gürcistan-Macaristan 1 (1X; Macaristan'da Szoboszlai yok), Norveç-Galler 1 (1X), Portekiz-Danimarka 1 (1X), Fransa-Türkiye 1 (Yüksek), Belçika-İtalya 2 (X2), Hırvatistan-Çekya 1 (1X), İspanya-İngiltere 1 (1X), Almanya-Hollanda 1 (1X), K.Makedonya-Slovenya 2 (X2), Yunanistan-Sırbistan 1 (1X), İsviçre-İskoçya 1 (Yüksek).
- **GEÇİCİ olanlar (revize et):** Fransa-Türkiye, Belçika-İtalya, Hırvatistan-Çekya, İspanya-İngiltere (12 Kasım akşamı Türkiye-Belçika, İtalya-Fransa, Çekya-İspanya, İngiltere-Hırvatistan sonuçlarına bağlı), Almanya-Hollanda (13 Kasım Sırbistan-Almanya, Hollanda-Yunanistan). Revize edince `predictions/milli_*.csv` güncelle, JPEG'i yenile (`tools/rapor/shot.js`).
- Sonuçlar bitince `hg/ag` doldur → `python3 src/milli_report.py predictions/milli_2026-11-13.csv`.
- UEFA tabloları (6 Ekim itibarıyla): A1 Fransa 10, İtalya 7, Belçika 6, Türkiye 0 (11 yedi); A2 Hollanda 8, Yunanistan 8, Almanya 5, Sırbistan 0; A3 İspanya 12, İngiltere 9, Hırvatistan 3, Çekya 0; A4 Portekiz 12, Danimarka 6, Galler 3, Norveç 3; B1 İsviçre 12, Slovenya 7, İskoçya 4, K.Makedonya 0; B2 K.İrlanda 8, Macaristan 7, Ukrayna 4, Gürcistan 2; C3 Slovakya 10, Faroe 4, Moldova 4, Kazakistan 2; C4 İzlanda 8, Estonya 6, Bulgaristan 4, Lüksemburg 3; D2 Azerbaycan 5, Litvanya 4, Lihtenştayn 1. Playoff çekilişi 20 Kasım.

## 10) Dikkat edilecek davranış kalıpları
- Kullanıcı sık sık "ne olur / neden / tablo hazırla / pdf ver / jpeg ver" ister: kısa cevap + gerekirse dosya (`SendUserFile`, gönderdikten sonra depoya commit). PDF'i göndermeden önce Read ile sayfayı gör.
- Yeni dosya/çıktı üretince commit + push (Stop hook zorluyor); mesaj sonuna Co-Authored-By ve Claude-Session satırlarını (sistem hatırlatması hangi modeli diyorsa) ekle.
- Arka plan görevlerinin sonucunu bildirimden oku; `sleep` ile bekleme.
- Hatalarımı açıkça kabul et (örn. "piyasa tabanlı" önerisi, takvimin Avrupa'yı görmemesi, paket üzerine yazma, test için raporu ezme).

## 11) Kullanıcının kararlarının kısa listesi (kronolojik)
Süper Lig + ücretsiz CSV + Avrupa ligleri ile başla → modele Elo ekle → sakatlık Transfermarkt'ı kullanıcının PC'sinden → FotMob xG her Perşembe → tahminleri ben yazarım → Yüksek güvende tek/Orta-Düşükte çifte şans → PAS yok → ilk 11 isteme → 50 maçlık ek liste beklemede (sonra 28-42 maçlık günlük listeler geldi) → Atlético-Barça %40 kalsın (kullanıcının görüşü) → kupon değerlendirmesi Salı → hava/hakem/takvim/lig hedefi/saha ekle → sakatlık sabit formül → TM'siz çalışma ve oranlı kupon denemeleri → kupon/bahis/kombine defterde ayrı sütun → milli maçlar elle (seçenek 1).

## 12) Bekleyen işler / fikirler
1. **Zamanlanmış görevleri yeni oturuma yeniden kur** (bölüm 0).
2. **Milli maç revizesi** (12-13 Kasım sonuçları gelince) ve sonuç kaydı; JPEG'i yenile.
3. 14-17 Kasım sonrası: milli aradan dönen liglerin ilk haftasında yeni liste gelecek (kullanıcı maç listesini verir).
4. 50 maçlık ek liste (beklemede, muhtemelen artık günlük listelerle karşılandı; kullanıcıya sor).
5. Ücretli kaynak kararı (FootyStats / API-Football): 100+ geçerli maç (şu an 47) birikince, hangi bilginin eksik olduğuna göre.
6. Fikirler (onay yok, yapılmadı): mevkiye göre sakatlık testi (geçmiş veri), zirve maçı motivasyonu, hoca değişikliği etkisi testi, favori hafife alma düzeltmesi (model güçlü takımlara küçük ek), rapordaki eşit olasılık sayım hatasını düzeltmek, `milli_pack`'e mevki desteği, 5'li çifte şans kuponunu defterde kaydetmek, Milan gibi eksik Avrupa kapsamını (`EU_COMPS` kimlikleri) genişletmek.
7. Kullanıcının bildirdiği Göztepe/Napoli gibi sonuçlar CSV ile doğrulandı (12 Kasım); yeni bildirim gelirse NOTLAR'a "kullanıcının bildirdiği sonuçlar" altına yaz.
