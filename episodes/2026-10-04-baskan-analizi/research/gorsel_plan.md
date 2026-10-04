# Görsel plan v2 — cümle cümle

Kurallar `brand/identity.md`, `brand/motion.md`, `brand/palette.md` dosyalarından. Bu bir plan; sahne veya render üretilmedi.

**Genel**
- 1080×1920, 30 fps. Tüm video `AVATAR` modunda (kayıt yalnızca ses). Ritim yerleşim değişimiyle
  taşınıyor; hiçbir yerleşim 12 sn'yi aşmıyor (aşağıdaki tablo).
- Zemin: marka gradyanı, parıltı sağ-altta. Repodaki grafikler kullanılmıyor; hepsi
  `data/animation_data.json` içinden yeniden kuruluyor.
- **Lider fotoğrafı yok.** Liderler yalnızca isim yazısı (Inter/Manrope 600, `parlak-tas`).
  Repodaki lider renkleri kullanılmıyor: marka tek vurgu rengine izin veriyor. Ayırt etmek için
  isim etiketi ve konum yeterli.
- Renk rolleri: `parlak-tas` ana metin ve sayılar · `kraft` etiket, çizgi, kart kenarı ·
  `golge-tas` pasif veri · `erik` / `sarap-siyah` kart ve panel zemini · `vurgu` (#D45A93) karedeki
  **tek** önemli öğe. `derin-golge` metinde hiç kullanılmıyor.
- Sayılar JetBrains Mono 400/600, ondalık virgül (0,42), yüzde işareti önde (%5,5).
- Altyazı 64–72 px, satırda en çok 4–5 kelime. Grafikte vurgulu öğe varken altyazıda vurgulu kelime yok.
  Avatar irisleri bu sayıma dahil edilmedi.
- Teknik terimler bir kez, ekranda küçük `kraft` dipnotla açıklanıyor (marka kuralı: "bir kez açıklanır").

## Yerleşimler (güvenli alan: üst 220, alt 380, sağ 160 → içerik x 0–920, y 220–1540)

| kod | avatar | grafik alanı | altyazı |
|---|---|---|---|
| **A** `alt-orta` | 2,5× (775×1000), x=152, y=520 → yüz y≈670–1245; gövde y=1520'de `sarap-siyah` kürsü paneline oturur | başın üstü, y 240–500 | y 1290–1500, ceketin üstünde; defne karelerinde altyazıya `sarap-siyah` %85 plaka |
| **B** `grafik + kose` | 0,9× (279×360), x=620, y=880 → yüz y≈934–1141; altyazı paneline oturur | x 60–900, y 240–860; y 860–1240 arasında yalnızca x 60–600 | `sarap-siyah` panel y 1240–1520 |
| **C** `alt-sol` | 1,6× (496×640), x=20, y=880 → yüz y≈976–1344; kürsü paneline oturur | x 540–900, y 240–1200 | y 260–420, sol hizalı |

İzinli avatar hareketleri: göz kırpma, iris ±4 px, kaş −6 px, ±2° / 4 px vurgu sallanması,
`avatar-giris`, `tac`, `tac-cikis`. Gülme, açık ağız, dudak senkronu yok (marka yasağı).

## Cümle cümle

Zamanlar tahmini; kayıttan sonra gerçek sürelere göre kaydırılır.

| # | zaman (sn) | metin (kısa) | yerleşim / avatar | grafik / animasyon | tek vurgu | veri |
|---|---|---|---|---|---|---|
| S01 | 0,0–4,7 | "…biliyor muydunuz?" | **A**, sade, `avatar-giris`. Soru sonunda iris +4 px (kameraya yan bakış) | Başın üstünde tek satır: "Siyasi söylem × yapay zeka" `kayis` | altyazıda "yapay zekayla" | — |
| S02 | 5,0–10,2 | "…devletleri yöneteceğini konuşanlar bile var." | **C**, sade | Sağ sütunda kelimeler alt alta `kayis` ile (120 ms arayla), `golge-tas`: "kod" · "metin" · "görsel" · "müzik" · en son **"devlet?"** | "devlet?" | — |
| S03 | 10,5–15,7 | "…yerine değil, yanında…" | **A**, sade. "yerine değil" sözünde kaş −6 px, "yanında"da geri | Başın üstünde: "yerine değil · yanında" | "yanında" | — |
| S04 | 16,0–21,5 | "…yirmi konuşmasını…okuttum." | **C**, sade | **B0 · Derlem.** 20 nokta, beş sütun (isim altta): 5-4-4-4-3. Dolu nokta = yılbaşı mesajı (16), içi boş = diğer (4). Noktalar `sayac` gibi tek tek yanar. Dipnot (`kraft`, 28 px): "Erdoğan, Macron, Merkel: İngilizce çeviri · Putin: resmi İngilizce metin" | yok | `corpus` |
| S05 | 21,8–28,4 | "Kim ne konuşuyor? Macron'da…" | **B**, sade | **B1 · Temalar.** Beş satır (Macron, Putin, Trump, Merkel, Erdoğan). Her satır: isim + en yüksek tema etiketi + 0,50 çizgisinden sağa uzanan çubuk + değer. Orta dikey çizgi "ortalama". Söylenen lider satırı `parlak-tas`'a geçer, diğerleri `golge-tas` | söylenen satırın çubuğu (sırayla tek tek) | `B1_temalar.leaders[].top3[0]` |
| S06 | 28,7–33,9 | "Erdoğan'da dış politika… tek bir konuşma taşıyor." | **C**, sade | Sağ sütunda Erdoğan'ın 2 teması: "Dış politika 0,56" ve "Hukuk ve kurumlar 0,58". İkincisinin altında 5 küçük nokta = 5 konuşma (0,42 · 0,60 · 0,54 · 0,44 · **0,91**). 0,91'lik nokta sağa ayrılır, etiketi: "sempozyum konuşması" | 0,91 noktası | `B1_temalar.erdogan_democracy_by_speech` |
| S07 | 34,2–39,6 | "…FIFA oyuncu kartları geldi." [gülme] | **C**, sade. Gülme anında avatar **gülmüyor**: kaş −6 px + göz kırpma (deadpan) | Sağda beş radar poligonu üst üste (`golge-tas` 1,5 px, dolgu yok); "FIFA" kelimesinde poligonlar kart çerçevesine dönüşür (300 ms) | yok | `B2_fifa_kartlari` |
| S08 ★ | 39,9–45,5 | "Putin'in kartı: teşekkür 70, vaat 31…" | **B**, `tac` → defne (kose ölçeğinde); cümle sonunda `tac-cikis` | **B2 · FIFA kartı.** Büyük kart (x 120–600, y 260–1180), `erik` zemin, `kraft` 3 px kenar, üstte isim. 7 istatistik iki sütun mono 600: ÇAT 51 · İŞB 56 · GEÇ 62 · GEL 55 · B-O 50 · TŞK 70 · VAT 31. "teşekkür"de 70 `vurgu` preset, "vaat"te vurgu 31'e geçer. **Genel puan (OVR) yok** | önce 70, sonra 31 (aynı anda tek) | `B2_fifa_kartlari.cards[Putin]` |
| S09 | 45,8–50,6 | "Trump'ta biz-onlar 65, Merkel… Macron…" | **B**, sade | Kart yatay kayarak değişir (her biri ~1,6 sn): Trump (B-O 65), Merkel (İŞB 61), Macron (GEL 57). Her kartta yalnız söylenen istatistik vurgulu | söylenen istatistik | `cards[Trump/Merkel/Macron]` |
| S10 | 50,9–54,5 | "Erdoğan'ın kartı en dengelisi…" | **C**, sade, 4 px zıplama | Sağda Erdoğan kartı: 7 istatistik 41–53. Altında yatay mini şerit: beş kartın min–max aralığı (Erdoğan 12, Macron 19, Merkel 23, Trump 28, Putin 39); Erdoğan'ın şeridi en kısa | Erdoğan şeridi | `cards[].range` |
| S11 | 54,8–62,0 | "Duygu tonu hepsinde olumlu ağırlıklı… yüzde 6'nın altında." | **B**, sade | **B3 · Duygu.** Üst: "duygu değeri" 5 çubuk, sıfırdan sağa (0,42…0,77), hepsi pozitif; Putin 0,77. Alt: "korku" ve "düşmanlık" 0–%100 ölçeğinde 5'er çubuk; hepsi %6 çizgisinin altında kalıyor. Çizgi etiketi "%6". Bıyık çizgileri (güven aralığı) `golge-tas` | önce Putin çubuğu, sonra "%6" çizgisi | `B3_duygu` |
| S12 | 62,2–65,0 | "Üslupta en yakın ikili Erdoğan ile Macron." | **C**, sade | Sağda 10 çiftlik sıralı liste (üslup kosinüsü): 1. Erdoğan–Macron 0,42 … 10. Erdoğan–Putin −0,53. Dipnot: "üslup = 7 retorik ölçü + duygu" | 1. satır | `B4_stil.style_pairs` |
| S13 ★ | 65,2–69,7 | "Asıl ilginci: konuda…Macron ve Merkel, üslupta benzemiyor." | **B**, `tac` → defne; sonda `tac-cikis` | **B4 · Konu × üslup** (`dagilim` preset). 10 nokta = 10 çift; x = konu benzerliği, y = üslup benzerliği. Noktalar gri saçılır; Macron–Merkel noktası en sağda ama orta-altta kalır. Eksen etiketleri: "konu →", "üslup ↑". Köşede küçük: "ilişki: 0,21" | Macron–Merkel noktası | `B4_stil.macron_merkel` + `data/stil_ciftler.csv` |
| S14 | 70,0–75,7 | "Kendi içinde en toplu… Erdoğan'ınki; yine o tek konuşma…" | **B**, sade | **B5 · Takımyıldızlar.** Beş küçük küme yan yana (2 satır). Her kümede merkez nokta + konuşma noktaları; noktanın merkeze uzaklığı = gerçek uzaklık × 800 px. Macron'unkiler neredeyse üst üste; Erdoğan'da dört nokta yakın, sempozyum noktası uzakta | Erdoğan'ın sempozyum noktası | `B5_dagilim`, `data/dagilim_konusma.csv` |
| S15 | 76,0–81,7 | "Bunların hiçbiri kimin iyi, kimin kötü…" | **C**, sade, hareketsiz, bir göz kırpma | Sağda düz metin kartı (`kraft` ince kenar): "20 metin · ölçüm, hüküm değil" | yok (bilerek sakin) | — |
| S16 ★ | 82,0–88,7 | "…bilmiyorum. [es] Ama… liderleri denetleyebiliriz." | **A**. İlk cümle sade + kaş −6 px. Esten sonra `tac` → defne (yalnızca ikinci cümle, ~3,5 sn), sonra `tac-cikis` | Başın üstünde: "devlet yönetir mi? —" sonra "denetleyebiliriz" | "denetleyebiliriz" | — |
| S17 | 88,9–89,9 | "Kod GitHub'ımda." | **A**, sade, 4 px zıplama | Başın üstünde mono, iki satır: `github.com/kutluege/` · `Presidential_language_analysis` | yok | — |

### Defne bütçesi
S08 (5,7 sn) + S13 (4,5 sn) + S16 ikinci cümle (~3,5 sn) = **~13,7 sn / ~90 sn ≈ %15** (sınır %20, en çok 3 kez).
S08 ve S13'te avatar köşede (0,9×) olduğu için taç küçük görünür. Daha görünür olsun istersen
o iki cümlede A yerleşimine geçip grafiği başın üstüne sıkıştırmak gerekir. Ben grafiğin okunmasını öne aldım.

### Yerleşim ritmi
A 0–4,7 · C 5–10,2 · A 10,5–15,7 · C 16–21,5 · B 21,8–28,4 · C 28,7–39,6 · B 39,9–50,6 ·
C 50,9–54,5 · B 54,8–62 · C 62,2–65 · B 65,2–75,7 · C 76–81,7 · A 82–89,9. En uzun blok 10,9 sn.

## Animasyon kartları

**B0 · Derlem** — `corpus`. 20 nokta (Ø 28 px, aralık 44 px). Dolu `parlak-tas` = yılbaşı mesajı, içi boş `kraft`
= diğer (Erdoğan sempozyum, Trump veda / yemin / alıntı derlemesi). Tür adları ekranda yazmıyor; sadece "16 yılbaşı mesajı + 4 diğer".

**B1 · Temalar** — `B1_temalar`. Çubuklar 0,50'den başlar (0,50 = 20 konuşmanın ortalaması; marka dipnotu:
"0,50 = ortalama"). Ölçek 0,40–0,75. Değer etiketleri mono, virgüllü. Tema adları Türkçe (`theme_tr`).

