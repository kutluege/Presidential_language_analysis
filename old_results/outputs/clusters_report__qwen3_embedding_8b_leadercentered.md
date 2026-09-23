# Exploratory topic discovery — qwen3_embedding_8b_leadercentered

PCA 50 components (63% variance kept) → HDBSCAN(min_cluster_size=6, min_samples=2, euclidean, eom). 9 clusters, 57% of chunks unassigned (noise).

Candidate labels are the top fixed themes of the member chunks (neutral topical descriptions, not interpretations). Cluster membership is exploratory and depends on parameters — see the grid table.

## Cluster -1 — (noise — not assigned)  (n=172, 57% of chunks)

Leader distribution: erdogan 43 (25%; corpus share 28%), macron 60 (35%; corpus share 33%), merkel 29 (17%; corpus share 15%), putin 15 (9%; corpus share 9%), trump 25 (15%; corpus share 16%) · mixing entropy 0.94 (1 = perfectly mixed)

Theme profile (mean percentile): Crisis, Threat & Resilience 0.57, Future, Reform & Technology 0.55, Democracy, Law & Institutions 0.54

Frequent terms (vs corpus): nation, demokratie, agir, dabei, pays, menschen, sais, aujourd, müssen, ensemble, president, ganz

Representative passages (closest to centroid):

1. *macron / macron2023* (cos 0.38): 2024, année de la détermination, de l’efficacité des résultats. Et j’aurai l’occasion dans les semaines qui viennent de vous dire comment notre Nation relèvera ces défis. Mes chers compatriotes, l’action n’est pas une option. L’action est notre devoir pour les…
2. *macron / macron2024* (cos 0.34): A nous donc, collectivement, de faire, car 2025 imposera l’audace et le sens des décisions.  Mes chers compatriotes, les grandes Nations sont celles qui, dans les moments de crise, de doute, savent voir loin, se détacher des polémiques du quotidien pour bâtir …
3. *putin / putin2024* (cos 0.32): Our nation – independent, free, and strong – has tackled successfully the most formidable challenges. As we stand on the brink of a new year, we think about the future. We are confident that everything is going to be all right. We will continue to advance. We …
4. *putin / putin2022* (cos 0.31): The outgoing year has brought great and dramatic changes to our country and to the world. It was filled with uncertainty, anxiety and worry.  But our multiethnic nation showed great courage and dignity as it had in every challenging period in Russian history, …
5. *erdogan / erdogan2025* (cos 0.30): Komisyonun, son düzlükte de uzlaşı ruhuyla hareket etmesi arzumuzdur.  Ülkemizi, 40 yıllık bir musibetten kurtarmayı hedefleyen bu süreç, gündelik siyasetin çıkar hesaplarına kurban edilmemelidir.  Biz de sürecin, bir yol kazası yaşanmadan menzil-i maksuduna v…

## Cluster 0 — Security & Military  (n=11, 4% of chunks)

