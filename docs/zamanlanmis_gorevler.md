# Zamanlanmış görevler: tam metinler (yeniden kurmak için)

**Neden bu dosya var:** Aşağıdaki görevler, kurulduğu OTURUMA bağlıdır (persistent session). Oturum kapanır/değişirse
görevler o oturumu uyandıramaz. Yeni oturumda:
1. `list_triggers` ile mevcut görevlere bak. Eski oturuma bağlı olanları `delete_trigger` ile sil (çift çalışmasın).
2. Aşağıdaki iki görevi `create_trigger` ile (varsayılan: bu oturuma bağlı) yeniden kur. `initiation: human_request`.
3. Kullanıcıya haber ver.
**Durum (12 Kasım 2026):** iki görev kurulduğu eski oturumda çalıştı (Salı 10 Kasım 08:47, Perşembe 12 Kasım 09:41). Kullanıcı YENİ oturum açıyor: görevler eski oturuma bağlı kalacağı için yeni oturumda silinip yeniden kurulmalı. `docs/DEVIR_TESLIM.md` bölüm 0 adım 3.
Kurulum tarihi: 2026-11-06. Oturum o zaman: `session_013GrRe5XCnSDLBzoVtDLj2c`. Dal: `ccr-53ccebd7-15qd1c`.

## 1) Haftalık tahmin defteri sonuç işleme: Salı 08:47 (İstanbul)
- Ad: `Haftalık tahmin defteri sonuç işleme`
- cron: `CRON_TZ=Europe/Istanbul 47 8 * * 2`  (Salı: Pazartesi akşamı biten maçlar ve CSV gecikmesi için pay)
- İlk bilinen kimlik: `trig_019wZe5FaZmjq7naYgZF19Bg`
- Prompt:
```
Haftalık tahmin defteri işi (kullanıcı onayladı). Sırayla yap: 1) Repo klasöründe `git fetch origin ccr-53ccebd7-15qd1c && git checkout ccr-53ccebd7-15qd1c && git pull origin ccr-53ccebd7-15qd1c`. 2) `cd src && python3 -W ignore refresh_data.py` (güncel CSV ve fikstür). 3) `python3 -W ignore ledger.py settle`, sonra `python3 -W ignore ledger.py report` ve `python3 -W ignore ledger.py errors`. 4) NOTLAR.md içindeki 'Canlı defterden dersler' bölümünü güncelle, ama sadece kaç maça dayandığını yazarak; toplam geçerli sonuçlanmış maç 100'ün altındaysa 'iyi/kötü gidiyoruz' sonucu ÇIKARMA, sadece sayıları aktar. 5) Değişiklikleri (predictions/ledger.csv, reports/, NOTLAR.md, data/) commit'le ve ccr-53ccebd7-15qd1c dalına push et. 6) Kullanıcıya Türkçe, kısa maddelerle özetle: kaç maç sonuçlandı, bekleyen kaç maç var, isabet ve RPS (ben/model/piyasa), en büyük 3 hata ve nedeni. Sonuçlanmamış maç varsa (CSV gecikmesi) bunu açıkça söyle. Yeni tahmin yazma, sadece işle ve raporla.
```

## 2) Perşembe FotMob xG çekimi: Perşembe 09:41 (İstanbul)
- Ad: `Perşembe FotMob xG çekimi`
- cron: `CRON_TZ=Europe/Istanbul 41 9 * * 4`
- İlk bilinen kimlik: `trig_01AB8vPq5Me3KQh2boRNZmME`
- Kapsam: `data/fotmob/leagues.csv` (Süper Lig, Premier Lig, La Liga, Bundesliga, Serie A, Ligue 1, Şampiyonlar Ligi, Avrupa Ligi). Yeni sezonda sezon kimlikleri güncellenmeli.
- Prompt:
```
Haftalık FotMob xG çekimi (kullanıcı onayladı, her Perşembe). Sırayla: 1) `git fetch origin ccr-53ccebd7-15qd1c && git checkout ccr-53ccebd7-15qd1c && git pull origin ccr-53ccebd7-15qd1c`. 2) `cd src && python3 -W ignore fotmob_stats.py` (data/fotmob/leagues.csv içindeki aktif tüm ligler; tarihli anlık görüntü ve history.csv'ye ekleme). 3) Çıktıda ✗ ile başarısız istatistik veya '[uyarı] eşleşmeyen takımlar' varsa not et: eşleşmeyen takımlar için data/fotmob/team_names.csv'ye doğru eşleşmeyi ekle (emin değilsen eklemeden kullanıcıya sor). 4) Değişiklikleri (data/fotmob/) commit'le ve ccr-53ccebd7-15qd1c dalına push et. 5) Kullanıcıya Türkçe, 3-4 kısa madde ile özetle: kaç lig/takım çekildi, hata var mı, ve bu hafta xG'de dikkat çeken 2-3 şey (örn. şans göstergesi en uç takımlar). Sonuçlardan 'iyi/kötü gidiyoruz' çıkarma. Yeni tahmin yazma. Not: FotMob resmi olmayan uç nokta; hata (403/429) alırsan tekrar tekrar deneme, kullanıcıya bildir.
```

## Notlar (kurulumdan sonra öğrenilenler)
- Perşembe çekimi 8 yarışma × ~20 takım için 110 saniyeyi AŞABİLİR (ilk denemede kesildi): arka planda çalıştır (`run_in_background`), bitince `git add data/fotmob` + commit + push. Kesilirse güvenle tekrar çalıştırılabilir (aynı gün tekrarında history çoğalmaz).
- Salı görevi `ledger.py report`'u çalıştırınca `reports/weekly_<tarih>.md` yazılır (ezilir); n<100 iken NOTLAR'a yalnız sayılar yazılır.
- Yeni sezonda FotMob sezon kimlikleri (`data/fotmob/leagues.csv`) güncellenmeli.
- Her iki görev de 'yeni tahmin yazma' der; milli maç tahminleri bu görevlerin kapsamı dışında.
