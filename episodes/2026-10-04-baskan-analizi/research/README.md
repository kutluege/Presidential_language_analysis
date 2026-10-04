# Bölüm araştırması: başkan konuşmaları analizi (2026-10-04)

Durum: **senaryo + görsel plan taslağı. Sahne/render üretilmedi, onay bekliyor.**

| dosya | ne |
|---|---|
| `senaryo.md` | Seslendirme metni (S01–S14), ★ anları, kısaltma seçenekleri, cümle başına kaynak tablosu |
| `gorsel_plan.md` | Yerleşim sistemi, cümle cümle görsel plan, animasyon kartları (A1–A8), SFX |
| `data/animation_data.json` | Sahne başına temiz veri (A1…A8), marka formatında gösterim dizgileri (`*_tr`) |
| `data/pairs_run1_vs_run2.csv` | 10 lider çifti: Tur 1 / Tur 2 benzerlik ve sıra, fark, ikinci model, Tur 1 BGE-M3 |
| `data/knn_same_leader_share.csv` | Lider başına en yakın 10 komşuda aynı lider payı (Tur 1, Tur 2, ikinci model, şans düzeyi) |
| `build_data.py` | Tüm sayıları alt tablolardan yeniden hesaplar, repodaki değerlerle karşılaştırır, `data/` dosyalarını üretir |
| `verification_log.txt` | Son çalıştırmanın çıktısı: her kontrol `[OK ]` |

Marka kuralları: `brand/` (identity, motion, palette, avatar SVG'leri; kullanıcının
gönderdiği dosyalar, değiştirilmeden kopyalandı).

## Seçilen hikaye: "Model önce dili görüyormuş"

