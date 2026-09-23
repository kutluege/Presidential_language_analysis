# Video insights — candidate findings (run 2, English corpus)

Generated 2026-09-23 12:50 from the result tables · primary model KaLM-Embedding-Gemma3-12B-2511 · robustness model Qwen3-Embedding-8B. Every finding is about the collected speech corpus and its measurements. None measures ideology, political quality, personality, competence or morality; none is an endorsement.

**Global caution to state on camera:** Erdoğan, Macron and Merkel are analysed in English translation and Putin in an official English transcript; for them, style measurements describe the translated text and therefore also carry the translator's choices. The speeches come from different years and formats, and there are 3–5 per leader. Rankings are sorted measurements with confidence intervals; where intervals overlap, no difference should be claimed.

## Finding 1

**FINDING**  
Translating the corpus into English removed most of the language signal that dominated the first run: chunks stopped clustering by leader nearly as much, and Erdoğan's speeches moved from the edge of the space toward the middle.

**NUMBER**  
Same-leader share of a chunk's 10 nearest neighbours (same model, Qwen3-Embedding-8B): Erdoğan 100% → 60%, Macron 96% → 71%, Merkel 69% → 48%, Putin 92% → 76%, Trump 87% → 66%. Erdoğan's four leader pairs: mean rank 8.5 → 4.2 of 10. Rank correlation of the ten pair similarities between the two corpora: -0.43.

**TECHNICAL EXPLANATION**  
Both runs use identical chunking, aggregation and the same Qwen3-Embedding-8B model; only the text language changed (run 1 archived in old_results/). Language and speaker were confounded in run 1; translation separates them at the price of adding the translator's voice.

**VIDEO VERSION**  
"Konuşmaları İngilizceye çevirince tablo değişti: birinci turda Erdoğan'ın parçalarının komşuları yüzde 100 oranında yine Erdoğan'dı, şimdi yüzde 60. Model önce Türkçeyi görüyordu; şimdi içeriği görüyor."

**CAUTION**  
The English texts of Erdoğan, Macron, Merkel, Putin are translations or official transcripts; what remains is content plus translator style. Putin and Trump did not change between runs.

## Finding 2

**FINDING**  
Even in English, a chunk's nearest neighbours still come from the same leader far more often than chance — the speech sets keep a recognisable content signature, and how strong it looks depends on the model.

**NUMBER**  
Same-leader neighbour share (KaLM-Embedding-Gemma3-12B-2511): Erdoğan 83% (×3.9 vs chance), Macron 89% (×3.7 vs chance), Merkel 78% (×6.6 vs chance), Putin 92% (×12.1 vs chance), Trump 95% (×8.6 vs chance); range 78%–95% against a chance level of 8%–24%. Same text with Qwen3-Embedding-8B: 48%–76%.

**TECHNICAL EXPLANATION**  
kNN (k=10) on 250 unit-normalised vectors, excluding chunks of the same speech; expected share = the leader's share of the remaining chunks. KaLM-Embedding-Gemma3-12B-2511 separates the speech sets more sharply than Qwen3-Embedding-8B does on identical English text.

**VIDEO VERSION**  
"İngilizcede bile bir parçanın en yakın komşuları yüzde 78 ile 95 arasında aynı liderin diğer konuşmalarından geliyor; rastgele olsa bu oran yüzde 8 ile 24 arasında olurdu. İkinci modelde aynı oran yüzde 48 ile 76."

**CAUTION**  
A signature of the collected speech sets (topics, recurring occasions such as New Year addresses, translator style), not a fingerprint of the person; the strength of the signature is model-dependent.

## Finding 3

**FINDING**  
The two speech sets whose centroids sit closest in the KaLM-Embedding-Gemma3-12B-2511 space are Macron–Merkel.

**NUMBER**  
Cosine similarity 0.850 (95% speech-level bootstrap 0.811–0.860); closest pair in 100% of 2000 resamples; rank 1 of 10 under Qwen3-Embedding-8B.

**TECHNICAL EXPLANATION**  
Chunk vectors → normalised speech centroids → normalised leader centroids (equal weight per speech). Agreement between two different embedding models on the same English text is the main robustness test now that language is out of the picture.

**VIDEO VERSION**  
"Yeni modelde en yakın iki konuşma seti Macron–Merkel: kosinüs benzerliği 0.85. İkinci model aynı çifti 1. sıraya koyuyor."

