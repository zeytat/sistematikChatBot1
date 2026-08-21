import pandas as pd

from app.response import cevap_olustur
from app.database import sql_connection


def personel_bul(ad, soyad):
    """
    Verilen ad ve soyada göre Personnel tablosundan
    personel kayıtlarını getirir.
    """

    query = """
        SELECT
            Id,
            Name,
            Surname,
            RegistryNumber,
            CardNo,
            CardNoTemp
        FROM Personnel
        WHERE
            Name = ?
            AND Surname = ?
            AND IsActive = 1
    """

    result = pd.read_sql(
        query,
        sql_connection,
        params=[ad, soyad]
    )

    return result

def personel_id_bul(ad, soyad):
    """
    Ad ve soyada göre tek bir personel varsa
    Personnel.Id değerini döndürür.

    Birden fazla eşleşme varsa None döndürür.
    """

    result = personel_bul(ad, soyad)

    if len(result) != 1:
        return None

    return int(result.iloc[0]["Id"])

from app.parquet import (
    personel_hareketleri,
    personel_ilk_son_gorulme,
    personel_lokasyonlari,
    personel_lokasyon_ziyaretleri,
    personel_lokasyon_sureleri,
    personel_belirli_zamanda_konum
)


def personel_hareketlerini_bul(
    ad,
    soyad,
    baslangic,
    bitis
):
    """
    Ad ve soyada göre personeli bulur,
    ardından ilgili personelin Parquet hareketlerini getirir.
    """

    personel_id = personel_id_bul(
        ad,
        soyad
    )

    if personel_id is None:
        return None

    return personel_hareketleri(
        personel_id,
        baslangic,
        bitis
    )

from app.parquet import personel_lokasyon_sureleri


def personel_lokasyon_sorgusu(
    ad,
    soyad,
    baslangic,
    bitis
):
    """
    Personel adı, soyadı ve tarih aralığı verilince
    personelin lokasyonlarda geçirdiği süreleri getirir.
    """

    personel_id = personel_id_bul(ad, soyad)

    if personel_id is None:
        return None

    return personel_lokasyon_sureleri(
        personel_id,
        baslangic,
        bitis
    )

def sorgu_calistir(metin):
    """
    Doğal dildeki sorguyu analiz eder ve
    uygun backend fonksiyonunu çalıştırır.
    """

    analiz = sorguyu_analiz_et(metin)

    intent = analiz["intent"]
    personel = analiz["personel"]
    baslangic = analiz["baslangic"]
    bitis = analiz["bitis"]

    if personel is None:
        return {
            "hata": "Personel adı ve soyadı anlaşılamadı."
        }

    if baslangic is None or bitis is None:
        return {
            "hata": "Sorguda tarih bilgisi bulunamadı."
        }

    if intent == "konum":

        if analiz["saat"] is None:
            return {
                "hata": "Konum sorgusu için saat bilgisi gerekli."
            }

        saat, dakika = analiz["saat"]

        tarih_saat = baslangic.replace(
            hour=saat,
            minute=dakika,
            second=0,
            microsecond=0
        )

        personel_id = personel_id_bul(
            personel["ad"],
            personel["soyad"]
        )

        if personel_id is None:
            return {
                "hata": "Personel bulunamadı."
            }

        sonuc = personel_belirli_zamanda_konum(
            personel_id,
            tarih_saat
        )

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": sonuc
        }

    if intent in ["ilk_gorulme", "son_gorulme"]:

        hareketler = personel_hareketlerini_bul(
            personel["ad"],
            personel["soyad"],
            baslangic,
            bitis
        )

        if hareketler is None or hareketler.empty:
            return {
                "hata": "Bu tarih aralığında personel hareketi bulunamadı."
            }

        if intent == "ilk_gorulme":
            kayit = hareketler.iloc[0]
        else:
            kayit = hareketler.iloc[-1]

        return {
            "intent": intent,
            "personel": personel,
            "zaman": kayit["DeviceTime"]
        }

    if intent == "lokasyon_suresi":

        sonuc = personel_lokasyon_sorgusu(
            personel["ad"],
            personel["soyad"],
            baslangic,
            bitis
        )

        if sonuc is None:
            return {
                "hata": "Personel bulunamadı."
            }

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": sonuc
        }

    return {
        "hata": f"Desteklenmeyen sorgu türü: {intent}"
    }


from app.nlu import sorguyu_analiz_et


sorgu = "Yücel Durmuş 31 Temmuz'da ne kadar süre kaldı?"

sonuc = sorgu_calistir(sorgu)

print(cevap_olustur(sonuc))