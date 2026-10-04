# Senaryo v2 — "Liderlerin konuşmalarını yapay zekaya okuttum"

Seslendirme metni. Anlatıcı ekranda avatar, ses senin (kayıt yalnızca ses → tüm video `AVATAR` modu).

- 17 cümle, 188 kelime. Tahmini süre **~88–90 sn** (saniyede ~6,4 hece, gülme payı dahil).
  Marka sınırı olan 90 sn'nin içinde, ama ilk brifteki 50–75 sn'yi aşıyor. ~75 sn'lik kesim aşağıda.
- ★ = defne tacı anı (3 adet, toplam ~13,7 sn ≈ %15; marka sınırı %20).
- `[...]` okunmaz: tempo ya da ton notu.
- Dil/çeviri hikayesi isteğin üzerine seslendirmede yok. Çeviri bilgisi yalnızca S04'te ekranda
  dipnot olarak duruyor (bkz. README, "Dikkat" bölümü).

---

### Giriş

**S01** — Siyasi söylemlerin yapay zekayla analiz edilebileceğini biliyor muydunuz?

**S02** — Bugün yapay zeka her işte kullanılıyor; devletleri yöneteceğini konuşanlar bile var.

**S03** — Ben ise yapay zekanın insanların yerine değil, yanında çalışacağına inanıyorum.

### Kurulum

**S04** — Beş liderin, çoğu yılbaşı mesajı olan yirmi konuşmasını bir yapay zeka modeline okuttum.

### 1 · Kim ne konuşuyor? (`top_themes_by_leader`)

**S05** — Kim ne konuşuyor? Macron'da gelecek ve reform, Putin'de ulusal kimlik, Trump'ta ekonomi, Merkel'de dayanışma.

**S06** — Erdoğan'da dış politika. Hukuk ve kurumlar da önde, ama onu tek bir konuşma taşıyor.

### 2 · FIFA kartları (`rhetorical_radar_all_leaders`)

**S07** — Retorik profillerini radara dökünce aklıma FIFA oyuncu kartları geldi. [kısa gülme]

**S08** ★ — Putin'in kartı: teşekkür 70, vaat 31. Pası herkese veriyor, gol sözü vermiyor.

**S09** — Trump'ta biz-onlar 65, Merkel'de iş birliği 61, Macron'da gelecek 57.

**S10** — Erdoğan'ın kartı en dengelisi: hiçbir özelliği uçta değil.

### 3 · Duygu (`emotion_profile`)

**S11** — Duygu tonu hepsinde olumlu ağırlıklı, en olumlusu Putin. Korku ve düşmanlık en yüksek Trump'ta, o da yüzde 6'nın altında.

### 4 · Üslup (`style_similarity_heatmap`)

**S12** — Üslupta en yakın ikili Erdoğan ile Macron.

**S13** ★ — Asıl ilginci: konuda en çok benzeşen Macron ve Merkel, üslupta benzemiyor.

### 5 · Dağılım (`semantic_dispersion`)

**S14** — Kendi içinde en toplu set Macron'unki, en dağınığı Erdoğan'ınki; yine o tek konuşma yüzünden.

### Kapanış

**S15** — Bunların hiçbiri kimin iyi, kimin kötü olduğunu söylemiyor; sadece bu yirmi metni ölçüyor.

**S16** ★ — Yapay zeka devlet yönetebilir mi, bilmiyorum. [es] Ama biz yapay zeka araçlarıyla liderleri denetleyebiliriz.
_(taç yalnızca ikinci cümlede)_

**S17** — Kod GitHub'ımda.

---

## ~75 sn'lik kesim

Sırayla çıkar: **S12** (S13 tek başına durabilir: "Üslupta asıl ilginci…"), **S09**, **S14**.
Kalan ~76 sn. Daha da kısa gerekirse S02 ve S03 birleşir:
"Yapay zekanın devlet yöneteceğini konuşanlar var; ben ise onun insanların yanında çalışacağına inanıyorum."

