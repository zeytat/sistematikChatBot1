
def cevap_olustur(sonuc):
    """
    Backend sonucunu kullanıcıya okunabilir
    doğal dil cevabına dönüştürür.
    """

    if "hata" in sonuc:
        return sonuc["hata"]

    intent = sonuc["intent"]

    personel = sonuc.get("personel")

    if personel is not None:
        ad_soyad = f"{personel['ad']} {personel['soyad']}"

    # --------------------------------------------------
    # BELİRLİ ZAMANDA KONUM
    # --------------------------------------------------

    if intent == "konum":

        bilgi = sonuc["sonuc"]

        if bilgi is None:
            return (
                f"{ad_soyad} için belirtilen zamanda "
                f"konum kaydı bulunamadı."
            )

        return (
            f"{ad_soyad}, "
            f"{bilgi['istenen_zaman'].strftime('%d.%m.%Y %H:%M')} "
            f"civarında {bilgi['lokasyon']} lokasyonunda, "
            f"{bilgi['fiziksel_bolge']} fiziksel bölgesindeydi. "
            f"En yakın kayıt "
            f"{bilgi['gorulme_zamani'].strftime('%H:%M:%S')} "
            f"zamanında alınmış; zaman farkı "
            f"{bilgi['zaman_farki_saniye']:.0f} saniye."
        )

    # --------------------------------------------------
    # İLK GÖRÜLME
    # --------------------------------------------------

    if intent == "ilk_gorulme":

        zaman = sonuc["zaman"]

        return (
            f"{ad_soyad}, {zaman.strftime('%d.%m.%Y')} tarihinde "
            f"ilk olarak saat {zaman.strftime('%H:%M:%S')} "
            f"zamanında görüldü."
        )

    # --------------------------------------------------
    # SON GÖRÜLME
    # --------------------------------------------------

    if intent == "son_gorulme":

        zaman = sonuc["zaman"]

        return (
            f"{ad_soyad}, {zaman.strftime('%d.%m.%Y')} tarihinde "
            f"son olarak saat {zaman.strftime('%H:%M:%S')} "
            f"zamanında görüldü."
        )

    # --------------------------------------------------
    # LOKASYON SÜRELERİ
    # --------------------------------------------------

    if intent == "lokasyon_suresi":

        tablo = sonuc["sonuc"]

        if tablo.empty:
            return (
                f"{ad_soyad} için belirtilen tarih aralığında "
                f"lokasyon kaydı bulunamadı."
            )

        cevap = (
            f"{ad_soyad} için lokasyon kayıtları:\n"
        )

        for _, row in tablo.iterrows():

            cevap += (
                f"- {row['lokasyon']} / "
                f"{row['fiziksel_bolge']}: "
                f"{row['sure_dakika']:.2f} dakika\n"
            )

        return cevap.strip()

    # --------------------------------------------------
