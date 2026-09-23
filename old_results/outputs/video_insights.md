# Video insights — candidate findings

Generated 2026-09-22 19:08 from the result tables (primary model Qwen/Qwen3-Embedding-8B; robustness model BAAI/bge-m3). Every finding is about the collected speech corpus and its embeddings. None of them measures ideology, political quality, personality, competence or morality, and none is an endorsement.

**Global caution to state on camera:** each leader speaks a different language in this corpus (Putin and Trump both in English transcript), the speeches come from different years and formats, and there are only 3–5 speeches per leader. Findings that change with the embedding model are marked as such.

## Finding 1

**FINDING**  
In this corpus, a chunk's nearest neighbours in embedding space are almost always other chunks by the same leader — and each leader speaks a different language.

**NUMBER**  
Share of the 10 nearest neighbours (other speeches only) from the same leader: 69%–100% (Erdoğan 100%, Macron 96%, Merkel 69%, Putin 92%, Trump 87%); 3.7×–14.8× what random neighbours would give.

**TECHNICAL EXPLANATION**  
k-nearest-neighbour analysis on 304 unit-normalised Qwen/Qwen3-Embedding-8B chunk vectors, excluding chunks of the same speech. Leader and language are confounded (tr/fr/de/en; Putin and Trump share English), so the model's language signal and the speaker signal cannot be separated here.

**VIDEO VERSION**  
"Embedding uzayında bu konuşmaların en yakın komşuları neredeyse hep aynı liderin diğer konuşmalarından geliyor: %69 ile %100 arasında. Ama dikkat, her lider farklı bir dilde konuşuyor; model önce dili görüyor."

**CAUTION**  
This is not evidence of distinctive 'personal styles'. Language, transcript conventions and speech genre all pull chunks of one leader together; an English-normalised corpus would be needed to separate them.

## Finding 2

**FINDING**  
The two collected speech sets whose centroids sit closest in the Qwen/Qwen3-Embedding-8B space are Putin–Trump.

**NUMBER**  
Cosine similarity 0.744 (95% speech-level bootstrap interval 0.633–0.759); closest pair in 89% of 2000 resamples. Under BAAI/bge-m3 the same pair ranks 10 of 10.

**TECHNICAL EXPLANATION**  
Chunk vectors → normalised speech centroids → normalised leader centroid (each speech weighs equally). Both corpora are English transcripts, and the pair drops to rank 10 with the second model, so language and model choice are the leading explanations.

**VIDEO VERSION**  
"Bu embedding modelinde en yakın iki konuşma seti Putin–Trump çıktı: kosinüs benzerliği 0.74. Ama ikisi de İngilizce metin ve ikinci modelde aynı çift 10. sıraya düşüyor."

**CAUTION**  
Semantic similarity of the collected speeches in one model's space; not ideological, political or personal similarity. Not robust to the embedding model.

## Finding 3

**FINDING**  
Macron–Merkel is the only pair that ranks in the top two under both embedding models.

**NUMBER**  
Qwen/Qwen3-Embedding-8B: 0.698 (rank 2); BAAI/bge-m3: 0.942 (rank 1). Difference to the top pair is not significant: 95% CI -0.052 to 0.093.

**TECHNICAL EXPLANATION**  
Leader-centroid cosine similarity computed independently with two multilingual embedding models; the bootstrap difference CI resamples speeches within each leader.

**VIDEO VERSION**  
"İki farklı embedding modelinde de ilk ikide kalan tek çift Macron–Merkel. Bu sonuç modele göre değişmeyen az sayıdaki bulgudan biri."

**CAUTION**  
Two European New Year addresses in French and German; similar genre and neighbouring topics (Europe, energy, climate) are plausible drivers. Not a claim about the two people.

## Finding 4

**FINDING**  
Which corpora look 'close' depends strongly on the embedding model: the two models disagree about the ranking of the ten leader pairs.

**NUMBER**  
Spearman rank correlation between the pair rankings of Qwen/Qwen3-Embedding-8B and BAAI/bge-m3: -0.37. Erdoğan–Macron is the least similar pair in the first model (0.581) and rank 2 of 10 in the second (0.941).

**TECHNICAL EXPLANATION**  
Same chunks, same aggregation, two models (4096-d vs 1024-d). BGE-M3's space is more compressed (mean off-diagonal similarity 0.88 vs 0.65) and less language-clustered (same-leader neighbour share Erdoğan 100% → 47%).

**VIDEO VERSION**  
"İşin ilginç tarafı: modeli değiştirince sıralama tersine dönebiliyor. İki modelin lider çifti sıralamaları arasındaki korelasyon -0.37. Yani 'kim kime yakın' sorusunun cevabı modelin gözlüğüne bağlı."

