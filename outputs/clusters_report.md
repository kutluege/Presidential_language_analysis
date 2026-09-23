# Exploratory topic discovery — kalm_embedding_gemma3_12b

PCA 50 components (73% variance kept) → HDBSCAN(min_cluster_size=6, min_samples=2, euclidean, eom). 6 clusters, 32% of chunks unassigned (noise).

Candidate labels are the top fixed themes of the member chunks (neutral topical descriptions, not interpretations). Cluster membership is exploratory and depends on parameters — see the grid table.

## Cluster -1 — (noise — not assigned)  (n=81, 32% of chunks)

Leader distribution: erdogan 23 (28%; corpus share 25%), macron 35 (43%; corpus share 30%), merkel 19 (23%; corpus share 15%), putin 1 (1%; corpus share 10%), trump 3 (4%; corpus share 19%) · mixing entropy 0.77 (1 = perfectly mixed)

Theme profile (mean percentile): Democracy, Law & Institutions 0.55, Future, Reform & Technology 0.51, Economy & Welfare 0.47

Frequent terms (vs corpus): state, order, better, ensure, federal, necessary, able, held, them, preparing, fully, accountable

Representative passages (closest to centroid):

1. *macron / macron2022* (cos 0.79): To do this, we must remain united, but we must also preserve an undiminished collective ambition: an ambition to continue transforming our country in the face of vested interests, in the face of all the apparently good reasons for continuing as before, and in …
2. *merkel / merkel1* (cos 0.78): Our state does everything it can to guarantee its citizens security in freedom.  This work is never finished, and especially this year we have provided our security authorities with a great deal of additional support. In 2017, as the Federal Government, wherev…
3. *macron / macron2022* (cos 0.78): New Year’s addresses have something unique about them: they compel us to speak of a future which, in truth, we do not know, but which we know with certainty we will have to face, with our strengths and our weaknesses, but as a united country.  In carrying out …
4. *merkel / merkel1* (cos 0.77): And even with the images of bombed-out Aleppo in Syria before our eyes, we can once again say how important and right it was that, during the past year, our country helped those who genuinely need our protection to gain a foothold here among us and to integrat…
5. *merkel / merkel3* (cos 0.76): In order to safeguard jobs, prosperity and the foundations of our lives, the Federal Government is consistently taking the next steps in the structural transition from traditional to new technologies and is implementing its strategy for digital progress.  Thro…

## Cluster 0 — National Identity & Unity / Security & Military  (n=46, 18% of chunks)

Leader distribution: erdogan 1 (2%; corpus share 25%), macron 0 (0%; corpus share 30%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 10%), trump 45 (98%; corpus share 19%) · mixing entropy 0.07 (1 = perfectly mixed)

Theme profile (mean percentile): National Identity & Unity 0.63, Security & Military 0.61, Economy & Welfare 0.58

Frequent terms (vs corpus): america, american, americans, administration, president, safe, world, people, across, back, nations, four

Representative passages (closest to centroid):

1. *trump / trump1* (cos 0.88): This is a republic of proud citizens who are united by our common conviction that America is the greatest nation in all of history. We are, and must always be, a land of hope, of light, and of glory to all the world. This is the precious inheritance that we mu…
2. *trump / trump3* (cos 0.86): This American carnage stops right here and stops right now.  We are one nation, and their pain is our pain. Their dreams are our dreams, and their success will be our success.  We share one heart, one home, and one glorious destiny.  The oath of office I take …
3. *trump / trump1* (cos 0.86): So I left behind my former life and stepped into a very difficult arena, but an arena nevertheless, with all sorts of potential if properly done. America had given me so much, and I wanted to give something back.  Together with millions of hardworking patriots…
4. *trump / trump1* (cos 0.86): My fellow Americans: Four years ago, we launched a great national effort to rebuild our country, to renew its spirit, and to restore the allegiance of this government to its citizens. In short, we embarked on a mission to make America great again — for all Ame…
5. *trump / trump3* (cos 0.86): So to all Americans in every city near and far, small and large, from mountain to mountain, from ocean to ocean, hear these words:  You will never, never be ignored again.  Your voice, your hopes, and your dreams will define our American destiny.  And your cou…

## Cluster 1 — Democracy, Law & Institutions  (n=6, 2% of chunks)

