# Bölüm araştırması: başkan konuşmaları analizi (2026-10-04)

Durum: **senaryo v2 + görsel plan taslağı. Sahne/render üretilmedi, onay bekliyor.**

| dosya | ne |
|---|---|
| `senaryo.md` | Seslendirme metni (S01–S17), ★ anları, ~75 sn kesimi, cümle başına kaynak tablosu |
| `gorsel_plan.md` | Yerleşim sistemi, cümle cümle plan, animasyon kartları (B0–B5), SFX |
| `data/animation_data.json` | Sahne başına temiz veri (B1…B5), marka formatında gösterim dizgileri (`*_tr`) |
| `data/temalar.csv` | 5 lider × 8 tema: değer, sıra, ilk-1 / ilk-3 bootstrap payı |
| `data/radar_kartlar.csv` | 5 lider × 7 retorik ölçü: değer, kart puanı (×100), sıra, %95 aralık, 1.'lik payı |
| `data/duygu.csv` | 5 lider × 4 duygu ölçüsü: değer, sıra, aralık, 1.'lik payı, derlem ortalaması |
| `data/stil_ciftler.csv` | 10 çift: üslup kosinüsü ve içerik kosinüsü, sıraları |
| `data/dagilim.csv`, `data/dagilim_konusma.csv` | Lider ve konuşma düzeyinde merkeze uzaklık |
| `build_data.py` | Sayıları alt tablolardan yeniden hesaplar, repodaki değerlerle karşılaştırır, `data/` dosyalarını üretir |
| `verification_log.txt` | Son çalıştırma: 202 kontrol `[OK ]` |
| `arsiv/v1_dil_hikayesi/` | İlk taslak ("model önce dili görüyormuş"); kendi verisi ve doğrulamasıyla |

Marka kuralları: `brand/` (kullanıcının gönderdiği dosyalar, değiştirilmeden).

## Hikaye (v2, kullanıcı yönlendirmesiyle)

Giriş (senin metnin) → derlem (20 konuşma) → beş grafik → "kimin iyi kimin kötü olduğunu söylemez" →
"yapay zeka devlet yönetebilir mi bilmiyorum, ama liderleri denetleyebiliriz" → GitHub.

Beş grafikten çıkan ve senaryoya giren bulgular:
1. **Temalar:** Macron'da gelecek/reform açık ara önde (her bootstrap örneğinde 1.). Erdoğan'da
   "hukuk ve kurumlar" önde görünüyor, ama bunu tek bir sempozyum konuşması taşıyor (0,91; yılbaşı
   mesajları 0,42–0,60). Bunu söylemek hem dürüst hem "bunu bilmiyordum" anı.
2. **FIFA kartları:** Radar → kart. Putin teşekkür 70, vaat 31 (en sağlam iki ölçüm). Erdoğan'ın kartı en dar aralıklı (12 puan).
3. **Duygu:** Hepsi olumlu ağırlıklı. Korku ve düşmanlıkta en yüksek set bile %6'nın altında.
4. **Üslup:** Konuda en benzeşen Macron–Merkel (0,850), üslupta benzemiyor (−0,20). İçerik ile üslup ilişkisi 0,21.
5. **Dağılım:** Macron'un konuşmaları en toplu. Erdoğan'ın setini yine sempozyum konuşması dağıtıyor (onsuz 0,031).

1 ve 5 aynı kaynağa çıkıyor: Erdoğan setindeki tek yılbaşı-dışı konuşma. Videonun içinde küçük bir
geri çağırma ("yine o tek konuşma yüzünden") olarak kullanıldı.

## Doğrulama

Embedding dosyaları (`*.npy`) repoda yok (git-ignore); bu ortamda GPU da yok, yani metinler yeniden
gömülmedi. Her lider düzeyindeki sayı, pipeline'ın kaydettiği bir alt seviyeden bağımsız olarak
yeniden hesaplandı:

