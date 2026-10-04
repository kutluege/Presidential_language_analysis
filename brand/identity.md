# Marka kimliği (v1.0)

## Karakter

Avatar, Ege'nin çizgi film tarzında stilize edilmiş hali: "yapay zeka filozofu".
Dosyalar `brand/avatar/` altında. Avatar ASLA baştan çizilmez veya yeniden üretilmez;
yalnızca bu SVG dosyaları kullanılır.

| Dosya | Ne zaman |
|---|---|
| `avatar-sade.svg` | Varsayılan. Videonun büyük kısmı. |
| `avatar-defne.svg` | Sadece önemli anlarda (aşağıya bak). Defne tacı + toga. |

### Defne tacı ne zaman gelir?

Defne tacı "bu önemli" sinyalidir. Seyrek kalırsa anlamlıdır.
- Hook'taki ana iddia (ilk 3 saniye içinde olabilir)
- Videonun tezi / ana fikri söylendiğinde
- Kritik veri veya şaşırtıcı bulgu
- Kapanıştaki punchline
- Bir videoda en fazla 3 kez, toplam sürenin en fazla %20'si

Geçiş: sade → defne geçişi bir "taçlanma" anıdır (bkz. `motion.md`, `tac` preset'i).

### Avatarın sabitleri (değiştirilemez)

- Yarım daire gözler: üstü düz kapak çizgisi, altı yay; iris `vurgu` renginde ve kapaktan sarkan yarım disk
- Ağır kapaklı, deadpan bakış; hafif sinsi gülümseme (sağ köşe yukarı)
- Kalın, düz, koyu kaşlar
- Kısa, üstü dikenli, yanları traşlı saç (koyu erik, mor konturlu)
- Noktalı doku ile kirli sakal
- Açılı, keskin geometri; düz renk blokları; koyu kontur
- Işık sol-üstten, magenta kenar ışığı sağdan

### Yasaklar

- Avatarı yeniden çizmek, "iyileştirmek" veya üretken modelle yeniden üretmek
- 3D, gradyanlı ten, parlama, gerçekçi doku
- Gözlere yuvarlak göz bebeği veya beyaz parıltı eklemek
- Dudak senkronu / konuşan ağız (avatar anlatıcıyken bile)
- Gülen, ağzı açık, abartılı ifadeler
- Avatarı yatay olarak aynalamak (ışık yönü bozulur)
- Paletin dışında renk

### Avatar animasyonu (izin verilenler)

SVG'deki katman id'leri: `body`, `toga`, `head`, `beard`, `hair`, `wreath`, `brows`,
`eyes`, `irises`, `eyelids`, `nose`, `mouth`, `rimlight`.
- Göz kırpma: `eyes` grubunu kapak çizgisi (y=166) etrafında scaleY 1 → 0.1 → 1, 120 ms
- Bakış kayması: `irises` en fazla ±4 px yatay
- Kaş kaldırma: `brows` en fazla -6 px dikey (şüphe, "ciddi misin?")
- Vurgu sallanması: tüm avatar en fazla ±2° döner veya 4 px zıplar, cümle vurgusunda
- Giriş/çıkış: alttan kayarak, `motion.md` preset'leriyle
Bunların dışında yüz parçası hareket ettirilmez.

## Anlatıcı modları

Anlatıcı konuya göre değişir. Her sahne şu modlardan birine atanır:

| Mod | Ne görünür | Ne zaman |
|---|---|---|
| `YUZ` | Ege'nin kamera görüntüsü, altyazı | Kişisel deneyim, görüş, hikaye, hook (video kaydı varsa) |
| `YUZ+GRAFIK` | Ege'nin görüntüsü küçük kutuda veya üst/alt bölünmüş, yanında grafik | Bir şeyi gösterirken anlatma, demo, veri açıklaması |
| `AVATAR` | Avatar + motion grafik, Ege'nin sesi | Kavram anlatımı, veri hikayesi, geçişler; ham kayıt sadece ses ise tüm video |

Kurallar:
- Ham kayıt yalnızca ses ise tüm video `AVATAR` modundadır.
- Aynı mod 12 saniyeden uzun sürmez; mod değişimi ritmi taşır.
- Ege'nin yüzü ile avatar aynı karede yan yana görünmez (iki "karakter" çatışır).

## Ton ve metin

- Ekran dili Türkçe; kısa cümle, Ege'nin ağzından.
- Sakin, net, deadpan mizah. Ünlem ve büyük harfle bağırma yok.
- Türkçe büyük harf kuralı: i → İ, ı → I. İngilizce alıntılar büyük harfe çevrilmez (İ tuzağı).
- Ondalık ayırıcı virgül (12,5); binlik ayırıcı nokta (1.250).
- Teknik terim gerekiyorsa bir kez açıklanır.

## Tez

"Yapay zeka çağında herkesin içeriği ortalamaya yakınsıyor; hikaye ('ne' değil 'neden') fark yaratır."
Videolar mümkün olduğunda bu tezle bağ kurar, ama her videoda söylenmez.
