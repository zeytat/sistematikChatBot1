import re


def sorgu_turu_bul(metin):
    """
    Kullanıcının doğal dildeki sorusunun temel türünü belirler.
    """

    metin = metin.lower()

    # Önce daha spesifik sorguları kontrol ediyoruz.
    if any(
        ifade in metin
        for ifade in [
            "hangi lokasyonlarda",
            "nerelerde bulundu",
            "nerelerdeydi",
            "hangi bölgelerde bulundu",
            "ne kadar kaldı",
            "ne kadar süre"
        ]
    ):
        return "lokasyon_suresi"

    if any(
        ifade in metin
        for ifade in [
            "ilk ne zaman",
            "ilk görüldü",
            "ilk görülme"
        ]
    ):
        return "ilk_gorulme"

    if any(
        ifade in metin
        for ifade in [
            "son ne zaman",
            "son görüldü",
            "son görülme"
        ]
    ):
        return "son_gorulme"

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

    Şimdilik iki kelimelik isimleri destekliyoruz.
    """
    
    kelimeler = metin.strip().split()

    # Sorgu ifadelerini temizle
    gereksizler = {
        "nerede",
        "neredeydi",
        "nerelerde",
        "bulundu",
        "hangi",
        "lokasyonlarda",
        "lokasyon",
        "bölgede",
        "bölgelerde",
        "ilk",
        "son",
        "ne",
        "zaman",
        "görüldü",
        "görülme",
        "süre",
        "kaldı",
        "konumu"
    }

    temiz = [
        kelime
        for kelime in kelimeler
        if kelime.lower() not in gereksizler
    ]

    if len(temiz) < 2:
        return None

    ad = temiz[0].upper()
    soyad = temiz[1].upper()

    return {
        "ad": ad,
        "soyad": soyad
    }