**CAUTION**  
Semantic similarity of the collected speeches, not ideological or personal similarity.

## Finding 4

**FINDING**  
The most distant pair is Putin–Trump; the two models now agree about the overall ordering of the ten pairs.

**NUMBER**  
Putin–Trump: 0.701 (rank 10 of 10 under Qwen3-Embedding-8B). Spearman between the models' pair rankings: 0.83 (run 1, mixed languages: −0.37).

**TECHNICAL EXPLANATION**  
Same chunks, same aggregation, two models (3840-d vs 4096-d). Absolute cosine levels are model-specific; only rankings are compared.

**VIDEO VERSION**  
"En uzak çift Putin–Trump. İki modelin sıralamaları arasındaki korelasyon birinci turda eksi 0.37'ydi, İngilizce metinde 0.83."

**CAUTION**  
With five leaders there are only ten pairs; a rank correlation over ten points is itself uncertain.

## Finding 5

**FINDING**  
The three most represented themes in each collected speech set.

**NUMBER**  
Erdoğan: Democracy, Law & Institutions (0.58, top-3 in 69%); Foreign Policy & Geopolitics (0.56, top-3 in 100%); Security & Military (0.50, top-3 in 67%)  
Macron: Future, Reform & Technology (0.69, top-3 in 100%); Economy & Welfare (0.55, top-3 in 96%); Crisis, Threat & Resilience (0.53, top-3 in 100%)  
Merkel: Future, Reform & Technology (0.61, top-3 in 93%); Social Solidarity & Values (0.60, top-3 in 99%); Democracy, Law & Institutions (0.56, top-3 in 65%)  
Putin: National Identity & Unity (0.68, top-3 in 100%); Social Solidarity & Values (0.67, top-3 in 100%); Security & Military (0.61, top-3 in 99%)  
Trump: Economy & Welfare (0.56, top-3 in 100%); Security & Military (0.53, top-3 in 96%); National Identity & Unity (0.49, top-3 in 74%)  
Values: mean percentile of chunk–theme similarity over the whole corpus (0.5 = corpus average).

**TECHNICAL EXPLANATION**  
Each chunk is compared with eight fixed theme descriptions using the same embedding model; percentiles over all chunks, averaged per speech, then per leader.

**VIDEO VERSION**  
"Her konuşma setinde en çok yer alan tema: Erdoğan için demokrasi, hukuk ve kurumlar, Macron için gelecek, reform ve teknoloji, Merkel için gelecek, reform ve teknoloji, Putin için ulusal kimlik ve birlik, Trump için ekonomi ve refah. İlk üçün tamamı ve güven aralıkları grafikte."

**CAUTION**  
Which themes the collected speeches lean towards relative to this corpus; not why. The NLI classifier ranks themes differently (see the agreement finding).

## Finding 6

**FINDING**  
The most stable theme signal is Future, Reform & Technology in the Macron speeches.

**NUMBER**  
Mean percentile 0.69; top theme of that leader in 100% of 2000 speech-level resamples.

**TECHNICAL EXPLANATION**  
The bootstrap redraws speeches with replacement within each leader and recomputes the profile; a theme that stays on top does not hinge on one speech.

**VIDEO VERSION**  
"En sağlam tema sinyali Macron konuşmalarındaki 'Gelecek, Reform ve Teknoloji': 2000 yeniden örneklemede yüzde 100 oranında birinci."

**CAUTION**  
Stability within this corpus is not generalisation beyond it.

## Finding 7

**FINDING**  
Seven rhetorical dimensions, ranked by measured value (sorted measurements, not a verdict).

**NUMBER**  
Conflict / Threat Framing: Trump 0.54 > Putin 0.51 > Erdoğan 0.49 > Merkel 0.49 > Macron 0.44 — first place holds in 48% of resamples; intervals of 1st and 2nd overlap  
Cooperation / Solidarity Framing: Merkel 0.61 > Putin 0.56 > Macron 0.47 > Erdoğan 0.43 > Trump 0.41 — first place holds in 66% of resamples; intervals of 1st and 2nd overlap  
Past Orientation: Putin 0.62 > Erdoğan 0.53 > Macron 0.49 > Trump 0.44 > Merkel 0.38 — first place holds in 88% of resamples; intervals of 1st and 2nd overlap  
Future Orientation: Macron 0.57 > Putin 0.55 > Erdoğan 0.52 > Merkel 0.45 > Trump 0.37 — first place holds in 45% of resamples; intervals of 1st and 2nd overlap  
Us-versus-Them Contrast: Trump 0.65 > Merkel 0.51 > Putin 0.50 > Erdoğan 0.46 > Macron 0.39 — first place holds in 81% of resamples; intervals of 1st and 2nd overlap  
Gratitude & Recognition: Putin 0.70 > Trump 0.51 > Merkel 0.44 > Macron 0.44 > Erdoğan 0.41 — first place holds in 100% of resamples; intervals of 1st and 2nd overlap  
Promises & Commitments: Trump 0.59 > Macron 0.57 > Erdoğan 0.46 > Merkel 0.43 > Putin 0.31 — first place holds in 64% of resamples; intervals of 1st and 2nd overlap