Leader distribution: erdogan 6 (100%; corpus share 25%), macron 0 (0%; corpus share 30%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 10%), trump 0 (0%; corpus share 19%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Democracy, Law & Institutions 0.92, Future, Reform & Technology 0.44, National Identity & Unity 0.38

Frequent terms (vs corpus): system, sisters, brothers, government, experiences, issue, presidential, multi, gone, constitutional, amendment, party

Representative passages (closest to centroid):

1. *erdogan / erdogan1* (cos 0.90): In fact, the Presidential System that we are discussing today did not suddenly emerge in a day, a month, or a year. Behind it lies such a deep and thought-provoking historical background.  The system we are discussing is the most appropriate solution to the qu…
2. *erdogan / erdogan1* (cos 0.88): My dear brothers and sisters, I congratulate the administrators of SETA for organizing this symposium at a time when Türkiye stands on the eve of a historic decision to transition to the Presidential System.  Every country has a form of government unique to it…
3. *erdogan / erdogan1* (cos 0.87): What we are engaged in here is a struggle over a system. This is a struggle over the system. What will happen after Erdoğan? Whatever the nation says will happen. Whatever God wills will happen.  More importantly, Türkiye has already taken its first steps towa…
4. *erdogan / erdogan1* (cos 0.85): Since our transition to multi-party political life in 1950, we have always tried to keep our democracy standing under the shadow of military coups and tutelary administrations.  The most important consequence of these distortions has been the constant threat t…
5. *erdogan / erdogan1* (cos 0.82): My brothers and sisters, without a soul, the body is merely a corpse. Likewise, if we do not explain to our nation the spirit, essence, and fundamental meaning of this issue, the provisions of the constitutional amendment alone will remain nothing more than dr…

## Cluster 2 — Social Solidarity & Values / National Identity & Unity  (n=25, 10% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 25%), macron 0 (0%; corpus share 30%), merkel 0 (0%; corpus share 15%), putin 25 (100%; corpus share 10%), trump 0 (0%; corpus share 19%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Social Solidarity & Values 0.71, National Identity & Unity 0.67, Security & Military 0.63

Frequent terms (vs corpus): russia, friends, motherland, love, sincere, russian, parents, comrades, happy, always, special, future

Representative passages (closest to centroid):

1. *putin / putin2022* (cos 0.91): As we see the New Year in, everyone strives to give joy to their loved ones, to show them attention and warmth, to give them presents they have been dreaming of, to see the delight in children’s eyes and parents’ touching gratitude for our attention. The older…
2. *putin / putin2025* (cos 0.91): Citizens of Russia, friends,  At this moment, as we stand on the threshold of the New Year, we all feel the passage of time. Before us lies the future, and what it holds largely depends on us.  We draw strength from within ourselves and from those who stand be…
3. *putin / putin2022* (cos 0.90): The outgoing year has brought great and dramatic changes to our country and to the world. It was filled with uncertainty, anxiety and worry.  But our multiethnic nation showed great courage and dignity as it had in every challenging period in Russian history, …
4. *putin / putin2025* (cos 0.89): You have taken upon yourselves the duty of fighting for our native land, for truth and for justice. On this New Year’s Eve, millions of people across Russia, I assure you, are with you: they think of you, share your feelings, and place their hopes in you. We a…
5. *putin / putin2022* (cos 0.89): Citizens of Russia, friends,  The year 2022 is drawing to a close. It was a year of difficult but necessary decisions, of important steps towards Russia's full sovereignty and a powerful consolidation of our society.  It was a year that put many things in thei…

## Cluster 3 — Future, Reform & Technology  (n=40, 16% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 25%), macron 40 (100%; corpus share 30%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 10%), trump 0 (0%; corpus share 19%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Future, Reform & Technology 0.71, Crisis, Threat & Resilience 0.58, Economy & Welfare 0.55

Frequent terms (vs corpus): french, europe, ahead, build, compatriots, stronger, paralympic, olympic, games, pride, growth, live

Representative passages (closest to centroid):

1. *macron / macron2022* (cos 0.89): And like you, I too grow impatient, but without ever giving in to easy solutions or fatalism. And so my wish for us in 2023 is that, through our work and our commitment, we strive to rebuild a France that is stronger and fairer, so that we may pass it on to ou…
2. *macron / macron2022* (cos 0.89): And so many other projects will take shape throughout our country, enabling France both to reduce carbon emissions and to reduce unemployment. In the coming months, in our classrooms, in our hospitals and in our doctors’ practices, you will see the first tangi…
3. *macron / macron2023* (cos 0.89): 2024: a year of determination, choices, renewal and pride. At its heart, a year of hope. Yes, much of our future will be decided this year. So it is up to us to act together. It is up to us to choose rather than endure, to chart the course rather than follow i…
4. *macron / macron2025* (cos 0.87): Let us not give up on reconciling the climate, biodiversity, growth, and independence. Let us not give up on major scientific discoveries, on our love of science and research, or on economic success.  Let us not give up on the place of reading, beauty, and cul…
5. *macron / macron2023* (cos 0.86): And yet I am convinced—and this is not false optimism—that in this context of crises, the best can emerge.  That is why I have never ceased to follow the same course: to act with determination and consistency, for today and for tomorrow. For seven years, from …

## Cluster 4 — Future, Reform & Technology / Social Solidarity & Values  (n=20, 8% of chunks)

Leader distribution: erdogan 1 (5%; corpus share 25%), macron 0 (0%; corpus share 30%), merkel 19 (95%; corpus share 15%), putin 0 (0%; corpus share 10%), trump 0 (0%; corpus share 19%) · mixing entropy 0.12 (1 = perfectly mixed)

Theme profile (mean percentile): Future, Reform & Technology 0.71, Social Solidarity & Values 0.69, Foreign Policy & Geopolitics 0.67

Frequent terms (vs corpus): germany, well, union, work, values, together, change, future, fellow, stand, police, opportunity

Representative passages (closest to centroid):

1. *merkel / merkel1* (cos 0.90): Solidarity, openness, our democracy, and a strong economy that serves the well-being of all: these are the things that, even at the end of a difficult year, give me confidence in our future here in Germany.  None of these values is simply given to us. We will …
2. *merkel / merkel2020* (cos 0.89): I thank the many people who work for the good of our community, both professionally and on a voluntary basis: the police officers, firefighters and all those who stand by their fellow citizens in difficult situations. Together, they form the backbone of our de…
3. *merkel / merkel2* (cos 0.87): Dear Fellow Citizens,  The struggle to find the right answers is part of a vibrant democracy. We are, in the best sense of the word, a society of many voices. At the same time, we are united by the values of our Basic Law: respect for the inviolable dignity of…
4. *merkel / merkel2* (cos 0.86): For this reason, I would particularly like to thank the police officers who are there for us this evening as well, protecting, for example, the many New Year’s Eve celebrations taking place across the country, as well as the soldiers who serve our country here…
5. *merkel / merkel2* (cos 0.86): Both are realities in our country: success and confidence, but also fears and doubts. For me, both are a source of motivation.  For you, dear fellow citizens, have given us politicians the task of addressing the challenges of the future while keeping the needs…

## Cluster 5 — Foreign Policy & Geopolitics / Economy & Welfare  (n=32, 13% of chunks)

Leader distribution: erdogan 32 (100%; corpus share 25%), macron 0 (0%; corpus share 30%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 10%), trump 0 (0%; corpus share 19%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Foreign Policy & Geopolitics 0.57, Economy & Welfare 0.56, Crisis, Threat & Resilience 0.55

Frequent terms (vs corpus): türkiye, goals, century, greet, humanity, calendar, region, feelings, willing, affection, period, economic

Representative passages (closest to centroid):

1. *erdogan / erdogan2023* (cos 0.91): Yes, the 2023 goals were only the beginning; our real rise begins with the Century of Türkiye and with 2024.  We sincerely believe that, with your support, we will bring this struggle to victory as well.  With these feelings, I once again wish for the new cale…
2. *erdogan / erdogan2023* (cos 0.90): God willing, 2024 will be a year in which we leave behind the difficult period that began with the coup attempt, grew with the COVID-19 pandemic, and deepened with the conflicts in our region, and instead focus on our goals.  At a time when global crises conti…
3. *erdogan / erdogan2022* (cos 0.89): On the contrary;  By strengthening our national unity and solidarity…  By expanding our counterterrorism strategy in the direction of eliminating threats at their source…  By burying terrorists in the trenches they had dug…  By crushing the coup plotters…  By …
4. *erdogan / erdogan2025* (cos 0.89): Just as we have done for the past 23 years, with nothing but love for our nation and our homeland in our hearts, we will continue to serve all 86 million of our citizens and work selflessly for the prosperity, peace, and well-being of all of Türkiye.  In 2026 …
5. *erdogan / erdogan2022* (cos 0.88): We regard the infrastructure of democracy and development that we have brought to our country over the past 20 years as the foundation, the beginning, the “Bismillah” of this great leap forward.  In other words, we are only just beginning.  Our aim is to make …

## Parameter grid

 min_cluster_size  min_samples  n_clusters  noise_share  relative_validity  is_primary
                4            2           8        0.396              0.142       False
                4            3           7        0.400              0.121       False
                4            5           2        0.260              0.002       False
                5            2           8        0.396              0.142       False
                5            3           7        0.400              0.121       False
                5            5           2        0.260              0.002       False
                6            2           6        0.324              0.229        True
                6            3           6        0.420              0.119       False
                6            5           2        0.260              0.002       False
                8            2           5        0.348              0.227       False
                8            3           2        0.148              0.004       False
                8            5           2        0.260              0.002       False
               10            2           2        0.112              0.005       False
               10            3           2        0.148              0.004       False
               10            5           2        0.260              0.002       False