# GÜN İÇİNDEKİ HAREKETLER
# --------------------------------------------------

    if intent == "hareketler":

        tablo = sonuc["sonuc"]

    if tablo.empty:
        return (
            f"{ad_soyad} için belirtilen tarih aralığında "
            f"hareket kaydı bulunamadı."
        )

    tablo = tablo.sort_values("DeviceTime").copy()

    # --------------------------------------------------
    # Eksik lokasyonları temizle
    # --------------------------------------------------

    tablo["LocationName"] = tablo["LocationName"].apply(
        lambda x: "Bilinmiyor" if pd_is_missing(x) else str(x)
    )

    tablo["PhysicalZoneName"] = tablo["PhysicalZoneName"].apply(
        lambda x: "Bilinmiyor" if pd_is_missing(x) else str(x)
    )

    # Aynı lokasyondaki ardışık kayıtları grupla
    tablo["grup"] = (
        (tablo["LocationName"] != tablo["LocationName"].shift()) |
        (tablo["PhysicalZoneName"] != tablo["PhysicalZoneName"].shift())
    ).cumsum()

    gruplar = []

    for _, grup in tablo.groupby("grup"):

        ilk_zaman = grup["DeviceTime"].min()
        son_zaman = grup["DeviceTime"].max()

        lokasyon = grup["LocationName"].iloc[0]
        fiziksel_bolge = grup["PhysicalZoneName"].iloc[0]

        kayit_sayisi = len(grup)

        gruplar.append({
            "baslangic": ilk_zaman,
            "bitis": son_zaman,
            "lokasyon": lokasyon,
            "fiziksel_bolge": fiziksel_bolge,
            "kayit_sayisi": kayit_sayisi
        })

    # --------------------------------------------------
    # Cevabı oluştur
    # --------------------------------------------------

    tarih = tablo["DeviceTime"].min().strftime("%d.%m.%Y")

    cevap = (
        f"{ad_soyad}'ın {tarih} tarihindeki hareket özeti:\n"
    )

    # Çok uzun liste oluşmasını engelle
    maksimum_grup = 30

    for grup in gruplar[:maksimum_grup]:

        baslangic = grup["baslangic"]
        bitis = grup["bitis"]

        lokasyon = grup["lokasyon"]
        fiziksel_bolge = grup["fiziksel_bolge"]

        if baslangic == bitis:
            zaman = baslangic.strftime("%H:%M:%S")
        else:
            zaman = (
                f"{baslangic.strftime('%H:%M:%S')} - "
                f"{bitis.strftime('%H:%M:%S')}"
            )

        cevap += (
            f"- {zaman} → "
            f"{lokasyon} / {fiziksel_bolge}\n"
        )

    if len(gruplar) > maksimum_grup:
        cevap += (
            f"\n... ve {len(gruplar) - maksimum_grup} "
            f"hareket grubu daha."
        )

    # --------------------------------------------------
    # Genel özet
    # --------------------------------------------------

    bilinen = tablo[
        tablo["LocationName"] != "Bilinmiyor"
    ]

    if not bilinen.empty:

        lokasyon_sayilari = (
            bilinen["LocationName"]
            .value_counts()
        )

        en_cok_lokasyon = lokasyon_sayilari.index[0]

        cevap += (
            f"\n\nÖzet:"
            f"\n- Toplam kayıt: {len(tablo)}"
            f"\n- Bilinen lokasyon kaydı: {len(bilinen)}"
            f"\n- En sık görülen lokasyon: {en_cok_lokasyon}"
        )

        return cevap.strip() 
    # --------------------------------------------------
    # LOKASYON ZİYARET SAYISI
    # --------------------------------------------------

    if intent == "lokasyon_ziyaret_sayisi":

        tablo = sonuc["sonuc"]

        if tablo.empty:
            return (
                f"{ad_soyad} için belirtilen tarih aralığında "
                f"lokasyon ziyareti bulunamadı."
            )

        cevap = (
            f"{ad_soyad} için lokasyon ziyaretleri:\n"
        )

        for _, row in tablo.iterrows():

            cevap += (
                f"- {row['lokasyon']} / "
                f"{row['fiziksel_bolge']}: "
                f"{row['sure_saniye']:.0f} saniye\n"
            )

        cevap += (
            f"\nToplam ziyaret sayısı: {len(tablo)}"
        )

        return cevap

    # --------------------------------------------------
    # EN UZUN KALDIĞI LOKASYON
    # --------------------------------------------------

    if intent == "en_uzun_lokasyon":

        bilgi = sonuc["sonuc"]

        if bilgi is None:
            return (
                f"{ad_soyad} için belirtilen tarih aralığında "
                f"lokasyon kaydı bulunamadı."
            )

        return (
            f"{ad_soyad}, belirtilen tarih aralığında "
            f"en uzun {bilgi['lokasyon']} lokasyonunda, "
            f"{bilgi['fiziksel_bolge']} fiziksel bölgesinde kaldı. "
            f"Toplam süre: {bilgi['sure_dakika']:.2f} dakika."
        )

    # --------------------------------------------------
    # EN ÇOK BULUNDUĞU FİZİKSEL BÖLGE
    # --------------------------------------------------

    if intent == "en_cok_fiziksel_bolge":

        bilgi = sonuc["sonuc"]

        if bilgi is None:
            return (
                f"{ad_soyad} için fiziksel bölge kaydı bulunamadı."
            )

        return (
            f"{ad_soyad}, belirtilen tarih aralığında "
            f"en çok {bilgi['fiziksel_bolge']} fiziksel bölgesinde "
            f"bulundu. "
            f"Kayıt sayısı: {bilgi['kayit_sayisi']}."
        )

    # --------------------------------------------------
    # PERSONEL KARŞILAŞTIRMA
    # --------------------------------------------------

    if intent == "personel_karsilastirma":

        sonuclar = sonuc["sonuclar"]

        cevap = "Personel karşılaştırması:\n"

        for bilgi in sonuclar:

            personel_bilgisi = bilgi["personel"]

            ad_soyad_karsilastirma = (
                f"{personel_bilgisi['ad']} "
                f"{personel_bilgisi['soyad']}"
            )

            if "hata" in bilgi:

                cevap += (
                    f"- {ad_soyad_karsilastirma}: "
                    f"{bilgi['hata']}\n"
                )

            else:

                cevap += (
                    f"- {ad_soyad_karsilastirma}: "
                    f"{bilgi['kayit_sayisi']} hareket kaydı\n"
                )

        return cevap.strip()

    # --------------------------------------------------
    # PERSONEL BİLGİSİ
    # --------------------------------------------------

    if intent == "personel_bilgisi":

        bilgi = sonuc["sonuc"]

        cevap = (
            f"{ad_soyad} personel bilgileri:\n"
            f"- Personel ID: {bilgi['Id']}\n"
            f"- Sicil numarası: {bilgi['RegistryNumber']}\n"
            f"- Kart numarası: {bilgi['CardNo']}"
        )

        if bilgi["CardNoTemp"]:
            cevap += (
                f"\n- Geçici kart numarası: "
                f"{bilgi['CardNoTemp']}"
            )

        return cevap

    # --------------------------------------------------
    # BELİRLİ SAATTE KİMLER VARDI
    # --------------------------------------------------

    if intent == "saatte_kimler":

        tablo = sonuc["sonuc"]
        zaman = sonuc["zaman"]

        if tablo.empty:
            return (
                f"{zaman.strftime('%d.%m.%Y %H:%M')} "
                f"civarında konumu belirlenebilen personel bulunamadı."
            )

        toplam = len(tablo)
        gosterilecek = tablo.head(20)

        cevap = (
            f"{zaman.strftime('%d.%m.%Y %H:%M')} civarında "
            f"konumu belirlenebilen {toplam} personel bulundu.\n"
        )

        if toplam > 20:
            cevap += "İlk 20 kişi:\n"
        else:
            cevap += "Personeller:\n"

        for _, row in gosterilecek.iterrows():

            ad = str(row["PersonnelName"])
            soyad = str(row["PersonnelSurname"])

            cevap += f"- {ad} {soyad}\n"

        if toplam > 20:
            cevap += (
                f"\n... ve {toplam - 20} kişi daha."
            )

        return cevap.strip()
    
    # --------------------------------------------------
    # BELİRLİ LOKASYONDA KİMLER VARDI
    # --------------------------------------------------

    if intent == "lokasyonda_kimler":

        tablo = sonuc["sonuc"]

        zaman = sonuc["zaman"]

        lokasyon = sonuc["lokasyon"]

        if tablo.empty:
            return (
                f"{zaman.strftime('%d.%m.%Y %H:%M')} "
                f"civarında {lokasyon} lokasyonunda "
                f"kimse bulunamadı."
            )

        cevap = (
            f"{zaman.strftime('%d.%m.%Y %H:%M')} civarında "
            f"{lokasyon} lokasyonunda "
            f"{len(tablo)} personel bulundu:\n"
        )

        for _, row in tablo.iterrows():

            ad = str(row["PersonnelName"])

            soyad = str(row["PersonnelSurname"])

            cevap += f"- {ad} {soyad}\n"

        return cevap.strip()

    return "Bu sorgu türü için henüz cevap oluşturamıyorum."


def pd_is_missing(deger):
    """
    Pandas değerinin boş/NaN olup olmadığını kontrol eder.
    """

    if deger is None:
        return True

    try:
        return bool(deger != deger)
    except Exception:
        return False