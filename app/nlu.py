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
