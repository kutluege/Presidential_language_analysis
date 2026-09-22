# Exploratory topic discovery — qwen3_embedding_8b

PCA 50 components (69% variance kept) → HDBSCAN(min_cluster_size=6, min_samples=2, euclidean, eom). 6 clusters, 19% of chunks unassigned (noise).

Candidate labels are the top fixed themes of the member chunks (neutral topical descriptions, not interpretations). Cluster membership is exploratory and depends on parameters — see the grid table.

## Cluster -1 — (noise — not assigned)  (n=58, 19% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 21 (36%; corpus share 33%), merkel 29 (50%; corpus share 15%), putin 3 (5%; corpus share 9%), trump 5 (9%; corpus share 16%) · mixing entropy 0.67 (1 = perfectly mixed)

Theme profile (mean percentile): Future, Reform & Technology 0.43, Economy & Welfare 0.38, Crisis, Threat & Resilience 0.38

Frequent terms (vs corpus): menschen, unserem, mehr, aura, sagen, unserer, familien, land, wünsche, neues, lange, gerade

Representative passages (closest to centroid):

1. *merkel / merkel1* (cos 0.71): Dafür braucht es einen offenen Blick auf die Welt und Selbstvertrauen – in uns und unser Land.  Zusammenhalt, Offenheit, unsere Demokratie und eine starke Wirtschaft, die dem Wohl aller dient: Das ist es, was mich für unsere Zukunft hier in Deutschland auch am…
2. *merkel / merkel2* (cos 0.66): Beides sind Realitäten in unserem Land: der Erfolg und die Zuversicht, aber auch die Ängste und die Zweifel. Für mich ist beides Ansporn.  Denn Sie, liebe Mitbürgerinnen und Mitbürger, haben uns Politikern den Auftrag gegeben, uns um die Herausforderungen der …
3. *merkel / merkel2020* (cos 0.65): Liebe Mitbürgerinnen und Mitbürger,  heute Abend stehen wir nicht nur am Beginn eines neuen Jahres, sondern auch eines neuen Jahrzehnts. Ich bin überzeugt: Wir haben gute Gründe, zuversichtlich zu sein, dass die in wenigen Stunden beginnenden 20er Jahre des 21…
4. *merkel / merkel1* (cos 0.65): Auch indem wir zum Beispiel mit den Bildern des zerbombten Aleppo in Syrien vor Augen noch einmal sagen dürfen, wie wichtig und richtig es war, dass unser Land auch im zurückliegenden Jahr denjenigen, die tatsächlich unseren Schutz brauchen, geholfen hat, hier…
5. *merkel / merkel2* (cos 0.64): Liebe Mitbürgerinnen und Mitbürger,  ich grüße Sie herzlich. Ich freue mich über die Gelegenheit, Ihnen auch an diesem Silvestertag einige Gedanken zu sagen, die mich an der Schwelle zum neuen Jahr bewegen.  Aus zahlreichen Gesprächen und Begegnungen in diesem…

## Cluster 0 — Foreign Policy & Geopolitics / Crisis, Threat & Resilience  (n=85, 28% of chunks)

