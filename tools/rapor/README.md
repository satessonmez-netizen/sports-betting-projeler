# tools/rapor: PDF/JPEG rapor betikleri (8-12 Kasım 2026'da anlık yazıldı)

Bunlar sohbet sırasında kullanıcıya PDF/JPEG vermek için yazılmış tek seferlik betiklerdir. Genel amaçlı değiller:
tarihler, takım listeleri ve oranlar içlerine gömülü. Yeni hafta için kopyalayıp düzenle. **Repo kökünden çalıştır.**

| Betik | Ne üretir | Girdi |
|---|---|---|
| `mkpdf2.py` | 28 maçın tercih tablosu (kupon_tercihleri PDF). `C` sözlüğü (lig, tercih, oran, kupon) ve takım adı eşlemesi diğerleri tarafından `exec` ile yeniden kullanılır | `predictions/picks_2026-11-08_noTM.csv` |
| `mkpdf3.py` | Varsayımsal 5 tekli bahis PDF'i | elle yazılı 5 maç |
| `mkpdf4.py`, `mkpdf5.py` | 28 maç + 5'li çifte şans kuponu PDF'i (`mkpdf5` olasılık ve skor sütunları ekli) | picks_..._noTM.csv |
| `karsilastir.py` | Tahmin vs gerçekleşen (canlı/biten durumlu) | `/tmp/d_2026-11-08.json` |
| `iki_gun.py` | 7-8 Kasım iki günlük tahmin-sonuç tablosu | ledger.csv + `/tmp/d_<tarih>.json` |
| `tercih_sonuc.py` | Tercih vs resmi sonuç, 1 birimlik kâğıt üstü kâr/zarar | ledger.csv (resmi skor) + ESPN json |
| `kupon.py`, `kupon2.py` | Oranlı listeden bahisçi payı, EV ve en iyi 5'li kupon araması | oranlar elle girilmiş |
| `pdf.js` | HTML -> PDF (Playwright, Node) | `node tools/rapor/pdf.js girdi.html cikti.pdf` |
| `shot.js` | HTML (#w kutusu) -> JPEG | `node tools/rapor/shot.js girdi.html cikti.jpg` |

ESPN skorları: `sports-skills football get_daily_schedule --date=2026-11-08 > /tmp/d_2026-11-08.json`
(önce `pip install sports-skills`). Playwright bulut ortamında hazır kurulu (`require('playwright')`), tekrar kurma.
Üretilen çıktılar `reports/` altında. PDF'i gönderdikten sonra gözle kontrol et (Read ile sayfayı aç).