## Senin giriş metninde yaptığım değişiklikler

- "analiz edilebileceğini" → "yapay zekayla analiz edilebileceğini" (akış için).
- "her iş için kullanılıyor hatta bir gün devletleri bile yöneteceğini konuşanlar var" → iki yan cümle, noktalı virgülle.
- "insanlarla asiste bir şekilde çalışacağına" → "insanların yerine değil, yanında çalışacağına"
  ("asiste" yazı dilinde anlaşılıyor ama seste takılıyor). İstersen orijinaline dön.
- "5 yıllık tüm ulusa sesleniş konuşmaları" demedim, çünkü veri bunu karşılamıyor (README → Dikkat 1).

## Her cümlenin dayanağı

Sayılar `build_data.py` ile alt tablolardan yeniden hesaplandı ve repodaki çıktılarla eşleşti
(`verification_log.txt`, 202 kontrol). "tablo" = bootstrap payı ya da aralığı; yeniden hesaplanamadı,
olduğu gibi okundu.

| # | iddia | sayı | kaynak |
|---|---|---|---|
| S04 | 5 lider, 20 konuşma, 16'sı yılbaşı mesajı; diğerleri: Erdoğan sempozyum, Trump veda + yemin + alıntı derlemesi | 3–5 / lider | `data/metadata.csv` |
| S05 | En yüksek temalar: Macron gelecek/reform 0,69 (her bootstrap'te 1.); Putin ulusal kimlik 0,68 (dayanışma 0,67); Trump ekonomi 0,56 (ilk 3'te %100); Merkel dayanışma 0,60 (ilk 3'te %99; gelecek 0,61 ile başa baş) | 0,50 = ortalama | `top_themes_by_leader.csv`, `bootstrap_top_theme_stability.csv` (tablo) |
| S06 | Erdoğan: dış politika 0,56 (ilk 3'te %99,8); demokrasi/hukuk/kurumlar 0,58, ama sempozyum konuşması 0,91, dört yılbaşı mesajı 0,42–0,60; o konuşma olmadan ortalama 0,50 | | `theme_profile_speech.csv` |
| S08 | Putin: teşekkür 0,70 (bootstrap'lerin %99,95'inde 1.), vaat 0,31 (5/5) | ×100 | `style_rankings.csv` |
| S09 | Trump biz–onlar 0,65 (1.; %81); Merkel iş birliği 0,61 (1.; %66); Macron gelecek 0,57 (1.; yalnızca %45, Putin 0,55 çok yakın) | ×100 | aynı |
| S10 | En dar aralık Erdoğan: 7 ölçü 0,41–0,53 (12 puan); diğerleri 19–39 puan | | `framing_speech.csv` |
| S11 | Duygu değeri hepsinde pozitif (0,42–0,77), en yüksek Putin 0,77 (%79); korku/üzüntü en yüksek Trump %5,5 (%70), düşmanlık en yüksek Trump %3,5 (%85) | | `emotion_profile_leader.csv`, `style_rankings.csv` |
| S12 | Üslup kosinüsü en yüksek Erdoğan–Macron 0,42 (en yakın çift, bootstrap'lerin %58'inde) | | `style_similarity_leader.csv`, `style_pairs.csv` |
| S13 | Macron–Merkel içerik benzerliği 0,850, 10 çiftin 1.'si (%100); üslup kosinüsü −0,20. İçerik ile üslup arasında Spearman 0,21 | | `leader_cosine_similarity.csv`, `content_vs_style.csv` |
| S14 | Konuşma merkezlerinin lider merkezine uzaklığı: Macron 0,019 (en toplu) … Erdoğan 0,065 (en dağınık). Sempozyum konuşması 0,162, yılbaşı mesajları 0,035–0,049; onsuz Erdoğan 0,031 | | `semantic_dispersion.csv` |