Leader distribution: erdogan 7 (64%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 3 (27%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 1 (9%; corpus share 16%) · mixing entropy 0.53 (1 = perfectly mixed)

Theme profile (mean percentile): Security & Military 0.68, Foreign Policy & Geopolitics 0.55, Social Solidarity & Values 0.51

Frequent terms (vs corpus): alan, suriye, unseren, unserem, türlü, tatsächlich, hedef, desteği, aracı, istikrar, gereken, ülkemize

Representative passages (closest to centroid):

1. *merkel / merkel1* (cos 0.57): Und – ja – es ist besonders bitter und widerwärtig, wenn Terroranschläge von Menschen begangen werden, die in unserem Land angeblich Schutz suchen. Die genau deshalb die Hilfsbereitschaft unseres Landes erlebt haben und diese nun mit ihren Taten verhöhnen. Wie…
2. *erdogan / erdogan2025* (cos 0.50): Türkiye olarak; Arap, Kürt, Türkmen, Sünni, Şii, Nusayri demeden, Suriye halkının huzur ve güvenliği için yeni yönetime gereken desteği vereceğiz.  Gazze’de, bizim de katkımızla sağlanan ateşkes, İsrail’in tüm ihlallerine rağmen, Gazzeli kardeşlerimizin sağduy…
3. *merkel / merkel1* (cos 0.48): Auch indem wir zum Beispiel mit den Bildern des zerbombten Aleppo in Syrien vor Augen noch einmal sagen dürfen, wie wichtig und richtig es war, dass unser Land auch im zurückliegenden Jahr denjenigen, die tatsächlich unseren Schutz brauchen, geholfen hat, hier…
4. *merkel / merkel1* (cos 0.48): Und in einer festen Entschlossenheit, der Welt des Hasses der Terroristen unsere Mitmenschlichkeit und unseren Zusammenhalt entgegenzusetzen.  Indem wir unserem Leben und unserer Arbeit nachgehen, sagen wir den Terroristen: Sie sind Mörder voller Hass, aber wi…
5. *erdogan / erdogan2022* (cos 0.46): Terör örgütlerinin şehirlerimizi hedef alan eylemlerinin ülkemize yönelik şantaj aracı haline getirildiği günlerden, sınırımızın onlarca, bazen yüzlerce kilometre ötesinde operasyonlar yürütebildiğimiz bir seviyeye geldik.  Ülkemizin neresine gidersek gidelim …

## Cluster 1 — Crisis, Threat & Resilience  (n=7, 2% of chunks)

Leader distribution: erdogan 1 (14%; corpus share 28%), macron 3 (43%; corpus share 33%), merkel 2 (29%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 1 (14%; corpus share 16%) · mixing entropy 0.79 (1 = perfectly mixed)

Theme profile (mean percentile): Crisis, Threat & Resilience 0.67, Economy & Welfare 0.61, Security & Military 0.55

Frequent terms (vs corpus): croissante, sorgen, sagen, divisions, viele, land, nation

Representative passages (closest to centroid):

1. *macron / macron2025* (cos 0.73): Je vois aussi nos propres divisions, nos doutes, la solitude croissante qui existe dans la société, la baisse de notre natalité, l'insécurité, les difficultés de pouvoir d'achat.…
2. *macron / macron2023* (cos 0.66): Marquée encore par la tension géopolitique croissante, les conséquences des dérèglements climatiques sur notre territoire, des actes terroristes sur notre sol. Par des divisions, des gestes de haine, parfois, des violences, à plusieurs occasions, qui fragilise…
3. *merkel / merkel2* (cos 0.65): Die anderen sagen: Es gibt zu viele Menschen, die an diesem Erfolg nicht teilhaben. Die nicht mit dem Tempo unserer Zeit mitkommen. Die sehen, dass es ihre Kinder in die Großstädte zieht und sie allein bleiben, in Gebieten, in denen vom Einkauf bis zum Arztbes…
4. *erdogan / erdogan2023* (cos 0.52): Aziz Milletim…  Elbette bu meşakkatli yolda sürekli yeni sınamalarla, yeni sıkıntılarla, yeni engellerle de karşılaşıyoruz.  Terörle mücadeleden ekonomik tuzaklara kadar pek çok alanda yaşadığımız sorunların temelinde, büyük ve güçlü Türkiye’nin inşasını engel…
5. *merkel / merkel2* (cos 0.51): Liebe Mitbürgerinnen und Mitbürger,  ich grüße Sie herzlich. Ich freue mich über die Gelegenheit, Ihnen auch an diesem Silvestertag einige Gedanken zu sagen, die mich an der Schwelle zum neuen Jahr bewegen.  Aus zahlreichen Gesprächen und Begegnungen in diesem…

## Cluster 2 — National Identity & Unity  (n=6, 2% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 6 (100%; corpus share 33%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): National Identity & Unity 0.58, Future, Reform & Technology 0.48, Democracy, Law & Institutions 0.42

Frequent terms (vs corpus): paralympiques, olympiques, jeux, fierté, héros, promis, fiers, dame, décembre, cathédrale, paris, française

Representative passages (closest to centroid):

1. *macron / macron2024* (cos 0.79): Une France qui rayonne avec ses exploits sportifs, ses émotions, sa générosité, une ville de Paris magnifiée.  Nos Jeux Olympiques et Paralympiques, oui, sont et resteront un moment inoubliable de la vie de la Nation.  En ce mois de décembre 2024, comme nous l…
2. *macron / macron2023* (cos 0.78): Nous serons fiers de nos athlètes, de nos artistes, de nos paysages, de cette fête populaire, permise par des milliers de bénévoles, bâtissant aussi pour notre Nation un héritage sportif. Par notre engagement à tous qui commencera dès demain.  Oui, 2024 sera v…
3. *macron / macron2023* (cos 0.72): 2024 sera une année de fierté de la langue française. Après avoir restauré le château de Villers-Cotterêts et y avoir créé la Cité internationale de la langue française, nous y accueillerons dans quelques mois le monde de la Francophonie.  2024, sera aussi une…
4. *macron / macron2023* (cos 0.66): 2024 sera enfin l’année de nos fiertés françaises. Fierté pour ces milliers de compagnons, d’artisans, d’entrepreneurs qui ont pris part au magnifique chantier pour rebâtir Notre-Dame-de-Paris dont la flèche, s’élance à nouveau vers le ciel et coiffe une cathé…
5. *macron / macron2024* (cos 0.65): Nous nous sommes souvenus, de ceux tombés pour que la France se relève. Nos héros, nos aînés, nos alliés, ceux venus de tous les continents pour libérer la patrie.  Nous avons eu aussi, comme promis il y a un an, des moments de grande fierté. D'abord, nous avo…

## Cluster 3 — Foreign Policy & Geopolitics  (n=15, 5% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 7 (47%; corpus share 33%), merkel 5 (33%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 3 (20%; corpus share 16%) · mixing entropy 0.65 (1 = perfectly mixed)

Theme profile (mean percentile): Foreign Policy & Geopolitics 0.70, Security & Military 0.58, Future, Reform & Technology 0.56

Frequent terms (vs corpus): europe, européens, accélérer, réarmement, investir, continuer, force, zusammenarbeit, souveraineté, schönheit, puissances, internationalen

Representative passages (closest to centroid):

1. *macron / macron2024* (cos 0.64): C’est pourquoi l’Europe ne peut plus déléguer à d’autres puissances sa sécurité et sa défense. En 2025, la France devra continuer d’investir pour son réarmement militaire, pour garantir notre souveraineté, la protection de nos intérêts et la sécurité de nos co…
2. *macron / macron2025* (cos 0.64): Notre indépendance exige que nous continuions d'investir dans nos armées, dans nos forces de sécurité, dans nos services publics et notre économie malgré les difficultés financières. Depuis 10 ans, j'ai beaucoup plaidé et nous avons beaucoup fait pour renforce…
3. *macron / macron2023* (cos 0.57): Nous devons donc continuer ce réarmement de la Nation face au dérèglement du monde. Car la force de caractère est la vertu des temps difficiles. 2024 sera aussi une année de choix décisifs.  Nous aurons à faire le choix d’une Europe plus forte plus souveraine,…
4. *macron / macron2023* (cos 0.57): Vous aurez au mois de juin prochain à vous prononcer sur la poursuite de ce réarmement de notre souveraineté européenne face aux périls : arrêter la Russie et soutenir les Ukrainiens ou céder aux puissances autoritaires en Ukraine ; continuer l’Europe ou la bl…
5. *macron / macron2025* (cos 0.53): Protégeons aussi notre Europe industrielle et agricole, en instaurant des règles de commerce loyales, justes vis-à-vis du reste du monde. Osons être une vraie puissance qui assume une préférence européenne pour ses emplois, ses entreprises. Bâtissons une Europ…

## Cluster 4 — Democracy, Law & Institutions  (n=11, 4% of chunks)

Leader distribution: erdogan 11 (100%; corpus share 28%), macron 0 (0%; corpus share 33%), merkel 0 (0%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 0 (0%; corpus share 16%) · mixing entropy -0.00 (1 = perfectly mixed)

Theme profile (mean percentile): Democracy, Law & Institutions 0.91, National Identity & Unity 0.51, Foreign Policy & Geopolitics 0.50

Frequent terms (vs corpus): cumhurbaşkanlığı, sistemine, sistemi, yönetim, millet, üzerinde, vardır, sisteminin, kardeşlerim, ülke, yürütme, sisteme

Representative passages (closest to centroid):

1. *erdogan / erdogan1* (cos 0.72): Bütün bu tecrübeleri yaşanmış Olduğumuz bu olayları tarihi okumaları bir araya getirdiğimizde ülkemizin Yeni anayasaya ve onunla birlikte yeni bir yönetim sistemine olan ihtiyacı gün gibi ortaya çıkıyor kardeşlerim görüldüğü gibi Bugün üzerinde konuştuğumuz Cu…
2. *erdogan / erdogan1* (cos 0.72): Cumhurbaşkanlığı sisteminin özü yönetimin doğrudan millete veriliyor olmasıdır.  Yürütme görevini ifa edecek olan Cumhurbaşkanı gücünü aldığı Millete karşı sorumlu olacağı için attığı her adımda gözü kamuoyunun üzerinde olmak zorundadır.  Biz ne dedik Bizimki …
3. *erdogan / erdogan1* (cos 0.68): Mesele ülke ve millet olarak geçmişte yaşadığımız tecrübeler ışığında kendimize çok daha güçlü çok daha dirençli hedeflerimizi gerçekleştirmeye çok daha uygun bir yönetim sistemi kurma çabasıdır.  Cumhurbaşkanlığı sisteminin en büyük güvencesi gerçek anlamda d…
4. *erdogan / erdogan1* (cos 0.65): Esasen Bugün üzerinde konuştuğumuz Cumhurbaşkanlığı sistemi konusu öyle bir anda bir günde bir yılda ortaya çıkmış değildir gerisinde işte böylesine Derin ve düşündürücü bir arka plan vardır.  Tartıştığımız sistem Türkiye'nin ve Türk milletinin Asırlardır deva…
5. *erdogan / erdogan1* (cos 0.60): Dolayısıyla anayasa değişikliğiyle konuyu şahsileştirmek yönetimi bir sisteme bağlıyoruz.  Kardeşlerim ruh olmayınca beden cesettir Bu konuda da milletimize işin ruhunu özünü esasını anlatmazsa tek başına anayasa değişikliği hükümleri kuru hukuki ifadelerden i…

## Cluster 5 — National Identity & Unity / Social Solidarity & Values  (n=41, 13% of chunks)

Leader distribution: erdogan 15 (37%; corpus share 28%), macron 7 (17%; corpus share 33%), merkel 4 (10%; corpus share 15%), putin 9 (22%; corpus share 9%), trump 6 (15%; corpus share 16%) · mixing entropy 0.94 (1 = perfectly mixed)

Theme profile (mean percentile): National Identity & Unity 0.71, Social Solidarity & Values 0.70, Security & Military 0.50

Frequent terms (vs corpus): selamlıyorum, yılının, insanlık, diliyorum, olmasını, always, happy, vesile, takvim, sağlıcakla, muhabbetle, kalın

Representative passages (closest to centroid):

1. *erdogan / erdogan2024* (cos 0.72): Aziz Milletim…  Hepinizi en kalbi duygularımla, muhabbetle selamlıyorum.  Bugün 2024’e veda ediyor; yeni umut, beklenti ve hayallerle 2025 senesini karşılıyoruz.  Öncelikle yeni miladi yılın ülkemiz, milletimiz, gönül coğrafyamız ve tüm insanlık için hayırlara…
2. *erdogan / erdogan2023* (cos 0.69): Aziz Milletim,  Hepinizi en kalbi duygularımla, muhabbetle selamlıyorum.  Bu gece 2023 yılını tamamlıyor, 2024 yılına adım atıyoruz.  Yeni takvim yılının, ülkemiz, milletimiz ve tüm insanlık için hayırlara vesile olmasını diliyorum.…
3. *erdogan / erdogan2022* (cos 0.65): Aziz Milletim,  Hepinizi en kalbi duygularımla, muhabbetle selamlıyorum.  Bugün sadece bir yılı bitirip, yeni bir yılı karşılamakla kalmıyor, aynı zamanda Cumhuriyetimizin ilk yüzyılını geride bırakıp yeni yüzyılına adım atacağımız bir döneme giriyoruz.…
4. *erdogan / erdogan2025* (cos 0.63): Aziz Milletim;  Sizleri en kalbî duygularımla, muhabbetle, hürmetle selamlıyorum.  Bugün, 2025’le vedalaşıyor; yepyeni bir heyecanla, yeni ümit ve hedeflerle 2026’ya “merhaba” demeye hazırlanıyoruz.…
5. *erdogan / erdogan2025* (cos 0.62): Rabbim yar ve yardımcımız olsun, diyorum.  Türkiye Yüzyılı ülkümüze destek olan herkese teşekkür ediyorum.  Bu düşüncelerle yeni miladi yılınızı tebrik ediyor; 2026’nın ülkemiz, milletimiz, bölgemiz ve tüm insanlık için hayırlara vesile olmasını diliyorum.  Si…

## Cluster 6 — Social Solidarity & Values  (n=7, 2% of chunks)

Leader distribution: erdogan 2 (29%; corpus share 28%), macron 1 (14%; corpus share 33%), merkel 1 (14%; corpus share 15%), putin 1 (14%; corpus share 9%), trump 2 (29%; corpus share 16%) · mixing entropy 0.96 (1 = perfectly mixed)

Theme profile (mean percentile): Social Solidarity & Values 0.74, Security & Military 0.54, Crisis, Threat & Resilience 0.51

Frequent terms (vs corpus): entire, gratitude, administration, thank, service, military, everyone, people, support, america, country

Representative passages (closest to centroid):

1. *erdogan / erdogan2025* (cos 0.70): Yeni ev ve iş yerleri, depremzedelerimize hayırlı-uğurlu olsun, diyorum.  6 Şubat’tan bu yana kışın soğuğuna, yazın sıcağına aldırmadan 7 gün 24 saat esasıyla şantiyelerde çalışan tüm kardeşlerime, konutların inşasında emeği geçen tüm kurumlarımıza ve hayırsev…
2. *putin / putin2022* (cos 0.65): Comrades,  thank you for your valiant service. Our entire vast country is proud of your fortitude, endurance and courage. Millions of people are with you in their hearts and souls, and will be raising a toast to you at their New Year's table.  Many thanks to e…
3. *trump / trump1* (cos 0.64): I also want to thank Vice President Mike Pence, his wonderful wife Karen, and the entire Pence family.  Thank you as well to my Chief of Staff, Mark Meadows; the dedicated members of the White House Staff and the Cabinet; and all the incredible people across o…
4. *merkel / merkel2020* (cos 0.60): Unsere Sicherheit und unser Wohlstand hängen wesentlich davon ab, dass es auch in unserer Nachbarschaft sicher wird und wirtschaftlich aufwärts geht. Deshalb danke ich heute Abend sowohl unseren Soldatinnen und Soldaten, den Polizistinnen und Polizisten als au…
5. *trump / trump1* (cos 0.53): This week, we inaugurate a new administration and pray for its success in keeping America safe and prosperous. We extend our best wishes, and we also want them to have luck — a very important word.  I’d like to begin by thanking just a few of the amazing peopl…

## Cluster 7 — Economy & Welfare  (n=21, 7% of chunks)

Leader distribution: erdogan 6 (29%; corpus share 28%), macron 7 (33%; corpus share 33%), merkel 1 (5%; corpus share 15%), putin 1 (5%; corpus share 9%), trump 6 (29%; corpus share 16%) · mixing entropy 0.85 (1 = perfectly mixed)

Theme profile (mean percentile): Economy & Welfare 0.84, Crisis, Threat & Resilience 0.40, Future, Reform & Technology 0.35

Frequent terms (vs corpus): ekonomi, economy, emplois, uyguladığımız, sahibi, pandemic, numbers, électricité, prix, passed, énergie, créer

Representative passages (closest to centroid):

1. *erdogan / erdogan2024* (cos 0.62): Seçimlere ve bölgemizde patlak veren yeni krizlere rağmen, kararlılıkla uyguladığımız ekonomi programımızın meyvelerini toplamaya başladık.  İstihdamda, ihracatta, üretimde, turizmde, savunma sanayiinde ve diğer alanlarda çok önemli başarılara imza attık.…
2. *macron / macron2022* (cos 0.61): La solidarité nationale, financée par les contribuables français, a permis d’atténuer la hausse des prix de l’énergie pour chacun, de sauvegarder nos entreprises, de protéger particulièrement les revenus des plus modestes d’entre nous. Et grâce à notre action …
3. *erdogan / erdogan2025* (cos 0.60): Kararlılıkla uyguladığımız ekonomi programının olumlu sonuçlarına geniş bir yelpazede şahitlik ediyoruz.  Dez-enflasyon süreci devam ederken, Merkez Bankamızın rezervleri güçleniyor; üretim, yatırım, istihdam ve ihracatta vites yükseltiyoruz.…
4. *trump / trump1* (cos 0.58): We also unlocked our energy resources and became the world’s number-one producer of oil and natural gas by far. Powered by these policies, we built the greatest economy in the history of the world. We reignited America’s job creation and achieved record-low un…
5. *macron / macron2023* (cos 0.56): Et nous avons continué cette année de créer des emplois, tout en réduisant encore plus rapidement nos émissions de gaz à effet de serre, conformément à nos engagements. Ceci prouve que vous êtes au rendez-vous de la mobilisation.  Grâce à ce réarmement économi…

## Cluster 8 — Economy & Welfare / Future, Reform & Technology  (n=13, 4% of chunks)

Leader distribution: erdogan 0 (0%; corpus share 28%), macron 8 (62%; corpus share 33%), merkel 1 (8%; corpus share 15%), putin 0 (0%; corpus share 9%), trump 4 (31%; corpus share 16%) · mixing entropy 0.53 (1 = perfectly mixed)

Theme profile (mean percentile): Economy & Welfare 0.79, Future, Reform & Technology 0.76, Democracy, Law & Institutions 0.74

Frequent terms (vs corpus): égalité, social, government, retraite, orientation, métiers, idea, forgotten, carrières, améliorer, everyone, enfants

Representative passages (closest to centroid):

1. *macron / macron2022* (cos 0.62): C’est par notre travail et notre engagement que nous bâtirons une société plus juste. Société plus juste c’est d’abord une société où l’égalité entre les femmes et les hommes est effective, et là aussi, ce qui est la grande cause de mes deux quinquennats, cont…
2. *macron / macron2022* (cos 0.59): C’est par notre travail, notre engagement que nous devons refonder nos grands services publics pour qu’ils assurent pleinement notre idéal d’égalité. Avec le Conseil National de la Refondation, nous avons entrepris de renouer le contrat entre les générations e…
3. *macron / macron2022* (cos 0.50): Mais c’est cela qui nous permettra d’équilibrer le financement de notre retraite, dans notre pays, et c’est une chance, où l’on vit plus longtemps, d’améliorer la retraite minimale pour toutes celles et ceux qui ont travaillé pour avoir leurs trimestres, et de…
4. *macron / macron2022* (cos 0.47): En réindustrialisant plus vite et plus fort notre pays, pour offrir de nouveaux emplois et des carrières d’avenir. Car la principale injustice de notre pays demeure le déterminisme familial, la trop faible mobilité sociale. Et la réponse se trouve dans l’école…
5. *merkel / merkel3* (cos 0.46): Um Arbeitsplätze, Wohlstand und unsere Lebensgrundlagen zu sichern, geht die Bundesregierung konsequent die nächsten Schritte beim Strukturwandel von traditionellen zu neuen Technologien und setzt ihre Strategie für den digitalen Fortschritt um.  Mit unserer A…

## Parameter grid

 min_cluster_size  min_samples  n_clusters  noise_share  relative_validity  is_primary
                4            2          17        0.569              0.103       False
                4            3           8        0.674              0.047       False
                4            5           4        0.803              0.028       False
                5            2          12        0.618              0.059       False
                5            3           8        0.674              0.047       False
                5            5           4        0.803              0.028       False
                6            2           9        0.566              0.066        True
                6            3           6        0.684              0.066       False
                6            5           4        0.803              0.028       False
                8            2           6        0.632              0.130       False
                8            3           5        0.664              0.066       False
                8            5           3        0.822              0.017       False
               10            2           5        0.569              0.024       False
               10            3           5        0.664              0.066       False
               10            5           2        0.852              0.000       False