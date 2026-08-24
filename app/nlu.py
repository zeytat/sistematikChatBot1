import re
from datetime import datetime, timedelta
def sorgu_turu_bul(metin):
    """
    Kullanıcının doğal dildeki sorusunun
    sorgu türünü belirler.
    """

    metin = metin.lower()

    # 1. Personel karşılaştırma
    if any(
        ifade in metin
        for ifade in [
            "karşılaştır",
            "karsilastir",
            "karşılaştırma",
            "karsilastirma",
            "kıyasla",
            "kiyasla"
        ]
    ):
        return "personel_karsilastirma"

    # 2. Personel bilgisi
    if any(
        ifade in metin
        for ifade in [
            "personel bilgisi",
            "personel bilgileri",
            "sicil numarası",
            "sicil numarasi",
            "kart numarası",
            "kart numarasi"
        ]
    ):
        return "personel_bilgisi"

    # 3. Belirli saatte kimler vardı?
    if any(
        ifade in metin
        for ifade in [
            "saatte kimler",
            "saatinde kimler",
            "o saatte kimler",
            "kimler vardı",
            "kimler vardi"
        ]
    ):
        return "saatte_kimler"

    # 4. Belirli lokasyonda kimler vardı?
    if any(
        ifade in metin
        for ifade in [
            "lokasyonunda kimler",
            "lokasyonda kimler",
            "bölgede kimler",
            "bolgede kimler"
        ]
    ):
        return "lokasyonda_kimler"

    # 5. Belirli lokasyonda ne kadar kaldı?
    if any(
        ifade in metin
        for ifade in [
            "lokasyonda ne kadar kaldı",
            "lokasyonunda ne kadar kaldı",
            "lokasyonda ne kadar süre",
            "lokasyonunda ne kadar süre"
        ]
    ):
        return "lokasyon_suresi_belirli"

    # 6. En çok bulunduğu fiziksel bölge
    if any(
        ifade in metin
        for ifade in [
            "en çok bulunduğu fiziksel bölge",
            "en cok bulundugu fiziksel bolge",
            "en çok bulunduğu bölge",
            "en cok bulundugu bolge",
            "en fazla bulunduğu fiziksel bölge",
            "en fazla bulundugu fiziksel bolge"
        ]
    ):
        return "en_cok_fiziksel_bolge"

    # 7. En uzun kaldığı lokasyon
    if any(
        ifade in metin
        for ifade in [
            "en uzun kaldığı lokasyon",
            "en uzun kaldigi lokasyon",
            "en uzun kaldığı yer",
            "en uzun kaldigi yer"
        ]
    ):
        return "en_uzun_lokasyon"

    # 8. Lokasyon ziyaret sayısı
    if any(
        ifade in metin
        for ifade in [
            "lokasyon ziyaret sayısı",
            "lokasyon ziyaret sayisi",
            "ziyaret sayısı",
            "ziyaret sayisi",
            "kaç kez ziyaret",
            "kac kez ziyaret"
        ]
    ):
        return "lokasyon_ziyaret_sayisi"

    # 9. Gün içindeki hareketler
    if any(
        ifade in metin
        for ifade in [
            "gün içindeki hareketleri",
            "gun icindeki hareketleri",
            "gün içindeki hareketleri",
            "hareketleri",
            "hareket kayıtları",
            "hareket kayitlari",
            "gün içindeki hareketleri"
        ]
    ):
        return "hareketler"

    # 10. Lokasyonlarda geçirdiği süre
    if any(
        ifade in metin
        for ifade in [
            "hangi lokasyonlarda",
            "nerelerde bulundu",
            "nerelerdeydi",
            "hangi bölgelerde bulundu",
            "ne kadar kaldı",
            "ne kadar süre",
            "nerelerde zaman geçirdi",
            "nerelerde kaldı"
        ]
    ):
        return "lokasyon_suresi"

    # 11. İlk görülme
    if any(
        ifade in metin
        for ifade in [
            "ilk ne zaman",
            "ilk görüldü",
            "ilk görülme"
        ]
    ):
        return "ilk_gorulme"

    # 12. Son görülme
    if any(
        ifade in metin
        for ifade in [
            "son ne zaman",
            "son görüldü",
            "son görülme"
        ]
    ):
        return "son_gorulme"

    # 13. Belirli konum
    if any(
        ifade in metin
        for ifade in [
            "nerede",
            "neredeydi",
            "hangi lokasyon",
            "hangi bölgede",
            "konumu"
        ]
    ):
        return "konum"

    return "bilinmeyen"

