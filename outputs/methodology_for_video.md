# Video için metodoloji notları (Türkçe) — 2. tur, İngilizce derlem

Kamera karşısında bir yapay zekâ mühendisi gibi anlatmak için: kısa, doğru, abartısız.
Derlem: 20 konuşma, 23,905 temizlenmiş İngilizce kelime, 250 parça.
Birincil model: KaLM-Embedding-Gemma3-12B-2511 (11.8 milyar parametre, 3840 boyut). Sağlamlık modeli: Qwen3-Embedding-8B.

## Neden her şeyi İngilizceye çevirdik?
Birinci turda her lider kendi dilindeydi ve model önce dili gördü: bir parçanın komşularının %69–100'ü aynı liderden, yani aynı dildendi;
Türkçe konuşan Erdoğan uzayın en uzak köşesindeydi. Dil ile lideri ayıramıyorduk. Çeviri bu sinyali kaldırıyor.
Bedeli var: Erdoğan, Macron, Merkel, Putin artık çevirmenin cümleleriyle konuşuyor. Stil ölçümlerinde bunu her seferinde söylüyoruz.
Birinci turun tüm sonuçları old_results/ klasöründe; aynı modelle (Qwen3) iki derlemi karşılaştıran "dil etkisi" grafiği buradan geliyor.

## Embedding nedir?
Bir metin parçasını anlamını temsil eden uzun bir sayı listesine (vektöre) çevirmek. Burada her parça 3840 sayı.
Anlamca yakın parçalar uzayda yakın düşer. Modelin "anlam" dediği şey eğitim verisinden öğrendiği istatistiksel örüntüler; konu, tür ve üslup hep bu vektörün içinde.

## Yeni model neden bu?
KaLM-Embedding-Gemma3-12B, açık ağırlıklı modeller arasında MTEB çok dilli sıralamasının en üstünde ve bf16 hassasiyetle bir RTX 5090'a sığan en büyük model (≈23 GB).
Daha yüksek puanlı 27 milyarlık bir model var ama 52 GB istiyor. Sağlamlık için aynı parçaları Qwen3-Embedding-8B ile de gömdük; iki model aynı şeyi söylüyorsa bulgu sağlam.

## Chunk (parça) neden kullandık?
Bütün konuşmayı tek vektöre sıkıştırsak konular birbirine karışır. Konuşmaları doğal paragraflardan başlayarak 80–180 token'lık
parçalara ayırdık (medyan 107 token, örtüşme yok). Böylece temaların sıklığını ve derlemlerin birbirine karışmasını ölçebiliyoruz.

## Cosine similarity nedir?
İki vektörün arasındaki açının kosinüsü: 1 aynı yön, 0 ilgisiz. Vektörler birim uzunlukta; yön karşılaştırılıyor, uzunluk değil.
Mutlak değerler modele özgüdür; iki modeli karşılaştırırken sıralamaya bakıyoruz.

## Leader centroid nasıl oluşturuldu?
(1) parça vektörlerini normalize et, (2) konuşmanın parçalarının ortalaması → normalize → konuşma merkezi,
(3) liderin konuşma merkezlerinin ortalaması → normalize → lider merkezi. Her konuşma eşit ağırlıkta.

## Retorik boyutlar ve "sıralama" ne demek?
Yedi boyut (çatışma-tehdit, iş birliği-dayanışma, geçmişe yönelim, geleceğe yönelim, biz-onlar, teşekkür-takdir, vaat-taahhüt) için birer tanım yazdık,
aynı modelle gömdük ve her parçanın tanıma benzerliğini ölçtük. Değerleri derlem yüzdeliği olarak veriyoruz (0.5 = derlem ortalaması).
"Sıralama", ölçülen değerlere göre sıralamak demek; yanında %95 güven aralığı var. Aralıklar örtüşüyorsa fark yok diyoruz. Kimseye "en sert" ya da "en yumuşak" etiketi yok.

## Duygu tonu nasıl ölçüldü?
Embedding'den bağımsız iki sınıflandırıcı: GoEmotions (28 duygu etiketi, çoklu etiket) ve üç sınıflı bir duygu değeri modeli.
Etiketleri ailelere topladık (olumlu-birleştirici, korku-kayıp, düşmanlık). Uyarı: bu modeller Reddit ve Twitter metniyle eğitildi; siyasi konuşma alan dışıdır.

## Stil benzerliği nasıl hesaplandı?
Her konuşma için 11 boyutlu bir stil vektörü (7 retorik boyut + 3 duygu ailesi + duygu değeri), tüm konuşmalar üzerinden z-puanı,
lider = konuşmalarının ortalaması, aradaki Öklid uzaklığı ve kosinüs. Dendrogram bu uzaklıklardan çiziliyor.
Ayrıca içerik benzerliği (embedding merkezleri) ile stil benzerliğini karşılaştırıyoruz: aynı şeyleri söyleyenler aynı şekilde mi söylüyor?

## Neden UMAP sonucu gerçek mesafe olarak kullanılmıyor?
UMAP 3840 boyutu 2'ye indirir; yerel komşulukları korur, küresel mesafeleri bozar. Ekrandaki uzaklık gerçek uzaklık değil.
"2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space."
Parametreler: n_neighbors=15, min_dist=0.1, metric=cosine, seed=42.

## Neden konuşma uzunluğunu normalize ettik?
En uzun konuşma 2.900 kelime, en kısası 450. Parça sayısı üzerinden ortalama alsak uzun konuşmalar kısaları ezerdi. Parça → konuşma → lider hiyerarşisinde her konuşma bir oy.

## Neden speech-level bootstrap yaptık?
Lider başına 3–5 konuşma var. Konuşmaları yerine koyarak 2000 kez yeniden örnekledik ve her sayıyı yeniden hesapladık.
Birim parça değil konuşma; çünkü aynı konuşmanın parçaları bağımsız değil. Güven aralığı sıfırı ya da komşusunu kapsıyorsa "fark var" demiyoruz.

## Söylememiz gereken şey
Tüm sayılar toplanan konuşma dosyalarını (İngilizce metinleriyle) tarif eder. İdeoloji, siyasi kalite, kişilik, yeterlilik ya da ahlak hakkında hiçbir şey söylemez.