1. İlk turda (her lider kendi dilinde) model en benzer çift olarak **Putin–Trump**'ı buldu
   (0,744; 2000 bootstrap örneğinin %88,7'sinde birinci).
2. Bu ikisi setteki **tek İngilizce** metinlerdi.
3. Her şey İngilizceye çevrilip **aynı modelle** yeniden ölçülünce Putin–Trump **1. sıradan 10. sıraya**
   düştü. Kendi puanları neredeyse hiç değişmedi (0,744 → 0,743; metinleri iki turda da birebir
   aynıydı), diğer 9 çiftin hepsi arttı (+0,083 … +0,276).
4. Erdoğan paragraflarının en yakın 10 komşusunda Erdoğan payı %99,5'ten %59,8'e indi.
5. Daha büyük ikinci bir model de İngilizce metinde Putin–Trump'ı en sona koyuyor (0,701).

**Neden bu hikaye:**
- "Bunu bilmiyordum" anı somut: herkesin aklına gelen yorum ("bu ikisi birbirine benziyormuş")
  tersine dönüyor, ve sebep teknik ama tek cümlede anlaşılıyor: model dil görüyordu.
- Kendi kendini doğrulayan bir doğal deney: Putin ve Trump metinleri iki turda da aynı kaldı,
  yani kontrol grubu gibi davranıyorlar. Puanları sabit kalırken sıraları tersine dönüyor.
- Siyasi olarak tarafsız: hikayenin öznesi liderler değil, ölçüm aracı. Kimse övülmüyor ya da
  eleştirilmiyor; ilk "bulgu" zaten çürütülüyor.
- Projenin kendi özeti de bunu "en temiz metodolojik hikaye" olarak işaretliyor
  (`outputs/PROJECT_BRIEF.md` §7).

**Bilerek dışarıda bırakılanlar (ve neden):**
- *Retorik/duygu sıralamaları* (ör. "biz–onlar" ölçeğinde 1. sıra, "teşekkür" ölçeğinde 1. sıra):
  güven aralıklarının çoğu örtüşüyor, çeviri etkisi taşıyor ve "X daha kavgacı" gibi kişiye dair
  okumalara çok açık. Tarafsızlık kuralı için riskli.
- *İçerik ile stil benzerliği ilişkisizdir (Spearman 0,21)*: ilginç ama 10 noktalı bir korelasyon,
  ve 60 sn'ye ikinci bir kavram sokuyor.
- *Tema profilleri*: iki yöntem (embedding ve NLI) parça düzeyinde yalnızca %34 aynı temayı buluyor;
  sağlam değil.
- *Kümeleme, dağılım (dispersion)*: teknik, görsel anlatımı uzun.

## Doğrulama

Embedding dosyaları (`*.npy`) repoda yok (git-ignore), bu ortamda GPU da yok; bu yüzden metinler
yeniden gömülmedi. Bunun yerine her lider düzeyindeki sayı, pipeline'ın kaydettiği bir alt
seviyedeki tablodan bağımsız olarak yeniden hesaplandı:

- Lider merkez benzerliği ← konuşma düzeyi benzerlik matrisi (lider merkezi = birim konuşma
  merkezlerinin normalize ortalaması olduğu için cos(A,B) = Σs_ij / √(Σs_AA·Σs_BB)).
  4 matris × 10 çift, hepsi 1e-4 içinde eşleşti.
- Sıralar, farklar, Spearman (−0,43 ve 0,83) bu yeniden hesaplanmış değerlerden türetildi; eşleşti.
- Komşu payları ← parça başına kNN tablosu; 3 çalışma × 5 lider eşleşti.
- Putin ve Trump parça metinlerinin iki turda birebir aynı olduğu kontrol edildi.

Çalıştırmak için: `pip install pandas numpy`, repo kökünden
`python episodes/2026-10-04-baskan-analizi/research/build_data.py`.

## Emin olmadığım / dikkat edilmesi gerekenler

1. **"Model dil görüyordu" bu model için doğru, genel olarak değil.** İlk turdaki *ikinci* model
   (BGE-M3, çok dilli eşleme için eğitilmiş) orijinal dillerde bile Putin–Trump'ı **10. sıraya**
   koymuştu ve Erdoğan komşu payı orada zaten %47,3'tü. Senaryo bu yüzden "yapay zeka" değil "model"
   diyor. İzleyiciden "her model böyle mi?" sorusu gelebilir; cevabı: hayır, model seçimine bağlı.
   İstersen S11'den sonra kısa bir satır eklenebilir: "Bu arada başka bir model bu tuzağa düşmemişti."
2. **Çeviri kendi izini bırakıyor.** Tur 2'de Erdoğan, Macron ve Merkel metinleri toplayıcının
   çevirisi. Putin–Trump'ın en sona düşmesinde "aynı çevirmen" etkisinin payı ayrıştırılamıyor
   (diğer üç set aynı kişi tarafından çevrildiyse birbirlerine yaklaşmaları kısmen bundan olabilir).
   S13 bunu "çevirmenin sesi" diye tek cümleyle söylüyor; daha fazla iddia etmiyoruz.
3. **S02'deki "konuşmaları karıştırıp iki bin kez tekrarladım"** bootstrap'in (konuşmaları yerine
   koyarak yeniden örnekleme) sadeleştirilmiş anlatımı. Daha kesin istenirse: "konuşmaları rastgele
   yeniden seçip iki bin kez hesapladım".
4. **S10'daki "ortalama altısı"** 5,98'in yuvarlaması; ekranda kesin değer (%59,8) yazıyor.
5. **Süreler tahmin.** Saniyede 6–6,8 hece varsayımıyla 62–70 sn. Gerçek kayıt 75 sn'yi geçerse
   S12 ilk çıkarılacak satır.
6. **Marka şartnamesindeki iki gerilim** (plan içinde çözüm önerildi, onayını isterim):
   (a) Kayıt yalnızca ses → tüm video `AVATAR` modu, ama marka "aynı mod 12 sn'den uzun sürmez"
   diyor; ritmi mod yerine yerleşim değişimiyle (A/B/C) taşıdım. (b) `alt-orta` 2,5× avatarda yüz
   alt güvenli alanın üstünde kalınca gövde havada kalıyor; gövdeyi bir `sarap-siyah` kürsü paneline
   oturttum ve altyazıyı ceketin üzerine aldım (defne karelerinde açık toga yüzünden altyazıya plaka).
7. Brifte geçen `sources/baskan-analizi` klasörü henüz yok; bu senaryo düzenlendikten sonra
   kaynak olacak.