**CAUTION**  
Neither model is 'right'. Cross-lingual geometry with 3–5 speeches per leader is fragile; only findings that survive both models should be quoted as findings about the corpus.

## Finding 5

**FINDING**  
The three most represented themes in each collected speech set (embedding similarity to language-matched theme descriptions).

**NUMBER**  
Erdoğan: Foreign Policy & Geopolitics (0.55, top-3 in 89% of resamples); National Identity & Unity (0.53, top-3 in 95% of resamples); Crisis, Threat & Resilience (0.53, top-3 in 70% of resamples)  
Macron: Future, Reform & Technology (0.68, top-3 in 100% of resamples); Economy & Welfare (0.63, top-3 in 100% of resamples); Democracy, Law & Institutions (0.57, top-3 in 99% of resamples)  
Merkel: Social Solidarity & Values (0.56, top-3 in 100% of resamples); Future, Reform & Technology (0.53, top-3 in 97% of resamples); Crisis, Threat & Resilience (0.44, top-3 in 63% of resamples)  
Putin: Social Solidarity & Values (0.68, top-3 in 95% of resamples); National Identity & Unity (0.66, top-3 in 97% of resamples); Security & Military (0.56, top-3 in 59% of resamples)  
Trump: Economy & Welfare (0.67, top-3 in 75% of resamples); Security & Military (0.63, top-3 in 86% of resamples); Democracy, Law & Institutions (0.60, top-3 in 74% of resamples)  
Values are mean percentile ranks over the whole corpus (0.5 = corpus average).

**TECHNICAL EXPLANATION**  
Each chunk is compared with the eight theme descriptions written in the chunk's own language; percentile ranks are taken over all chunks, averaged per speech, then per leader.

**VIDEO VERSION**  
"Her konuşma setinde en çok yer alan tema: Erdoğan için dış politika ve jeopolitik, Macron için gelecek, reform ve teknoloji, Merkel için toplumsal dayanışma ve değerler, Putin için toplumsal dayanışma ve değerler, Trump için ekonomi ve refah. İlk üçün tamamı ve güven aralıkları grafikte."

**CAUTION**  
These describe which themes the collected speeches lean towards relative to this corpus. They do not say why a theme was emphasised, and the NLI classifier ranks the themes differently (see the method-agreement finding).

## Finding 6

**FINDING**  
The single most stable theme signal in the corpus is Future, Reform & Technology in the Macron speeches.

**NUMBER**  
Mean percentile 0.68; the leader's top theme in 93% of 2000 speech-level resamples; also the top theme under BAAI/bge-m3 (yes).

**TECHNICAL EXPLANATION**  
Bootstrap resamples speeches with replacement within the leader and recomputes the theme profile each time; a theme that stays on top across resamples does not depend on one speech.

**VIDEO VERSION**  
"En sağlam tema sinyali Macron konuşmalarındaki 'Gelecek, Reform ve Teknoloji': 2000 yeniden örneklemede yüzde 93 oranında birinci sırada."

**CAUTION**  
Stability across resamples of the same speeches is not the same as generalisation to speeches outside this corpus.

## Finding 7

**FINDING**  
Conflict/threat and cooperation/solidarity framing, measured for all five speech sets (no ranking, no labels).

**NUMBER**  
conflict_threat_framing: Erdoğan 0.61 [0.52–0.72], rate 37%; Macron 0.50 [0.45–0.55], rate 24%; Merkel 0.35 [0.29–0.44], rate 13%; Putin 0.43 [0.36–0.49], rate 15%; Trump 0.50 [0.41–0.59], rate 13%.  
cooperation_solidarity_framing: Erdoğan 0.51 [0.40–0.64], rate 23%; Macron 0.43 [0.38–0.48], rate 17%; Merkel 0.52 [0.44–0.60], rate 35%; Putin 0.63 [0.53–0.74], rate 37%; Trump 0.49 [0.34–0.66], rate 20%.

**TECHNICAL EXPLANATION**  
Mean percentile of chunk similarity to a framing description (language-matched), speech-weighted; 'rate' = share of a leader's chunks in the corpus top quartile. The leader ordering for conflict framing has Spearman -0.80 between the two embedding models, i.e. it is model-sensitive.

**VIDEO VERSION**  
"Çatışma-tehdit ve iş birliği-dayanışma dilini iki ayrı ölçek olarak ölçtük; kimseye 'en sert' ya da 'en yumuşak' etiketi yok. Erdoğan çatışma 0.61, iş birliği 0.51. Macron çatışma 0.50, iş birliği 0.43. Merkel çatışma 0.35, iş birliği 0.52. Putin çatışma 0.43, iş birliği 0.63. Trump çatışma 0.50, iş birliği 0.49."

