def cevap_olustur(sonuc):
    """
    Backend sonucunu kullanıcıya okunabilir
    doğal dil cevabına dönüştürür.
    """

    if "hata" in sonuc:
        return sonuc["hata"]

    intent = sonuc["intent"]
    personel = sonuc["personel"]
    ad_soyad = f"{personel['ad']} {personel['soyad']}"

    if intent == "konum":

        bilgi = sonuc["sonuc"]

        return (
            f"{ad_soyad}, "
            f"{bilgi['istenen_zaman'].strftime('%d.%m.%Y %H:%M')} "
            f"civarında {bilgi['lokasyon']} lokasyonunda, "
            f"{bilgi['fiziksel_bolge']} fiziksel bölgesindeydi. "
            f"En yakın kayıt {bilgi['gorulme_zamani'].strftime('%H:%M:%S')} "
            f"zamanında alınmış; zaman farkı "
            f"{bilgi['zaman_farki_saniye']:.0f} saniye."
        )

    if intent == "ilk_gorulme":

        zaman = sonuc["zaman"]

        return (
            f"{ad_soyad}, {zaman.strftime('%d.%m.%Y')} tarihinde "
            f"ilk olarak saat {zaman.strftime('%H:%M:%S')} "
            f"zamanında görüldü."
        )

    if intent == "son_gorulme":

        zaman = sonuc["zaman"]

        return (
            f"{ad_soyad}, {zaman.strftime('%d.%m.%Y')} tarihinde "
            f"son olarak saat {zaman.strftime('%H:%M:%S')} "
            f"zamanında görüldü."
        )

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

    return "Bu sorgu türü için henüz cevap oluşturamıyorum."