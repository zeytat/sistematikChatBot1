from app.queries import sorgu_calistir
from app.response import cevap_olustur


sorgular = [
    "Yücel Durmuş 31 Temmuz'da hangi lokasyonlarda bulundu?",
    "Yücel Durmuş 31 Temmuz'da ilk ne zaman görüldü?",
    "Yücel Durmuş 31 Temmuz'da son ne zaman görüldü?",
    "Yücel Durmuş 31 Temmuz saat 09:21'de neredeydi?",
]


for sorgu in sorgular:
    print("\nSorgu:", sorgu)

    sonuc = sorgu_calistir(sorgu)

    print("Cevap:")
    print(cevap_olustur(sonuc))
    