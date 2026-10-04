# Palet (v1.0)

Kaynak: taş heykel fotoğrafındaki arka plan ve taş tonları, piksel örneklemesiyle ölçüldü.
Vurgu ve kenar ışığı parıltı tonundan türetildi.

## Renkler

| Token | Hex | Rol |
|---|---|---|
| `obsidyen` | `#0F0406` | Ana zemin. Saf siyah değil, kırmızıya yatık. |
| `sarap-siyah` | `#27071B` | Gradyan ara durağı, ceket |
| `erik` | `#3F0F2C` | Gradyan ara durağı, ikincil yüzeyler |
| `parilti` | `#4B113A` | Gradyan çekirdeği (ışık kaynağı) |
| `parlak-tas` | `#E5DBC3` | Ana metin, en açık ton |
| `tas` | `#D9C9B0` | Avatar teni, ikincil metin |
| `kraft` | `#C9B196` | Etiketler, çizgiler, defne yaprakları |
| `golge-tas` | `#B8AE9D` | Gölgeler, pasif veri |
| `derin-golge` | `#635643` | Sadece dekoratif doku. Metin için ASLA (2.8:1). |
| `vurgu` | `#D45A93` | TEK vurgu rengi |
| `kenar-isigi` | `#6B1A52` | Sağ-alttan gelen kenar ışığı |

## Gradyan zemin

```css
background: radial-gradient(ellipse at 100% 88%,
  #4B113A 0%, #3F0F2C 16%, #27071B 38%, #0F0406 72%);
```

Kurallar:
- Parıltı tek kaynaktan, bir köşeden yayılır. Varsayılan köşe sağ-alt.
- Karenin en az %60'ı neredeyse siyah (obsidyen) kalır. Parıltı dekor değil, ışık kaynağıdır.
- Sahne geçişlerinde köşe kayabilir; renk durakları asla değişmez.
- Bu ton mor DEĞİL, şarap-erik magentası. Saf mor (#5B2A86 vb.) yasak.

## Vurgu kuralı

`vurgu` yalnızca şunlarda kullanılır:
- Avatarın irisleri
- Sahnenin en önemli tek kelimesi veya tek veri noktası
- Altyazıda vurgulanan kelime

Bir karede birden fazla vurgulu öğe olmaz.

## Kontrast (obsidyen üzerinde)

parlak-tas 14.7:1 · tas 12.4:1 · kraft 9.8:1 · golge-tas 9.2:1 · vurgu 5.5:1 · derin-golge 2.8:1