**CAUTION**  
Descriptive similarity to two concept descriptions, in one model. Intervals overlap for most leaders and the ordering flips with the second model; do not read as tone, intent or aggression.

## Finding 8

**FINDING**  
The collected corpora differ in how concentrated they are around their own centre.

**NUMBER**  
Mean cosine distance of speech centroids to the leader centroid: Erdoğan 0.065, Macron 0.025, Merkel 0.050, Putin 0.039, Trump 0.049. Within speeches (chunk → speech centroid): Erdoğan 0.258, Macron 0.326, Merkel 0.334, Putin 0.174, Trump 0.243.

**TECHNICAL EXPLANATION**  
Distances in the original 4096-d space. Erdoğan's spread is driven partly by one speech of a different type (a symposium speech among New Year messages); Putin's low within-speech spread goes with the shortest speeches (26 chunks).

**VIDEO VERSION**  
"Konuşma setlerinin kendi merkezine ne kadar toplandığına da baktık: Macron konuşmaları merkezine en yakın (0.025), Erdoğan en dağınık (0.065). Bu, tutarlılık değil, derlemin çeşitliliği."

**CAUTION**  
Semantic concentration of the collected files only. It is not 'consistency' or 'inconsistency' of a person, and it is sensitive to speech type mix and speech length.

## Finding 9

**FINDING**  
Unsupervised clustering rediscovers the leaders, not topics — until each leader's centroid is subtracted, after which mixed topical clusters appear.

**NUMBER**  
HDBSCAN on the raw chunk vectors: 6 clusters, every one 100% a single leader, 19% unassigned. After leader-centering: 9 clusters, 4 of them mixed (entropy ≥ 0.75), e.g. 'National Identity & Unity / Social Solidarity & Values' (41 chunks, 5 leaders); 'Economy & Welfare' (21 chunks, 5 leaders); 'Crisis, Threat & Resilience' (7 chunks, 4 leaders).

**TECHNICAL EXPLANATION**  
PCA(50) → HDBSCAN; candidate labels come from the fixed-theme scores of the member chunks. Leader-centering removes the leader/language mean vector from each chunk so that what remains is within-corpus variation.

**VIDEO VERSION**  
"Denetimsiz kümeleme önce sadece liderleri (aslında dilleri) buluyor. Her liderin ortalamasını çıkarınca ekonomi, Avrupa/dış politika, kriz gibi liderler arası ortak konu kümeleri ortaya çıkıyor."

**CAUTION**  
Cluster membership depends on parameters (see the grid table) and 57% of chunks stay unassigned after centering; labels are neutral topical candidates, not interpretations.

## Finding 10

**FINDING**  
The two theme-scoring methods agree on the big picture but not on details: the NLI classifier sees the same top theme for every leader.

**NUMBER**  
Embedding vs NLI: same top theme for 34% of chunks; chunk-level Spearman 0.34–0.57. NLI top theme: 'Social Solidarity & Values' for 5 of 5 leaders. Language-matched vs English descriptions: Spearman 0.79–0.91.

**TECHNICAL EXPLANATION**  
Option A = cosine to theme descriptions (same embedding model); Option B = multilingual zero-shot NLI (mDeBERTa) with 'This text is about {theme}'. Most speeches are New Year addresses, a genre saturated with solidarity and gratitude language, which the NLI method weights heavily.

**VIDEO VERSION**  
"İki farklı yöntemle tema ölçtük; parça düzeyinde sadece %34 aynı birinci temayı seçiyor. NLI sınıflandırıcı beş liderde de 'toplumsal dayanışma'yı öne koyuyor; çünkü konuşmaların çoğu yılbaşı mesajı."

**CAUTION**  
Theme scores are method-dependent estimates, not measurements of intent. Genre (New Year address) is a strong common factor across all five corpora.

## Finding 11

**FINDING**  
The whole experiment runs on a small, fully traceable corpus.

**NUMBER**  
20 speeches, 21,117 cleaned words → 304 chunks (median 110 tokens) → 4096-dimensional vectors from an 8B-parameter model; embedding all chunks took 4.1 s on one RTX 5090; uncertainty from 2000 speech-level bootstrap resamples.

**TECHNICAL EXPLANATION**  
Paragraph-based chunking (80–180 tokens, no overlap), unit-normalised embeddings, chunk → speech → leader aggregation so that long speeches do not dominate.

**VIDEO VERSION**  
"Tüm deney 20 konuşma, 304 parça ve 4096 boyutlu vektörlerden oluşuyor; 8 milyar parametreli model hepsini 4 saniyede gömdü."

**CAUTION**  
Small corpus: 3–5 speeches per leader, mostly New Year addresses from different years. Every number above is a statement about these files.
