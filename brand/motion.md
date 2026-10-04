# Hareket sistemi (v1.0)

## Format

- 1080x1920 (9:16), 30 fps, H.264, AAC 48 kHz
- Ses yüksekliği yaklaşık -14 LUFS (entegre)
- Süre hedefi: 30-90 saniye

## Güvenli alanlar (9:16)

Reels/Shorts arayüzü kenarları kapatır. Değerler yaklaşıktır; platform değişirse güncelle.
- Üst: 220 px boş (önemli içerik yok)
- Alt: 380 px boş (açıklama, butonlar)
- Sağ: 160 px boş (beğeni/yorum ikonları)
- Önemli metin, avatar yüzü ve veri bu alanların içinde kalır.

## Avatar yerleşimi

- Kaynak SVG 310x400. Varsayılan ölçek 2.5x (775x1000 px).
- Gövdenin alt kenarı ya kare dışına taşar (kırpılır) ya da bir panelin üstüne oturur; havada kesik durmaz.
- Yüz (yaklaşık SVG y=60-290 aralığı) alt güvenli alanın üstünde kalır.
- Yerleşimler: `alt-orta` (anlatıcı), `alt-sol` (yanında grafik), `kose` (küçük, 0.9x, tepki için).

## Tipografi

- Başlık / gövde: Türkçe karakter desteği olan bir sans (öneri: Inter veya Manrope)
- Sayılar ve veri: mono (öneri: JetBrains Mono)
- Ağırlıklar: 400 ve 600; başka ağırlık yok
- Altyazı: 64-72 px, `parlak-tas`, satır başına en fazla 4-5 kelime, vurgulu kelime `vurgu`
- Altyazı konumu: ekranın alt üçte birinin üstü (alt güvenli alanın hemen üstü)

## Preset'ler

Süreler sabit. Easing varsayılanı: `cubic-bezier(0.22, 1, 0.36, 1)` (yumuşak çıkış).

| Preset | Ne yapar | Süre |
|---|---|---|
| `sayac` | Rakam 0'dan hedefe sayar, mono font | 900 ms |
| `dagilim` | Gri noktalar saçılır, bir nokta `vurgu` renginde öne çıkar | 1200 ms |
| `vurgu` | Tek kelime/öğe `vurgu` rengine geçer, %4 büyür | 300 ms |
| `kesit` | Sert kesme, 2 karelik beyaz değil `parilti` flaşı | 66 ms |
| `kayis` | Öğe alttan 40 px kayarak, opaklık 0 → 1 | 400 ms |
| `avatar-giris` | Avatar alttan kayarak girer, sonunda 4 px zıplar | 500 ms |
| `tac` | Sade → defne: toga ve defne katmanları yukarıdan inip oturur, gradyan %15 parlar, avatar kaşlarını 6 px kaldırır | 700 ms |
| `tac-cikis` | Defne → sade: toga ve taç opaklıkla kaybolur | 400 ms |

## Ses tasarımı

- Müzik düşük (konuşmanın en az 18 dB altında), tek parça, sakin
- SFX sade: `vurgu` için yumuşak tık, `tac` için hafif metalik çınlama, `kesit` için kısa whoosh
- Her sahne geçişine ses konmaz; sadece vurgu anlarına

## Yasaklar

- Her cümlede zoom
- Neon, glow, blur yoğun efektler
- Parlak beyaz zemin
- Hazır şablon geçişleri (yıldız silme, sayfa çevirme vb.)
