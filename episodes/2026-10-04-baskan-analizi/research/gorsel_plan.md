# Görsel plan — cümle cümle

Kurallar `brand/identity.md`, `brand/motion.md`, `brand/palette.md` dosyalarından alındı.
Bu bir plan; sahne veya render üretilmedi.

**Genel**
- 1080×1920, 30 fps. Tüm video `AVATAR` modunda (kayıt yalnızca ses). Ritim, mod yerine
  **yerleşim değişimiyle** taşınıyor: aynı yerleşim 12 sn'yi geçmiyor.
- Zemin: marka gradyanı (parıltı sağ-altta). Grafik sahnelerinde köşe kaymıyor; ★ anlarında
  `tac` preset'inin %15 parlaması dışında gradyan sabit.
- Lider fotoğrafı yok. Liderler yalnızca **isim yazısı** (Inter/Manrope 600, `parlak-tas`).
  Repodaki lider renkleri (mavi/turuncu/…) **kullanılmıyor**: marka tek vurgu rengine izin
  veriyor ve renk-lider eşlemesi tarafsızlık için de gereksiz.
- Veri: `kraft` = etiket/çizgi, `golge-tas` = pasif veri, `parlak-tas` = ana metin/sayı,
  `vurgu` (#D45A93) = karedeki **tek** önemli öğe. `derin-golge` metinde hiç kullanılmıyor.
- Sayılar JetBrains Mono 400/600, ondalık virgül (0,744), yüzde işareti önde (%59,8).
- Altyazı: 64–72 px, `parlak-tas`, satırda en çok 4–5 kelime. Grafikte vurgulu öğe olan
  karelerde altyazıda vurgulu kelime **yok** (karede tek vurgu kuralı). Avatar irisleri bu
  sayıma dahil edilmedi (marka metninde irisler ayrıca sayılıyor).

## Yerleşimler (güvenli alan: üst 220, alt 380, sağ 160 px boş → içerik kutusu x 0–920, y 220–1540)

| kod | avatar | grafik alanı | altyazı |
|---|---|---|---|
| **A** `alt-orta` | `avatar-sade` veya `-defne`, 2,5× (775×1000), x=152, y=520 → yüz y≈670–1245. Gövde altı (y=1520) `sarap-siyah` kürsü paneline oturur (panel y 1520–1920, tam genişlik) | başın üstü, y 240–500 (tek satır / tek sayı) | y 1290–1500, ceketin üstünde. Defne karelerinde açık renkli toga altyazının arkasına girer → altyazıya `sarap-siyah` %85 plaka |
| **B** `grafik + kose` | 0,9× (279×360), x=620, y=880; altyazı paneline oturur. Yüz y≈934–1141 | x 60–900, y 240–860 tam genişlik; y 860–1240 arasında yalnızca x 60–600 | `sarap-siyah` panel y 1240–1520; metin y 1300–1480 |
| **C** `alt-sol` | 1,6× (496×640), x=20, y=880 → yüz y≈976–1344; gövde y=1520'de kürsü paneline oturur | x 540–900, y 240–1200 | y 260–420 (grafiğin üstü, sol hizalı) |

Avatar hiçbir zaman aynalanmıyor; yalnızca izinli hareketler: göz kırpma (`eyes` scaleY
1→0,1→1, 120 ms), bakış kayması (`irises` ±4 px), kaş kaldırma (`brows` −6 px), vurgu
sallanması (±2° / 4 px), `avatar-giris`, `tac`, `tac-cikis`.

## Cümle cümle

Zamanlar tahmini (saniyede 6 hece); seslendirmeden sonra kayıttaki gerçek sürelere göre kaydırılır.

| # | zaman (sn) | metin (kısa) | yerleşim / avatar | grafik / animasyon | ekrandaki metin | karedeki tek vurgu | veri |
|---|---|---|---|---|---|---|---|
| S01 | 0,0–5,8 | "…kim kime en çok benziyor?" | **A**, sade. `avatar-giris` (500 ms) ilk karede. "sordum" kelimesinde `irises` +4 px (soruya bakış) | Başın üstünde beş isim tek satır, `kayis` ile sırayla (80 ms arayla), `golge-tas` | Üstte: "Kim kime en çok benziyor?" (`parlak-tas`) | altyazıda "benziyor" | `leaders` |
| S02 | 6,0–12,4 | "Cevap: Putin ile Trump… %89'unda yine onlar." | **B**, sade | **A1 · Sıralama (Tur 1).** 10 satırlık sıralı liste `kayis` ile (satır başı 60 ms). "Putin ile Trump" kelimesinde 1. satır `vurgu` preset'i. Ardından satırın altında küçük mono etiket "2000 tekrarın %88,7'si" `sayac` ile | Başlık: "Benzerlik sırası" · altta küçük `kraft`: "model: Qwen3-Embedding-8B" | 1. satır: Putin–Trump 0,744 | `A1_siralama_tur1` |
| S03 | 12,7–14,6 | "Sonra bir şey dikkatimi çekti." | **A**, sade. Kaş kaldırma −6 px ("ciddi misin?"), sonra göz kırpma | Liste kayboluyor (opaklık, 300 ms). Grafik yok | — | yok (sessiz kare) | — |
| S04 | 14,9–22,0 | "Erdoğan Türkçe, Macron Fransızca…" | **B**, sade | **A2 · Dil rozetleri.** Beş isim kartı dikey dizilim (x 60–600). Her dil söylendiğinde o kartın yanında rozet `kayis` ile: TR, FR, DE, EN, EN. Rozet: `kraft` kontur, mono 600 | — | yok (rozetler hep `kraft`; vurgu S05'e saklanıyor) | `A2_dil_rozetleri` |
| S05 ★ | 22,3–25,8 | "Yani o ikisi, setteki tek İngilizce metinlerdi." | **A**, `tac` (700 ms) cümle başında → defne. Cümle sonunda `tac-cikis` (400 ms) | A2'nin küçültülmüş hali başın üstüne çıkar (tek satır: TR FR DE EN EN). Putin ve Trump'ın iki EN rozetini saran **tek köşeli parantez** çizilir | Parantez altında: "tek İngilizce metinler" | parantez (rozetler değil; tek öğe) | `A2_dil_rozetleri` |
| S06 | 26,1–30,0 | "Ben de hepsini İngilizceye çevirip…" | **B**, sade | `kesit` (66 ms `parilti` flaşı) → **A3 · Çeviri.** Rozetler TR→EN, FR→EN, DE→EN dönerek (scaleX 1→0→1, 300 ms, 100 ms arayla) değişir; Putin/Trump rozetleri yerinde kalır | Üst köşede küçük etiket: "Tur 2 · hepsi İngilizce · aynı model" | altyazıda "aynı modelle" | `A2_dil_rozetleri` (`flips_in_A3`) |
| S07 ★ | 30,3–34,1 | "Putin–Trump birincilikten onunculuğa…" | **B**, `tac` → defne (kose ölçeğinde). Sonda `tac-cikis` | **A4 · Eğim grafiği (sıra).** İki sütun: "Orijinal dil" / "Hepsi İngilizce", 1–10 sıra. Dokuz çizgi `golge-tas` 1,5 px, Putin–Trump çizgisi 1. sıradan 10. sıraya 800 ms'de iner. Değer değil sıra gösteriliyor (eksen kırpma yok) | Sütun başlıkları `kraft` | Putin–Trump çizgisi | `A4_egim_sira` |
| S08 | 34,4–37,9 | "…onların puanı kıpırdamadı bile." | **A**, sade. Cümle sonunda yalnızca göz kırpma (deadpan) | Başın üstünde büyük mono sayı **0,744**; `sayac` gibi saymaya başlar ama yalnızca son hane 4→3 olur (300 ms). Altında küçük `kraft`: "Putin–Trump · Tur 1 → Tur 2" | 0,744 → 0,743 | son hane "3" | `A5_kipirdamadi.putin_trump` |
| S09 | 38,2–42,7 | "Değişen diğerleriydi…" | **B**, sade | **A5 · Artışlar.** Diğer 9 çift alt alta, her birinin yanında yukarı ok + mono fark (+0,276 … +0,083), `kayis` 60 ms arayla, `parlak-tas`. Putin–Trump en altta `golge-tas` "±0,000" | — | altyazıda "yaklaştı" | `A5_kipirdamadi.others` |
| S10 | 43,0–51,6 | "…en yakın on komşusuna baktım…" | **C**, sade. "altısı"nda vurgu sallanması (4 px) | **A6 · Komşular** (`dagilim` preset). Ortada tek nokta = bir Erdoğan paragrafı; etrafına 10 komşu nokta saçılır. Önce 10'u dolu (`parlak-tas` = Erdoğan), etiket **%99,5**. Kesmeden geçişle 4 nokta içi boş `golge-tas` konturlu olur (başka liderler), etiket `sayac` ile **%59,8** | Etiket: "Erdoğan'ın 10 en yakın komşusu" · "Tur 1 → Tur 2" | merkez nokta | `A6_komsular` |
| S11 ★ | 51,9–55,2 | "Yani model önce dili görüyormuş, anlamı sonra." | **A**, `tac` → defne, cümle sonunda `tac-cikis` | Grafik yok. Başın üstünde iki satır: "önce dil" / "sonra anlam", `kayis` | "önce dil · sonra anlam" | "dil" kelimesi | — |
| S12 | 55,5–60,4 | "Daha büyük ikinci bir modelle…" | **B**, sade | **A8 · İkinci model.** A1 ile aynı liste tasarımı, bu kez İngilizce metin + KaLM-Embedding-Gemma3-12B. Liste alttan dolar; son satır Putin–Trump 0,701 | Başlık: "Model 2 · 12 milyar parametre" | 10. satır | `A8_ikinci_model` |
| S13 | 60,7–68,2 | "Bu, liderler hakkında bir şey kanıtlamıyor…" | **A**, sade. Hareketsiz, yalnızca bir göz kırpma | Başın üstünde düz metin kartı (`kraft` ince kontur): "20 konuşma · metin ölçümü" / "3'ü çeviri, 1'i resmi çeviri seti" | — | yok (bilerek sakin kare) | `corpus` |
| S14 | 68,5–69,6 | "Kod GitHub'ımda." | **A**, sade, avatar 4 px zıplama | Başın üstünde mono: `github.com/kutluege/Presidential_language_analysis` (satırı iki satıra böl: `github.com/kutluege/` · `Presidential_language_analysis`) | — | yok | — |

### Defne bütçesi
S05 (3,5 sn) + S07 (3,8 sn) + S11 (3,3 sn) = **10,6 sn / ~70 sn ≈ %15** (sınır %20, en çok 3 kez).

### Yerleşim ritmi
A (0–5,8) → B (6–12,4) → A (12,7–14,6) → B (14,9–22) → A (22,3–25,8) → B (26,1–34,1) →
A (34,4–37,9) → B (38,2–42,7) → C (43–51,6) → A (51,9–55,2) → B (55,5–60,4) → A (60,7–69,6).
En uzun tek yerleşim: S13–S14'teki A, ~9 sn. Hepsi 12 sn'nin altında.

## Animasyon kartları (veri → görsel)

Repodaki grafikler kullanılmıyor; her biri `data/animation_data.json` içindeki anahtardan
yeniden kuruluyor.

**A1 · Sıralama (Tur 1)** — `A1_siralama_tur1.rows`
10 satır, satır yüksekliği ~58 px, y 300–880. Sol: sıra no (mono `golge-tas`), orta: çift adı
(`parlak-tas`), sağ: değer (`sim_tr`, mono). Çubuk yok: değerler 0,581–0,744 aralığında,
çubuk sıfırdan başlarsa farklar görünmez, kırpılırsa yanıltır. Dil etiketleri (`lang`) bu
sahnede **gösterilmiyor**; ipucu S05'e saklanıyor.

**A2/A3 · Dil rozetleri** — `A2_dil_rozetleri`
Beş kart; rozet 96×56 px, `kraft` 2 px kontur, mono 600. A3'te `flips_in_A3 = true` olan üç
rozet dönüyor. S05'te tek satıra küçülüp başın üstüne taşınıyor.

**A4 · Eğim grafiği** — `A4_egim_sira`
Sol sütun `rank_run1`, sağ sütun `rank_run2`; iki sütun arası ~520 px. Çift adları her iki
uçta küçük (`kraft`, 28 px). Sadece `highlight: true` olan çizgi `vurgu`. Değer yok, sadece sıra.

**A5 · Kıpırdamadı + artışlar** — `A5_kipirdamadi`
S08: tek büyük sayı (mono 600, ~180 px). S09: `others` dizisi `delta` sırasına göre; ok uzunluğu
farkla orantılı olabilir (0,083 → 0,276), ama sayılar her zaman yazılı.

**A6 · Komşular** — `A6_komsular`
`dagilim` preset'i (1200 ms). Nokta sayıları (`filled_dots_run1` = 10, `filled_dots_run2` = 6)
**ortalamanın yuvarlanmış hali**; kesin değer etikette (`share_run1_tr`, `share_run2_tr`).
Diğer liderler renklendirilmiyor (tek vurgu kuralı); yalnızca "Erdoğan / diğer" ayrımı var.

**A8 · İkinci model** — `A8_ikinci_model.rows`
A1 ile aynı bileşen; yalnızca veri ve başlık farklı. İzleyici "aynı liste, farklı sonuç"u
göz ucuyla karşılaştırabilsin diye tasarım bilerek tekrar ediliyor.

## Ses / SFX
- `vurgu` → yumuşak tık: S02 (1. satır), S07 (çizgi inişi bitince), S10 (%59,8 oturunca).
- `tac` → hafif metalik çınlama: S05, S07, S11.
- `kesit` → kısa whoosh: S06.
- Müzik konuşmanın en az 18 dB altında; S03 ve S08'deki eslerde müzik de kısılabilir (deadpan).
