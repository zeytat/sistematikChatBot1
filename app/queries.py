import pandas as pd

from app.nlu import sorguyu_analiz_et
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
    personel_belirli_zamanda_konum,
    belirli_saatte_kimler,
    belirli_lokasyonda_kimler,
    lokasyonda_kimler
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

    if intent == "personel_karsilastirma":

        if analiz["personeller"] is None:
            return {
                "hata": "İki personel adı ve soyadı anlaşılamadı."
            }

        if baslangic is None or bitis is None:
            return {
                "hata": "Sorguda tarih bilgisi bulunamadı."
            }

        sonuclar = []

        for kisi in analiz["personeller"]:

            personel_id = personel_id_bul(
                kisi["ad"],
                kisi["soyad"]
            )

            if personel_id is None:
                sonuclar.append({
                    "personel": kisi,
                    "hata": "Personel bulunamadı."
                })
                continue

            hareketler = personel_hareketleri(
                personel_id,
                baslangic,
                bitis
            )

            sonuclar.append({
                "personel": kisi,
                "personel_id": personel_id,
                "kayit_sayisi": len(hareketler)
            })

        return {
            "intent": intent,
            "sonuclar": sonuclar
        }
    if intent == "personel_bilgisi":

        personel_id = personel_id_bul(
            personel["ad"],
            personel["soyad"]
        )

        if personel_id is None:
            return {
                "hata": "Personel bulunamadı veya birden fazla aktif personel eşleşti."
            }

        bilgi = personel_bul(
            personel["ad"],
            personel["soyad"]
        )

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": bilgi.iloc[0].to_dict()
        }
    if intent == "personel_bilgisi":

        personel_id = personel_id_bul(
            personel["ad"],
            personel["soyad"]
        )

        if personel_id is None:
            return {
                "hata": "Personel bulunamadı veya birden fazla aktif personel eşleşti."
            }

        bilgi = personel_bul(
            personel["ad"],
            personel["soyad"]
        )

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": bilgi.iloc[0].to_dict()
        }
    if intent == "saatte_kimler":

        if analiz["saat"] is None:
            return {
                "hata": "Saat bilgisi bulunamadı."
            }

        saat, dakika = analiz["saat"]

        tarih_saat = baslangic.replace(
            hour=saat,
            minute=dakika,
            second=0,
            microsecond=0
        )

        sonuc = belirli_saatte_kimler(
            tarih_saat
        )

        if sonuc is None or sonuc.empty:
            return {
                "intent": intent,
                "zaman": tarih_saat,
                "sonuc": pd.DataFrame()
            }

        # Aynı personelin birden fazla kaydı varsa
        # sadece en yakın kaydı tut.
        sonuc = sonuc.copy()

        sonuc["PersonnelId"] = pd.to_numeric(
            sonuc["PersonnelId"],
            errors="coerce"
        )

        if "zaman_farki" in sonuc.columns:
            sonuc = (
                sonuc
                .sort_values("zaman_farki")
                .drop_duplicates(
                    subset=["PersonnelId"],
                    keep="first"
                )
                .reset_index(drop=True)
            )
        else:
            sonuc = (
                sonuc
                .drop_duplicates(
                    subset=["PersonnelId"],
                    keep="first"
                )
                .reset_index(drop=True)
            )

        return {
            "intent": intent,
            "zaman": tarih_saat,
            "sonuc": sonuc
        }
    
    # Personel gerektiren sorgular
    personel_gereken_intentler = [
        "konum",
        "ilk_gorulme",
        "son_gorulme",
        "lokasyon_suresi",
        "lokasyon_suresi_belirli",
        "hareketler",
        "lokasyon_ziyaret_sayisi",
        "en_uzun_lokasyon",
        "en_cok_fiziksel_bolge",
        "personel_bilgisi"
    ]

    if intent in personel_gereken_intentler and personel is None:
        return {
            "hata": "Personel adı ve soyadı anlaşılamadı."
        }

    # Tarih gerektiren sorgular
    tarih_gereken_intentler = [
        "konum",
        "ilk_gorulme",
        "son_gorulme",
        "lokasyon_suresi",
        "lokasyon_suresi_belirli",
        "hareketler",
        "lokasyon_ziyaret_sayisi",
        "en_uzun_lokasyon",
        "en_cok_fiziksel_bolge",
        "personel_karsilastirma",
        "saatte_kimler",
        "lokasyonda_kimler"
    ]

    if intent in tarih_gereken_intentler:
        if baslangic is None or bitis is None:
            return {
                "hata": "Sorguda tarih bilgisi bulunamadı."
            }
            
    if intent == "lokasyonda_kimler":

        if analiz["saat"] is None:
            return {
                "hata": "Lokasyon sorgusu için saat bilgisi gerekli."
            }

        if analiz.get("lokasyon") is None:
            return {
                "hata": "Lokasyon anlaşılamadı."
            }

        saat, dakika = analiz["saat"]

        tarih_saat = baslangic.replace(
            hour=saat,
            minute=dakika,
            second=0,
            microsecond=0
        )

        lokasyon_adi = analiz["lokasyon"]

        query = """
            SELECT Id
            FROM Location
            WHERE Name = ?
              AND IsActive = 1
        """

        location_result = pd.read_sql(
            query,
            sql_connection,
            params=[lokasyon_adi]
        )

        if location_result.empty:
            return {
                "hata": f"{lokasyon_adi} lokasyonu bulunamadı."
            }

        location_id = int(
            location_result.iloc[0]["Id"]
        )

        sonuc = lokasyonda_kimler(
            tarih_saat,
            location_id
        )

        return {
            "intent": intent,
            "zaman": tarih_saat,
            "lokasyon": lokasyon_adi,
            "sonuc": sonuc
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

    if intent == "hareketler":

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

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": hareketler
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

    if intent == "lokasyon_ziyaret_sayisi":

        ziyaretler = personel_lokasyon_ziyaretleri(
            personel_id_bul(
                personel["ad"],
                personel["soyad"]
            ),
            baslangic,
            bitis
        )

        if ziyaretler is None or ziyaretler.empty:
            return {
                "hata": "Bu tarih aralığında lokasyon ziyareti bulunamadı."
            }

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": ziyaretler
        }

    if intent == "en_uzun_lokasyon":

        personel_id = personel_id_bul(
            personel["ad"],
            personel["soyad"]
        )

        if personel_id is None:
            return {
                "hata": "Personel bulunamadı."
            }

        sureler = personel_lokasyon_sureleri(
            personel_id,
            baslangic,
            bitis
        )

        if sureler is None or sureler.empty:
            return {
                "hata": "Bu tarih aralığında lokasyon kaydı bulunamadı."
            }

        en_uzun = sureler.iloc[0]

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": en_uzun
        }

    if intent == "en_cok_fiziksel_bolge":

        personel_id = personel_id_bul(
            personel["ad"],
            personel["soyad"]
        )

        if personel_id is None:
            return {
                "hata": "Personel bulunamadı."
            }

        hareketler = personel_hareketleri(
            personel_id,
            baslangic,
            bitis
        )

        if hareketler is None or hareketler.empty:
            return {
                "hata": "Bu tarih aralığında hareket kaydı bulunamadı."
            }

        bolgeler = (
            hareketler
            .dropna(subset=["PhysicalZoneName"])
            ["PhysicalZoneName"]
            .value_counts()
        )

        if bolgeler.empty:
            return {
                "hata": "Fiziksel bölge bilgisi bulunamadı."
            }

        return {
            "intent": intent,
            "personel": personel,
            "sonuc": {
                "fiziksel_bolge": bolgeler.index[0],
                "kayit_sayisi": int(bolgeler.iloc[0])
            }
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