def personel_adi_bul(metin):
    """
    Metin içerisinden personelin ad ve soyadını bulmaya çalışır.
    Personel gerektirmeyen sorgularda None döndürür.
    """

    metin_kucuk = metin.lower()

    # Bu sorgular personel adı gerektirmez
    if any(
        ifade in metin_kucuk
        for ifade in [
            "kimler vardı",
            "kimler vardi",
            "saatte kimler",
            "saatinde kimler",
            "o saatte kimler",
            "lokasyonunda kimler",
            "lokasyonda kimler",
            "bölgede kimler",
            "bolgede kimler"
        ]
    ):
        return None

    kelimeler = metin.strip().split()

    gereksizler = {
        "nerede",
        "neredeydi",
        "nerelerde",
        "bulundu",
        "hangi",
        "lokasyonlarda",
        "lokasyon",
        "lokasyonunda",
        "lokasyonda",
        "bölgede",
        "bölgelerde",
        "bolgede",
        "bolgelerde",
        "ilk",
        "son",
        "ne",
        "zaman",
        "görüldü",
        "görüldü",
        "görülme",
        "süre",
        "kaldı",
        "konumu",
        "gün",
        "gun",
        "içindeki",
        "icindeki",
        "hareketleri",
        "ziyaret",
        "sayısı",
        "sayisi",
        "en",
        "uzun",
        "çok",
        "cok",
        "bulunduğu",
        "bulundugu",
        "fiziksel",
        "bölge",
        "bolge",
        "hangisi",
        "hangisi",
        "personel",
        "bilgisi",
        "bilgileri",
        "ve",
        "karşılaştır",
        "karsilastir",
        "karşılaştırma",
        "karsilastirma"
    }

    temiz = [
        kelime
        for kelime in kelimeler
        if kelime.lower().strip(".,?!") not in gereksizler
    ]

    if len(temiz) < 2:
        return None

    ad = temiz[0].upper()
    soyad = temiz[1].upper()

    return {
        "ad": ad,
        "soyad": soyad
    }

def personelleri_bul(metin):
    """
    Metinden iki personelin ad ve soyadını bulur.
    """

    kelimeler = metin.strip().split()

    gereksizler = {
        "ile",
        "ve",
        "karşılaştır",
        "karşılaştırması",
        "karşılaştırma",
        "arasında"
    }

    temiz = [
        kelime
        for kelime in kelimeler
        if kelime.lower() not in gereksizler
    ]

    if len(temiz) < 4:
        return None

    return [
        {
            "ad": temiz[0].upper(),
            "soyad": temiz[1].upper()
        },
        {
            "ad": temiz[2].upper(),
            "soyad": temiz[3].upper()
        }
    ]

def sorguyu_analiz_et(metin):

    tarih = tarih_araligi_bul(metin)
    saat = saat_bul(metin)
    intent = sorgu_turu_bul(metin)

    if intent in ["lokasyonda_kimler", "saatte_kimler"]:
        sonuc = {
            "intent": intent,
            "personel": None,
            "baslangic": tarih[0] if tarih else None,
            "bitis": tarih[1] if tarih else None,
            "saat": saat
        }

        if intent == "lokasyonda_kimler":
            sonuc["lokasyon"] = lokasyon_bul(metin)

        return sonuc

    return {
        "intent": intent,
        "personel": personel_adi_bul(metin),
        "baslangic": tarih[0] if tarih else None,
        "bitis": tarih[1] if tarih else None,
        "saat": saat
    }


def tarih_araligi_bul(metin):
    """
    Metinden tarih bilgisini bulur ve gün başlangıcı/bitişi döndürür.

    Desteklenen örnekler:
    - 31 Temmuz
    - 31 Temmuz 2026
    - 31.07.2026
    - 31/07/2026
    """

    aylar = {
        "ocak": 1,
        "şubat": 2,
        "mart": 3,
        "nisan": 4,
        "mayıs": 5,
        "haziran": 6,
        "temmuz": 7,
        "ağustos": 8,
        "eylül": 9,
        "ekim": 10,
        "kasım": 11,
        "aralık": 12
    }

    metin_kucuk = metin.lower()

    # Örnek: 31 Temmuz 2026 veya 31 Temmuz
    eslesme = re.search(
        r"\b(\d{1,2})\s+([a-zçğıöşü]+)(?:\s+(\d{4}))?\b",
        metin_kucuk
    )

    if eslesme:
        gun = int(eslesme.group(1))
        ay_adi = eslesme.group(2)
        yil = eslesme.group(3)

        if ay_adi in aylar:
            yil = int(yil) if yil else datetime.now().year

            baslangic = datetime(
                yil,
                aylar[ay_adi],
                gun
            )

            bitis = baslangic + timedelta(days=1)

            return baslangic, bitis

    # Örnek: 31.07.2026 veya 31/07/2026
    eslesme = re.search(
        r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b",
        metin_kucuk
    )

    if eslesme:
        gun = int(eslesme.group(1))
        ay = int(eslesme.group(2))
        yil = int(eslesme.group(3))

        baslangic = datetime(
            yil,
            ay,
            gun
        )

        bitis = baslangic + timedelta(days=1)

        return baslangic, bitis

    return None

def saat_bul(metin):
    """
    Metinden saat bilgisini bulur.

    Desteklenen örnekler:
    - 09:21
    - saat 09:21
    - 9:21
    """

    eslesme = re.search(
        r"(?:saat\s*)?(\d{1,2}):(\d{2})",
        metin.lower()
    )

    if not eslesme:
        return None

    saat = int(eslesme.group(1))
    dakika = int(eslesme.group(2))

    if saat > 23 or dakika > 59:
        return None

    return saat, dakika

def lokasyon_bul(metin):
    """
    Sorgudaki lokasyon adını bulur.
    """

    lokasyonlar = [
        "ZİNCİR"
    ]

    metin_upper = metin.upper()

    for lokasyon in lokasyonlar:
        if lokasyon in metin_upper:
            return lokasyon

    return None