**B2 · FIFA kartları** — `B2_fifa_kartlari.cards`. Kısaltmalar: ÇAT çatışma/tehdit · İŞB iş birliği · GEÇ geçmişe
yönelim · GEL geleceğe yönelim · B-O biz–onlar · TŞK teşekkür/takdir · VAT vaat. Kart altında küçük dipnot: "50 = ortalama".
Kartlarda **mevki, bayrak, fotoğraf, genel puan yok**. Genel puan bir kalite notu gibi okunur, mevki
adları da siyasi çağrışım yapabilir ("sağ/sol kanat").

**B3 · Duygu** — `B3_duygu`. Duygu değeri çubukları ölçek 0–1. Korku ve düşmanlık 0–%100 ölçeğinde gösteriliyor
ki küçüklükleri görünsün. Bu bilerek seçildi, çünkü cümlenin iddiası "çok düşük". Dipnot: "duygu sınıflandırıcısı, olasılık".

**B4 · Konu × üslup** — `data/stil_ciftler.csv` (`content_cosine`, `style_cosine`). x ekseni 0,70–0,86,
y ekseni −0,6–0,5. Noktaların çift adları yok, yalnız Macron–Merkel etiketli (tek vurgu).

**B5 · Takımyıldızlar** — `data/dagilim_konusma.csv`. Konuşma noktaları merkez etrafında eşit açıyla dizilir;
yarıçap = uzaklık × 800 px (0,019 → 15 px, 0,162 → 130 px; küme kutusu ~280 px). Konuşma adları yok.

## Ses / SFX
- `vurgu` → yumuşak tık: S02 ("devlet?"), S08 (31), S13 (Macron–Merkel noktası), S14 (sempozyum noktası).
- `tac` → hafif metalik çınlama: S08, S13, S16.
- S07'deki gülme seslendirmenin kendisi; müzik o anda kısılabilir.
- Müzik konuşmanın en az 18 dB altında.