**TECHNICAL EXPLANATION**  
Each dimension is a written description embedded with the same model; a chunk's score is its cosine similarity, expressed as a corpus percentile; speech means → leader means; 95% speech-level bootstrap intervals and the share of resamples in which the first-ranked leader stays first.

**VIDEO VERSION**  
"Yedi retorik ölçekte ilk sıralar: çatışma / tehdit çerçevesi ölçeğinde Trump, i̇ş birliği / dayanışma çerçevesi ölçeğinde Merkel, geçmişe yönelim ölçeğinde Putin, geleceğe yönelim ölçeğinde Macron, biz-onlar karşıtlığı ölçeğinde Trump, teşekkür ve takdir ölçeğinde Putin, vaatler ve taahhütler ölçeğinde Trump. Ama çoğu farkın güven aralığı örtüşüyor; bunlar sıralı ölçümler, hüküm değil."

**CAUTION**  
Descriptive similarity to a description, in one model, on 20 speeches. Translated leaders (Erdoğan, Macron, Merkel, Putin) carry the translator's phrasing.

## Finding 8

**FINDING**  
Emotional tone, measured by an independent classifier rather than by embeddings.

**NUMBER**  
Affiliative / positive emotion: Putin 0.51 [0.47–0.55], Trump 0.48 [0.38–0.61], Merkel 0.46 [0.40–0.56], Macron 0.46 [0.43–0.48], Erdoğan 0.39 [0.29–0.50]  
Fear, sadness & loss: Trump 0.05 [0.00–0.10], Erdoğan 0.04 [0.01–0.06], Merkel 0.03 [0.01–0.06], Macron 0.03 [0.02–0.04], Putin 0.01 [0.00–0.02]  
Hostility & disapproval: Trump 0.03 [0.01–0.05], Merkel 0.02 [0.01–0.04], Erdoğan 0.01 [0.01–0.02], Macron 0.01 [0.01–0.01], Putin 0.01 [0.00–0.02]  
Sentiment valence (positive − negative): Putin 0.77 [0.56–0.91], Trump 0.65 [0.43–0.88], Merkel 0.52 [0.42–0.62], Macron 0.46 [0.40–0.56], Erdoğan 0.42 [0.21–0.63] Most frequent non-neutral emotion labels: Erdoğan: approval, optimism; Macron: optimism, approval; Merkel: approval, optimism; Putin: admiration, caring; Trump: gratitude, approval

**TECHNICAL EXPLANATION**  
GoEmotions (28 labels, multi-label) grouped into families (family score = highest member probability per chunk) plus a three-class sentiment model (valence = P(positive) − P(negative)); chunk → speech → leader means; 95% speech-level bootstrap.

**VIDEO VERSION**  
"Duygu tonunu embedding'den bağımsız bir sınıflandırıcıyla ölçtük: olumlu-birleştirici duygu, korku-kayıp ve düşmanlık aileleri artı genel duygu değeri. Sonuçlar grafikte, aralıklarıyla."

**CAUTION**  
Classifiers trained on Reddit and Twitter text; political speech is out of domain, and translated leaders are scored on the translation.

## Finding 9

**FINDING**  
On the combined style profile, the two most alike speech sets are Erdoğan–Macron; the least alike are Putin–Trump.

**NUMBER**  
Style distance 1.45 [1.15–3.84], closest pair in 58% of resamples; farthest 4.07. Spearman between content similarity and style similarity over the ten pairs: 0.21.

**TECHNICAL EXPLANATION**  
Style vector per speech = 7 rhetorical percentiles + 3 emotion family means + valence, z-scored across the 20 speeches; leader = mean of its speeches; Euclidean distance and cosine; average-linkage dendrogram.

