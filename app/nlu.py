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

def sorguyu_analiz_et(metin):
    """
    Doğal dildeki kullanıcı sorgusunu
    yapılandırılmış bir sözlüğe dönüştürür.
    """

    return {
        "intent": sorgu_turu_bul(metin),
        "personel": personel_adi_bul(metin)
    }

from datetime import datetime, timedelta
import re


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


print(
    tarih_araligi_bul(
        "Yücel Durmuş 31 Temmuz'da hangi lokasyonlarda bulundu?"
    )
)
