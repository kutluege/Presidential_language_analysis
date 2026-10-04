# Senaryo — "Yapay zeka kimi kime benzetti?"

Seslendirme metni. Konuşma dili, senin ağzından; anlatıcı ekranda avatar, ses senin
(kayıt yalnızca ses → `brand/identity.md` gereği tüm video `AVATAR` modu).

- 14 cümle, 139 kelime. Tahmini süre **~62–70 sn** (sakin Türkçe dış ses, saniyede 6–6,8 hece).
- ★ = defne tacı anı (3 adet, toplam ~10,6 sn ≈ sürenin %15'i; marka sınırı %20).
- `[...]` okunmaz: tempo ya da ton notu.

---

**S01** — Bir yapay zeka modeline beş liderin konuşmalarını okuttum ve sordum: kim kime en çok benziyor?

**S02** — Cevap: Putin ile Trump. Konuşmaları karıştırıp iki bin kez tekrarladım; yüzde 89'unda yine onlar.

**S03** — Sonra bir şey dikkatimi çekti. [kısa es]

**S04** — Erdoğan Türkçe, Macron Fransızca, Merkel Almanca. Putin'inki resmi İngilizce çeviri, Trump zaten İngilizce.

**S05** ★ — Yani o ikisi, setteki tek İngilizce metinlerdi.

**S06** — Ben de hepsini İngilizceye çevirip aynı modelle baştan ölçtüm.

**S07** ★ — Putin–Trump birincilikten onunculuğa, yani en sona düştü.

**S08** — İşin ilginci, onların puanı kıpırdamadı bile. [deadpan, kısa es]

**S09** — Değişen diğerleriydi: aynı dile geçince hepsi birbirine yaklaştı.

**S10** — Erdoğan'ın her paragrafının en yakın on komşusuna baktım. Önce neredeyse hepsi yine Erdoğan'dı; çeviriden sonra ortalama altısı.

**S11** ★ — Yani model önce dili görüyormuş, anlamı sonra.

**S12** — Daha büyük ikinci bir modelle de denedim; o da Putin–Trump'ı en sona koydu.

**S13** — Bu, liderler hakkında bir şey kanıtlamıyor. Ölçtüğüm şey yirmi konuşmanın metni; çevirilerde çevirmenin sesi de var.

**S14** — Kod GitHub'ımda.

---

## Kısaltma / alternatif satırlar

- **Süre taşarsa:** S12 çıkarılabilir (~5 sn). Hikaye bozulmaz; yalnızca "ikinci model de
  doğruladı" güvencesi gider.
- **S08 sayıyla:** "…kıpırdamadı bile: sıfır virgül yedi yüz kırk dörtten yedi yüz kırk üçe."
  (+2,5 sn). Sayı zaten ekranda yazıyor, o yüzden varsayılan metinde okunmuyor.
- **Tez bağı (isteğe bağlı, S13'ten önce):** "Model bir şey buldu diye, aradığın şeyi bulmuş olmuyor."
  Markadaki "ne değil, neden" tezine bağlanır. Süre bütçesi el verirse eklenebilir.

## Her cümlenin dayanağı

Tüm sayılar `build_data.py` ile alt tablolardan yeniden hesaplandı ve repodaki çıktılarla
birebir eşleşti (`verification_log.txt`).

| # | iddia | sayı | kaynak (repo) |
|---|---|---|---|
| S01 | 5 lider, konuşma metinleri | 20 konuşma (3–5'er) | `data/metadata.csv` |
| S02 | Tur 1'de (orijinal diller, Qwen3-Embedding-8B) en yakın çift Putin–Trump | 0,744; 2000 bootstrap örneğinin %88,7'sinde birinci | `old_results/outputs/tables/leader_pairs.csv`, `.../bootstrap_pair_rank_stability.csv` |
| S04 | Tur 1 dilleri: tr / fr / de / en (Putin: resmi İngilizce transkript) / en | — | `old_results/README.md`, `data/metadata.csv` |
| S05 | Putin ve Trump, Tur 1'deki tek İngilizce setler | — | aynı |
| S06 | Aynı model, aynı parçalama, aynı hesap; yalnızca dil değişti | — | `outputs/PROJECT_BRIEF.md` §2, `outputs/robustness_report.md` (kontrol G) |
| S07 | Sıra 1 → 10 | 1 → 10 | `outputs/tables/language_effect_pairs.csv` |
| S08 | Putin–Trump benzerliği değişmedi | 0,744 → 0,743 (fark −0,00015); iki turda Putin ve Trump parça metinleri birebir aynı | aynı + `verification_log.txt` §6 |
| S09 | Diğer 9 çiftin hepsi arttı | +0,083 … +0,276 | aynı |
| S10 | Erdoğan parçalarının en yakın 10 komşusunda (aynı konuşma hariç) Erdoğan payı, aynı model | %99,5 → %59,8 (10 komşuda ortalama 9,95 → 5,98) | `outputs/tables/language_effect_knn.csv` |
| S11 | Yorum: bu modelde dil sinyali içerikten baskındı | yukarıdaki iki sonuç | — |
| S12 | İkinci model (KaLM-Embedding-Gemma3-12B, ~12 milyar parametre), İngilizce metinde Putin–Trump 10/10 | 0,701; 2000 örneğin %90,7'sinde en uzak çift | `outputs/tables/leader_pairs.csv`, `outputs/tables/bootstrap_pair_rank_stability.csv` |
| S13 | 20 konuşma; Erdoğan / Macron / Merkel çeviri, Putin resmi çeviri | — | `data/metadata.csv` |
