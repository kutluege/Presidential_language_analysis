# Exploratory topic discovery — kalm_embedding_gemma3_12b_leadercentered

PCA 50 components (66% variance kept) → HDBSCAN(min_cluster_size=6, min_samples=2, euclidean, eom). 2 clusters, 18% of chunks unassigned (noise).

Candidate labels are the top fixed themes of the member chunks (neutral topical descriptions, not interpretations). Cluster membership is exploratory and depends on parameters — see the grid table.

## Cluster -1 — (noise — not assigned)  (n=46, 18% of chunks)

Leader distribution: erdogan 7 (15%; corpus share 25%), macron 17 (37%; corpus share 30%), merkel 4 (9%; corpus share 15%), putin 8 (17%; corpus share 10%), trump 10 (22%; corpus share 19%) · mixing entropy 0.93 (1 = perfectly mixed)

Theme profile (mean percentile): Security & Military 0.59, Crisis, Threat & Resilience 0.59, Social Solidarity & Values 0.58

Frequent terms (vs corpus): support, several, open, course, millions, hands, concern, true, common, first, marked, defending

Representative passages (closest to centroid):

1. *merkel / merkel1* (cos 0.35): And even with the images of bombed-out Aleppo in Syria before our eyes, we can once again say how important and right it was that, during the past year, our country helped those who genuinely need our protection to gain a foothold here among us and to integrat…
2. *macron / macron2023* (cos 0.29): It was also marked by growing geopolitical tensions, by the consequences of climate disruption on our territory, and by acts of terrorism on our soil. By divisions, acts of hatred and, at times, violence on several occasions, which weaken the cohesion of the N…
3. *putin / putin2022* (cos 0.28): With all my heart, I share your pain and ask you to accept my sincere words of support.  Friends,  Our country has always celebrated the start of the New Year, even during very difficult times. It has always been everyone’s favourite holiday, and has a magical…
4. *macron / macron2025* (cos 0.28): I know all the impatience, and sometimes the anger, that continues to exist in the country, and I share several of those concerns. These urgent matters require answers. From the very first weeks of the year ahead, the Government and Parliament will have to bui…
5. *merkel / merkel1* (cos 0.27): Our state does everything it can to guarantee its citizens security in freedom.  This work is never finished, and especially this year we have provided our security authorities with a great deal of additional support. In 2017, as the Federal Government, wherev…

## Cluster 0 — National Identity & Unity / Future, Reform & Technology  (n=9, 4% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 25%), macron 9 (100%; corpus share 30%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 10%), trump 0 (0%; corpus share 19%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): National Identity & Unity 0.60, Future, Reform & Technology 0.59, Social Solidarity & Values 0.49

Frequent terms (vs corpus): paralympic, olympic, games, french, pride, dame, cathedral, sporting, promised, impossible, rebuilt, paris

Representative passages (closest to centroid):

1. *macron / macron2024* (cos 0.80): A France that shines through its sporting achievements, its emotions, its generosity, and through a city of Paris shown at its very best.  Our Olympic and Paralympic Games, yes, are and will remain an unforgettable moment in the life of the Nation.  In this mo…
2. *macron / macron2023* (cos 0.77): We will be proud of our athletes, our artists, our landscapes, and of this great popular celebration, made possible by thousands of volunteers, who will also build a sporting legacy for our Nation. Through the commitment of us all, beginning tomorrow.  Yes, 20…
3. *macron / macron2023* (cos 0.74): Finally, 2024 will be a year of French pride. Pride in the thousands of craftsmen, builders and entrepreneurs who have taken part in the magnificent project to rebuild Notre-Dame de Paris, whose spire once again rises toward the sky above a cathedral that will…
4. *macron / macron2023* (cos 0.65): 2024 will be a year of pride in the French language. After restoring the Château de Villers-Cotterêts and creating there the Cité internationale de la langue française, in a few months we will welcome the French-speaking world there.  2024 will also be a year …
5. *macron / macron2022* (cos 0.64): As for us, let us be this generation of builders.  In the coming months of 2023, the reconstruction work on Notre-Dame de Paris, this extraordinary project, will move closer to completion. In the coming months, our entire country will come together in a spirit…

## Cluster 1 — Foreign Policy & Geopolitics / Economy & Welfare  (n=195, 78% of chunks)

Leader distribution: erdogan 56 (29%; corpus share 25%), macron 49 (25%; corpus share 30%), merkel 34 (17%; corpus share 15%), putin 18 (9%; corpus share 10%), trump 38 (19%; corpus share 19%) · mixing entropy 0.96 (1 = perfectly mixed)

Theme profile (mean percentile): Foreign Policy & Geopolitics 0.51, Economy & Welfare 0.50, Democracy, Law & Institutions 0.50

Frequent terms (vs corpus): well, respect, dear, place, live, future, borders, long, jobs, everyone, strength, europe

Representative passages (closest to centroid):

1. *macron / macron2025* (cos 0.33): Our independence requires us to continue investing in our armed forces, our security forces, our public services, and our economy despite financial difficulties. For ten years, I have argued strongly for this independence, and as Europeans we have done a great…
2. *macron / macron2022* (cos 0.33): In short, in 2023, step by step, we will have to consolidate our energy, economic, social, industrial, financial and strategic independence, and strengthen what I might call our strength of spirit. This is what we owe to our children.  This is not, and never w…
3. *macron / macron2022* (cos 0.30): And so many other projects will take shape throughout our country, enabling France both to reduce carbon emissions and to reduce unemployment. In the coming months, in our classrooms, in our hospitals and in our doctors’ practices, you will see the first tangi…
4. *erdogan / erdogan2025* (cos 0.30): Just as we have done for the past 23 years, with nothing but love for our nation and our homeland in our hearts, we will continue to serve all 86 million of our citizens and work selflessly for the prosperity, peace, and well-being of all of Türkiye.  In 2026 …
5. *macron / macron2025* (cos 0.29): Let us not give up on reconciling the climate, biodiversity, growth, and independence. Let us not give up on major scientific discoveries, on our love of science and research, or on economic success.  Let us not give up on the place of reading, beauty, and cul…

## Parameter grid

 min_cluster_size  min_samples  n_clusters  noise_share  relative_validity  is_primary
                4            2          12        0.496              0.113       False
                4            3           8        0.580              0.036       False
                4            5           6        0.664              0.037       False
                5            2          10        0.528              0.133       False
                5            3           2        0.308              0.000       False
                5            5           2        0.444              0.000       False
                6            2           2        0.184              0.001        True
                6            3           2        0.308              0.000       False
                6            5           2        0.444              0.000       False
                8            2           2        0.184              0.001       False
                8            3           2        0.308              0.000       False
                8            5           4        0.692              0.021       False
               10            2           2        0.404              0.000       False
               10            3           5        0.652              0.046       False
               10            5           3        0.728              0.000       False