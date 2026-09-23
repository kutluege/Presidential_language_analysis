# Video için metodoloji notları (Türkçe)

Bu metin, kamera karşısında bir yapay zekâ mühendisi gibi anlatmak için yazıldı: kısa, doğru, abartısız.
Derlem: 20 konuşma, 21,117 temizlenmiş kelime, 304 parça. Birincil model: Qwen/Qwen3-Embedding-8B. Sağlamlık modeli: BAAI/bge-m3.

## Embedding nedir?
Bir metin parçasını, anlamını temsil eden uzun bir sayı listesine (vektöre) dönüştürmek. Burada her parça 4096 sayıdan oluşan bir vektör oluyor.
Anlamca yakın parçalar bu uzayda birbirine yakın düşüyor. Modelin "anlam" dediği şey, eğitim verisinden öğrendiği istatistiksel örüntüler; dil, tür ve konu hep bu vektörün içinde.

## Chunk (parça) neden kullandık?
Bütün bir konuşmayı tek vektöre sıkıştırsak, konuşmanın içindeki farklı konular birbirine karışır ve ortalama bir "bulanık" nokta elde ederiz.
Bunun yerine konuşmaları doğal paragraflardan başlayarak yaklaşık 80–180 token'lık parçalara ayırdık (medyan 110 token), örtüşme yok.
Böylece "hangi temalar ne sıklıkla geçiyor" ve "iki derlemin parçaları birbirine karışıyor mu" sorularını cevaplayabiliyoruz.

## Cosine similarity nedir?
İki vektörün arasındaki açının kosinüsü: 1 aynı yön, 0 ilgisiz. Vektörleri birim uzunluğa getirdik; böylece uzunluk değil, yön karşılaştırılıyor.
Bu modelde iki rastgele parça arasındaki tipik benzerlik 0.33 civarında; lider merkezleri arası benzerlikler 0.58–0.74 arasında.
Mutlak değerler modele özgü: BAAI/bge-m3 ile aynı çiftler 0.82–0.94 çıkıyor. Bu yüzden modeller arası karşılaştırmada sıralamaya baktık, sayıya değil.

## Leader centroid nasıl oluşturuldu?
Üç adım: (1) her parçanın vektörünü normalize et, (2) bir konuşmanın parçalarının ortalamasını al ve tekrar normalize et → konuşma merkezi,
(3) bir liderin konuşma merkezlerinin ortalamasını al ve normalize et → lider merkezi. Her konuşma eşit ağırlıkta; uzun ya da çok konuşması olan lider fazladan ağırlık kazanmıyor.

## Neden multilingual model kullandık?
Derlem dört dilde: Türkçe, Fransızca, Almanca, İngilizce. Çok dilli bir model farklı dillerdeki benzer anlamları aynı uzaya yerleştirmeye çalışır.
Ama tamamen başaramaz: sonuçlarımızda parçaların en yakın komşularının %69–%100'i aynı liderden, yani aynı dilden.
Bu yüzden tema puanlarında her parçayı kendi dilindeki tema tanımıyla karşılaştırdık ve İngilizce tanımlarla da kontrol ettik (uyum yüksek). Dil ile lider bu derlemde ayrıştırılamıyor; bunu videoda açıkça söylemek gerekiyor.

## Neden UMAP sonucu gerçek mesafe olarak kullanılmıyor?
UMAP 4096 boyutu 2 boyuta indirir ve bunu yaparken yerel komşulukları korumaya, küresel mesafeleri ise bozmaya eğilimlidir. İki kümenin ekrandaki uzaklığı gerçek uzaklık değildir.
Bu nedenle: "2D projections are shown only for visualization; reported similarity values are calculated in the original embedding space."
UMAP parametreleri: n_neighbors=15, min_dist=0.1, metric=cosine, seed=42. PCA'yı da ikinci görsel olarak verdik.

## Neden konuşma uzunluğunu normalize ettik?
Macron'un bir konuşması 2.800 kelime, Putin'in bir konuşması 450 kelime. Parça sayısı üzerinden ortalama alsak Macron'un konuşmaları Merkel ve Putin'inkileri ezerdi.
Parça → konuşma → lider hiyerarşisiyle her konuşma bir oy hakkına sahip. Tema profilleri ve merkezler hep bu sırayla hesaplandı.

## Neden speech-level bootstrap yaptık?
Lider başına 3–5 konuşma var. Bir konuşmayı değiştirsek sonuç ne kadar değişir? Bunu görmek için her liderin konuşmalarını yerine koyarak 2000 kez yeniden örnekledik
ve merkez benzerliklerini, tema profillerini, çerçeve ölçümlerini her seferinde yeniden hesapladık. Yeniden örnekleme birimi parça değil, konuşma; çünkü aynı konuşmanın parçaları bağımsız değil.
Sonuç: bazı farklar (ör. en yakın çift ile ikinci çift arasındaki fark) güven aralığında sıfırı içeriyor; bunları "fark var" diye anlatmıyoruz.

## Ek: iki modelle sağlamlık kontrolü
Aynı parçaları BAAI/bge-m3 ile de gömdük ve tüm analizi tekrarladık. Lider çifti sıralamaları arasındaki korelasyon düşük; en yakın çift değişiyor.
Bu, "embedding geometrisi modele bağlıdır" cümlesinin somut hâli ve videonun en dürüst teknik mesajlarından biri.

## Söylememiz gereken şey
Tüm sayılar toplanan konuşma dosyalarını tarif eder. İdeoloji, siyasi kalite, kişilik, yeterlilik ya da ahlak hakkında hiçbir şey söylemez.