- Tema ve retorik: lider = konuşma yüzdeliklerinin ortalaması (40 + 35 kontrol).
- Duygu: konuşma = parçaların ortalaması, lider = konuşmaların ortalaması (80 + 20 kontrol).
- Üslup: 11 ölçü 20 konuşmada z-skoru, lider ortalaması, kosinüs (10 kontrol). İçerik: konuşma kosinüs matrisinden lider merkez kosinüsü (10 kontrol). Spearman 0,21 tuttu.
- Dağılım: konuşma → lider merkezi uzaklığı konuşma kosinüs matrisinden (5 kontrol).
- **Yeniden hesaplanamayanlar** (olduğu gibi okundu): bootstrap payları ve aralıkları, parça → konuşma uzaklığı.

Çalıştırmak için: `pip install pandas numpy`, sonra `python episodes/2026-10-04-baskan-analizi/research/build_data.py`.

## Dikkat / emin olmadığım noktalar

1. **"5 yıllık tüm ulusa sesleniş konuşmaları" diyemedim.** Derlem 20 konuşma, lider başına 3–5.
   16'sı yılbaşı mesajı. Erdoğan'ın birisi sempozyum konuşması, Trump'ınkiler veda, yemin ve 323
   kelimelik bir alıntı derlemesi (Trump'ın yılbaşı mesajı yok). Yıllar da farklı: Merkel 2016–2019,
   Erdoğan / Macron / Putin 2022–2025. Senaryo bu yüzden "çoğu yılbaşı mesajı olan yirmi konuşma" diyor.
2. **Trump'ın "en sık duygusu minnettarlık" sonucunu bilerek kullanmadım.** Bunu 323 kelimelik alıntı
   derlemesi taşıyor (minnettarlık 0,54). Veda ve yemin konuşmalarında 0,14 ve 0,17, ve orada ilk sırada
   değil. Aynı derleme Trump'ın olumlu duygu değerini de yukarı çekiyor; bu yüzden S11'de Trump için
   yalnızca korku/düşmanlık söyleniyor (o skorları gerçek konuşmalar taşıyor).
3. **Çeviri seslendirmede yok** (isteğin üzerine). Ama Erdoğan, Macron ve Merkel metinleri İngilizce
   çeviri, Putin resmi İngilizce metin. Retorik, duygu ve üslup ölçümleri çevirmenin tercihlerini de
   taşıyor. Bunu S04'te ekranda bir dipnot olarak bıraktım; kaldırmanı önermem.
4. **Sıralamaların çoğunda güven aralıkları örtüşüyor.** Senaryoya yalnızca görece sağlam olanları
   koydum: Putin teşekkür %99,95, Macron gelecek/reform teması %100, Trump biz–onlar %81. Macron'un
   "gelecek 57" değeri ise kıl payı (1.'lik payı %45, Putin 55). S09'da yalnızca sayıyı söylüyor, "en yüksek" demiyor.
5. **Futbol benzetmesi** her lidere eşit dozda değil: espri yalnızca Putin kartında ("pası herkese
   veriyor, gol sözü vermiyor"), çünkü en sağlam ölçüm orada. Diğer kartlar sadece sayı. Kartlarda
   genel puan ve mevki bilerek yok (kalite notu ve "sağ/sol kanat" çağrışımı).
6. **"Gül" notu:** Marka avatarın gülmesini yasaklıyor. Gülme yalnızca seste. Avatar o anda kaş kaldırıp göz kırpıyor (deadpan).
7. **"Liderleri denetleyebiliriz"** senin cümlen, olduğu gibi duruyor. Tüm liderlere eşit uygulanan
   genel bir ifade olduğu için tarafsızlık açısından sorun görmüyorum. Daha yumuşak bir alternatif:
   "liderlerin söylediklerini denetleyebiliriz".
8. **Süre ~88–90 sn.** Marka sınırının (90 sn) hemen altında, ilk brifteki 75 sn'nin üstünde.
   `senaryo.md` içinde ~75 sn'lik kesim var.
9. **Marka gerilimleri** (v1'den devam): tek modlu videoda ritim yerleşim değişimiyle taşınıyor; `alt-orta`'da
   gövde kürsü paneline oturuyor. S08 ve S13'te taç köşedeki küçük avatarda kalıyor.