Leader distribution: erdogan 85 (100%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Foreign Policy & Geopolitics 0.56, Crisis, Threat & Resilience 0.54, National Identity & Unity 0.54

Frequent terms (vs corpus): türkiye, büyük, millet, ediyorum, devam, ülke, ekonomik, aziz, ülkemizin, önemli, yılda, siyasi

Representative passages (closest to centroid):

1. *erdogan / erdogan2024* (cos 0.86): Doğru yoldayız; Allah’ın izniyle hedeflerimize de ulaşacağız.  Sizlerden sadece biraz daha sabır, metanet ve anlayış istiyoruz.  Aziz Milletim…  2024 senesinin son haftaları, köklü tarihi, beşeri ve komşuluk ilişkilerimizin bulunduğu Suriye’de yeni bir dönemin…
2. *erdogan / erdogan2023* (cos 0.82): İnşallah 2024, darbe girişimiyle başlayıp kKovid-19 salgınıyla büyüyen, bölgemizdeki çatışmalarla derinleşen sıkıntılı dönemden kurtulup, hedeflerimize kilitlendiğimiz bir yıl olacaktır.  Küresel krizlerin artarak sürdüğü bir dönemde, biz farkımızı bir kez dah…
3. *erdogan / erdogan2024* (cos 0.82): Ama gerektiğinde, devletimizin kadife eldiven içindeki demir yumruğunu devreye almaktan da çekinmeyeceğiz.  Bu çerçevede 2025 yılında milletimize inşallah yeni müjdeler vermeyi ümit ve arzu ediyoruz.  Rabbim yar ve yardımcımız olsun.…
4. *erdogan / erdogan2022* (cos 0.81): Yani, yeni başlıyoruz.  Amacımız, bu başlangıcı en iyi ve etkin şekilde yaparak, gençlerimize Türkiye Yüzyılını, hedeflerimize, hayallerimize, medeniyet ve tarih mirasımıza uygun şekilde başarıya ulaştırabilecekleri bir ülke bırakmaktır.  Bu duygularla geride …
5. *erdogan / erdogan2023* (cos 0.81): Cumhuriyetimizin ilk asrını bitirip, Türkiye Yüzyılı dediğimiz yeni asrına ayak bastığı bir dönemde, daha büyük hedeflere yönelirken, azmimizi ve gayretimizi sürekli perçinliyoruz.  Zalimin zulmünün ilanihaye sürüp gitmeyeceğine inanıyoruz.…

## Cluster 1 — Future, Reform & Technology / Economy & Welfare  (n=6, 2% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 6 (100%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Future, Reform & Technology 0.91, Economy & Welfare 0.89, Social Solidarity & Values 0.51

Frequent terms (vs corpus): fortschritt, bildung, digitalen, neue, menschen, arbeit, zukunft, mehr, müssen, zugang, wirtschaftlicher, unterstützen

Representative passages (closest to centroid):

1. *merkel / merkel2020* (cos 0.84): Im nächsten Jahr wird Deutschland seit 30 Jahren in Frieden und Freiheit wiedervereint sein. In diesen 30 Jahren haben wir Großartiges geschafft. So hatten zum Beispiel noch nie so viele Menschen Arbeit wie heute. Dennoch bleibt auch im nächsten Jahrzehnt noch…
2. *merkel / merkel1* (cos 0.82): Noch nie hatten so viele Menschen Arbeit wie heute. Unsere Unternehmen stehen überwiegend gut da. Unser wirtschaftlicher Erfolg gibt uns die Möglichkeit, unser Sozialsystem zu stärken und all denen zu helfen, die Hilfe brauchen. Ab morgen treten zum Beispiel w…
3. *merkel / merkel3* (cos 0.81): Um Arbeitsplätze, Wohlstand und unsere Lebensgrundlagen zu sichern, geht die Bundesregierung konsequent die nächsten Schritte beim Strukturwandel von traditionellen zu neuen Technologien und setzt ihre Strategie für den digitalen Fortschritt um.  Mit unserer A…
4. *merkel / merkel2* (cos 0.81): Das bedeutet zum einen:  bestehende Arbeitsplätze zu sichern wie auch ganz neue Jobs für die Zukunft zu schaffen, die Unternehmen noch mehr bei Forschung und Entwicklung in innovative Technologien zu unterstützen den Staat zum digitalen Vorreiter zu machen, un…
5. *merkel / merkel2* (cos 0.78): Denn die Welt wartet nicht auf uns. Wir müssen jetzt die Voraussetzungen dafür schaffen, dass es Deutschland auch in 10, 15 Jahren gut geht. Und wirklich gut geht es Deutschland, wenn der Erfolg allen Menschen dient und unser Leben verbessert und bereichert.  …

## Cluster 2 — Social Solidarity & Values / Democracy, Law & Institutions  (n=11, 4% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 11 (100%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Social Solidarity & Values 0.75, Democracy, Law & Institutions 0.71, Foreign Policy & Geopolitics 0.68

Frequent terms (vs corpus): europa, demokratie, danke, unserer, polizisten, sicherheit, dazu, soldatinnen, soldaten, polizistinnen, dienst, beitragen

Representative passages (closest to centroid):

1. *merkel / merkel2020* (cos 0.87): Ich danke den vielen, die sich für unser Gemeinwesen einsetzen, haupt- und ehrenamtlich: den Polizisten, Feuerwehrleuten und all denen, die ihren Mitmenschen in schweren Situationen beistehen. Sie alle bilden das Rückgrat unserer Demokratie.  In den vergangene…
2. *merkel / merkel2* (cos 0.84): Ich danke deshalb an dieser Stelle ganz besonders den Polizistinnen und Polizisten, die auch heute Abend für uns da sind und zum Beispiel die vielen Silvesterfeiern im Land schützen, wie auch den Soldatinnen und Soldaten, die hierzulande oder in den Auslandsei…
3. *merkel / merkel3* (cos 0.81): Im Mai können Sie durch Ihre Teilnahme an der Europawahl dazu beitragen, dass die Europäische Union auch in Zukunft ein Projekt von Frieden, Wohlstand und Sicherheit sein wird.  Liebe Mitbürgerinnen und Mitbürger, Wohlstand, Sicherheit und Frieden, dafür müsse…
4. *merkel / merkel2* (cos 0.79): Deutschland und Frankreich wollen gemeinsam dafür arbeiten, dass das gelingt, und so dazu beitragen, Europa für die Zukunft fit zu machen.  Liebe Mitbürgerinnen und Mitbürger, das Ringen um richtige Antworten gehört zu einer lebendigen Demokratie. Wir sind – i…
5. *merkel / merkel1* (cos 0.76): Wo Europa – wie im globalen Wettbewerb, beim Schutz unserer Außengrenzen oder bei der Migration – als Ganzes herausgefordert wird, muss es auch als Ganzes die Antwort finden – egal wie mühsam und zäh das ist. Und wir Deutschen haben jedes Interesse daran, eine…

## Cluster 3 — Future, Reform & Technology  (n=78, 26% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 78 (100%; corpus share 33%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Future, Reform & Technology 0.73, Economy & Welfare 0.66, Democracy, Law & Institutions 0.62

Frequent terms (vs corpus): avons, pays, europe, ceux, nation, travail, sécurité, engagement, enfants, bâtir, monde, français

Representative passages (closest to centroid):

1. *macron / macron2022* (cos 0.84): Et comme vous, je m’impatiente, mais sans jamais céder à la facilité ou à la fatalité. Aussi, je nous souhaite pour 2023 par notre travail et notre engagement d’œuvrer à refonder une France plus forte, plus juste, pour la transmettre à nos enfants.  C’est par …
2. *macron / macron2023* (cos 0.81): Et notre Histoire toute entière nous enseigne que la volonté de quelques-uns peut abattre toutes les fatalités. Alors à nous de faire, oui, d’agir ensemble, de continuer de dépasser les clivages, les corporatismes, car il y a en notre peuple les ressorts profo…
3. *macron / macron2022* (cos 0.80): Dans les prochains mois, dans nos salles de classe, dans nos hôpitaux, comme chez nos médecins en ville, vous verrez les premiers changements tangibles de la rénovation de notre école et de notre santé.  Pour tout cela, je forme pour nous tous, des vœux d’unit…
4. *macron / macron2024* (cos 0.79): C’est pour cela qu’en 2025 nous continuerons de décider et je vous demanderai aussi de trancher certains de ces sujets déterminants. Car chacun d’entre vous aura un rôle à jouer. Chacun d’entre vous sera nécessaire pour réussir ce projet que je viens rapidemen…
5. *macron / macron2025* (cos 0.79): Notre unité exige de reconnaître que chaque Française, chaque Français a un rôle à jouer pour relever les défis qui sont devant nous, que chacun d'entre nous est nécessaire et doit être encouragé et reconnu. Oui, dans notre vie de chaque jour, au fond, je nous…

## Cluster 4 — National Identity & Unity / Foreign Policy & Geopolitics  (n=43, 14% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 43 (100%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): National Identity & Unity 0.65, Foreign Policy & Geopolitics 0.63, Economy & Welfare 0.62

Frequent terms (vs corpus): america, country, american, world, people, citizens, americans, nation, across, president, thank, first

Representative passages (closest to centroid):

1. *trump / trump3* (cos 0.83): So to all Americans in every city near and far, small and large, from mountain to mountain, from ocean to ocean, hear these words:  You will never, never be ignored again.  Your voice, your hopes, and your dreams will define our American destiny.  And your cou…
2. *trump / trump1* (cos 0.81): This is a republic of proud citizens who are united by our common conviction that America is the greatest nation in all of history. We are, and must always be, a land of hope, of light, and of glory to all the world. This is the precious inheritance that we mu…
3. *trump / trump1* (cos 0.81): My fellow Americans: Four years ago, we launched a great national effort to rebuild our country, to renew its spirit, and to restore the allegiance of this government to its citizens. In short, we embarked on a mission to make America great again — for all Ame…
4. *trump / trump3* (cos 0.80): We assembled here today are issuing a new decree to be heard in every city, in every foreign capital, and in every hall of power.  From this day forward, a new vision will govern our land.  From this day forward, it's going to be only America first. America fi…
5. *trump / trump3* (cos 0.80): Chief Justice Roberts, President Carter, President Clinton, President Bush, President Obama, fellow Americans, and people of the world, thank you.  We, the citizens of America, are now joined in a great national effort to rebuild our country and restore its pr…

## Cluster 5 — Social Solidarity & Values / National Identity & Unity  (n=23, 8% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 0 (0%; corpus share 15%), putin 23 (100%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Social Solidarity & Values 0.71, National Identity & Unity 0.68, Security & Military 0.57

Frequent terms (vs corpus): russia, friends, future, love, motherland, happy, people, always, sincere, russian, support, wish

Representative passages (closest to centroid):

1. *putin / putin2025* (cos 0.88): You have taken upon yourselves the duty of fighting for our native land, for truth and for justice. On this New Year’s Eve, millions of people across Russia, I assure you, are with you: they think of you, share your feelings, and place their hopes in you. We a…
2. *putin / putin2023* (cos 0.86): This kind of generational kinship and love of one’s home fosters devotion to the Motherland.  I would like to convey my very best wishes for the new year to all Russian families. After all, the history of our huge, wonderful, and beloved Motherland is made up …
3. *putin / putin2024* (cos 0.86): Our nation – independent, free, and strong – has tackled successfully the most formidable challenges. As we stand on the brink of a new year, we think about the future. We are confident that everything is going to be all right. We will continue to advance. We …
4. *putin / putin2022* (cos 0.86): As we see the New Year in, everyone strives to give joy to their loved ones, to show them attention and warmth, to give them presents they have been dreaming of, to see the delight in children’s eyes and parents’ touching gratitude for our attention. The older…
5. *putin / putin2025* (cos 0.86): Citizens of Russia, friends,  At this moment, as we stand on the threshold of the New Year, we all feel the passage of time. Before us lies the future, and what it holds largely depends on us.  We draw strength from within ourselves and from those who stand be…

## Parameter grid

 min_cluster_size  min_samples  n_clusters  noise_share  relative_validity  is_primary
                4            2          11        0.263              0.034       False
                4            3           2        0.049              0.006       False
                4            5           2        0.122              0.003       False
                5            2          10        0.250              0.034       False
                5            3           2        0.049              0.006       False
                5            5           2        0.122              0.003       False
                6            2           6        0.191              0.019        True
                6            3           2        0.049              0.006       False
                6            5           2        0.122              0.003       False
                8            2           5        0.211              0.019       False
                8            3           2        0.049              0.006       False
                8            5           2        0.122              0.003       False
               10            2           5        0.211              0.019       False
               10            3           2        0.049              0.006       False
               10            5           2        0.122              0.003       False