**VIDEO VERSION**  
"Retorik ve duygu profillerini birleştirince birbirine en çok benzeyen iki set Erdoğan–Macron, en az benzeyen Putin–Trump. İçerik benzerliğiyle stil benzerliği arasındaki korelasyon 0.21."

**CAUTION**  
Style here means these eleven measured dimensions of the English text, nothing more; it is not delivery, voice or charisma.

## Finding 10

**FINDING**  
The speech sets differ in how concentrated they are around their own centre.

**NUMBER**  
Mean cosine distance of speech centroids to the leader centroid: Erdoğan 0.065, Macron 0.019, Merkel 0.029, Putin 0.026, Trump 0.040. Within speeches (chunk → speech centroid): Erdoğan 0.192, Macron 0.216, Merkel 0.204, Putin 0.131, Trump 0.177.

**TECHNICAL EXPLANATION**  
Distances in the original 3840-d space. Speech-type mix (one Erdoğan symposium speech among New Year messages; three different Trump formats) and speech length both affect these numbers.

**VIDEO VERSION**  
"Macron konuşmaları kendi merkezine en yakın (0.019), Erdoğan en dağınık (0.065). Bu tutarlılık değil, derlemin çeşitliliği."

**CAUTION**  
Semantic concentration of the collected files; not 'consistency' of a person.

## Finding 11

**FINDING**  
Unsupervised clustering of the English chunks: how much of the structure is still 'who is speaking' and how much is topic.

**NUMBER**  
HDBSCAN on the raw vectors: 6 clusters; single-leader share of the dominant leader per cluster 95%–100%; 32% unassigned. After subtracting each leader's centroid: 2 clusters, 1 mixed (entropy ≥ 0.75), e.g. 'Foreign Policy & Geopolitics / Economy & Welfare' (195 chunks, 5 leaders).

**TECHNICAL EXPLANATION**  
PCA(50) → HDBSCAN; candidate labels from the fixed-theme scores of the member chunks; leader-centering removes each leader's mean vector so that only within-corpus variation remains.

**VIDEO VERSION**  
"Denetimsiz kümeleme İngilizce metinde bile büyük ölçüde liderleri buluyor; her liderin ortalamasını çıkarınca ekonomi, dış politika, kriz gibi ortak konu kümeleri kalıyor."

**CAUTION**  
Cluster membership depends on parameters (see the grid table); labels are neutral topical candidates.

## Finding 12

**FINDING**  
Independent methods agree only partly, which is why every style number is reported with its method attached.

**NUMBER**  
Embedding vs NLI theme scoring: same top theme for 34% of chunks; chunk-level Spearman 0.16–0.58. Speech-level Spearman between conflict framing (embedding) and the hostility family (classifier): 0.49; cooperation framing vs affiliative emotion: -0.11.

**TECHNICAL EXPLANATION**  
Option A = cosine to descriptions (embedding); Option B = multilingual zero-shot NLI; emotion = supervised classifier. Moderate correlations mean the constructs overlap but are not the same measurement.

**VIDEO VERSION**  
"Aynı şeyi iki yöntemle ölçtüğümüzde parça düzeyinde sadece yüzde 34 aynı birinci temayı buluyoruz. Bu yüzden her sayının yanında yöntemi de söylüyoruz."

**CAUTION**  
Method dependence is a property of the measurements, not a flaw of any speaker.

## Finding 13

**FINDING**  
The whole experiment runs on a small, fully traceable corpus and a single consumer GPU.

**NUMBER**  
20 speeches, 23,905 cleaned English words → 250 chunks (median 107 tokens) → 3840-d vectors from an 11.8B-parameter model (KaLM-Embedding-Gemma3-12B-2511); embedding took 6.8 s at 22.83 GB peak VRAM on an RTX 5090; 2000 speech-level bootstrap resamples for every interval.

**TECHNICAL EXPLANATION**  
Paragraph-based chunking (80–180 tokens, no overlap), unit-normalised embeddings, chunk → speech → leader aggregation, two embedding models, two classifiers, archived first run for the language comparison.

**VIDEO VERSION**  
"Tüm deney 20 konuşma, 250 parça ve 3840 boyutlu vektör; 12 milyar parametreli model hepsini 7 saniyede gömdü, tek bir ekran kartında."

**CAUTION**  
3–5 speeches per leader, mostly New Year addresses from different years; every number is a statement about these files.
