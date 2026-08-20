from pathlib import Path
import pandas as pd


PARQUET_ROOT = Path(
    r"C:\Users\ASUS\Desktop\data.1\data\data\enriched"
)

def parquet_dosyasi_bul(tarih, saat):
    dosya = (
        PARQUET_ROOT
        / str(tarih.year)
        / f"{tarih.month:02d}"
        / f"{tarih.day:02d}"
        / f"{saat:02d}"
        / "rtls_enriched.parquet"
    )

    if not dosya.exists():
        return None

    return dosya

def parquet_oku(tarih, saat):
    dosya = parquet_dosyasi_bul(tarih, saat)

    if dosya is None:
        return pd.DataFrame()

    return pd.read_parquet(dosya)

from datetime import datetime, timedelta


def parquet_aralik_oku(baslangic, bitis):
    """
    Verilen tarih-saat aralığındaki gerekli Parquet dosyalarını okur.
    Sadece mevcut olan saat dosyalarını okur.
    """

    tum_veriler = []

    mevcut_saat = baslangic.replace(minute=0, second=0, microsecond=0)

    while mevcut_saat < bitis:
        df = parquet_oku(
            mevcut_saat.date(),
            mevcut_saat.hour
        )

        if not df.empty:
            tum_veriler.append(df)

        mevcut_saat += timedelta(hours=1)

    if not tum_veriler:
        return pd.DataFrame()

    sonuc = pd.concat(tum_veriler, ignore_index=True)

    # İstenen saat aralığının dışındaki kayıtları temizle
    if "DeviceTime" in sonuc.columns:
        sonuc["DeviceTime"] = pd.to_datetime(sonuc["DeviceTime"])

        sonuc = sonuc[
            (sonuc["DeviceTime"] >= baslangic) &
            (sonuc["DeviceTime"] < bitis)
        ]

    return sonuc

def personel_hareketleri(personel_id, baslangic, bitis):
    """
    Belirli bir personelin verilen tarih-saat aralığındaki
    hareket kayıtlarını Parquet dosyalarından getirir.
    """

    df = parquet_aralik_oku(baslangic, bitis)

    if df.empty:
        return df

    # PersonnelId sayısal değilse de karşılaştırmayı düzgün yapalım
    df["PersonnelId"] = pd.to_numeric(
        df["PersonnelId"],
        errors="coerce"
    )

    sonuc = df[df["PersonnelId"] == personel_id].copy()

    if "DeviceTime" in sonuc.columns:
        sonuc = sonuc.sort_values("DeviceTime")

    return sonuc.reset_index(drop=True)

def personel_ilk_son_gorulme(personel_id, baslangic, bitis):
    """
    Personelin verilen tarih-saat aralığındaki
    ilk ve son görülme zamanını döndürür.
    """

    df = personel_hareketleri(
        personel_id,
        baslangic,
        bitis
    )

    if df.empty:
        return None

    return {
        "personel_id": personel_id,
        "ad_soyad": (
            f"{df.iloc[0]['PersonnelName']} "
            f"{df.iloc[0]['PersonnelSurname']}"
        ),
        "ilk_gorulme": df["DeviceTime"].min(),
        "son_gorulme": df["DeviceTime"].max(),
    }

def personel_lokasyonlari(personel_id, baslangic, bitis):
    """
    Personelin verilen tarih-saat aralığında
    görüldüğü lokasyonları getirir.
    """

    df = personel_hareketleri(
        personel_id,
        baslangic,
        bitis
    )

    if df.empty:
        return pd.DataFrame()

    sonuc = df[
        [
            "DeviceTime",
            "LocationName",
            "PhysicalZoneName",
            "LocationId",
            "PhysicalZoneId"
        ]
    ].copy()

    sonuc = sonuc.dropna(
        subset=["LocationName", "PhysicalZoneName"],
        how="all"
    )

    return sonuc.reset_index(drop=True)

def personel_lokasyon_ziyaretleri(personel_id, baslangic, bitis):
    """
    Personelin aynı lokasyonda art arda bulunduğu kayıtları
    tek bir ziyaret olarak gruplar.
    """

    df = personel_lokasyonlari(
        personel_id,
        baslangic,
        bitis
    )

    if df.empty:
        return pd.DataFrame()

    df = df.sort_values("DeviceTime").reset_index(drop=True)

    df["ziyaret_grubu"] = (
        (df["LocationId"] != df["LocationId"].shift()) |
        (df["PhysicalZoneId"] != df["PhysicalZoneId"].shift())
    ).cumsum()

    ziyaretler = (
        df.groupby("ziyaret_grubu")
        .agg(
            baslangic=("DeviceTime", "min"),
            bitis=("DeviceTime", "max"),
            lokasyon=("LocationName", "first"),
            fiziksel_bolge=("PhysicalZoneName", "first"),
            location_id=("LocationId", "first"),
            physical_zone_id=("PhysicalZoneId", "first"),
        )
        .reset_index(drop=True)
    )

    ziyaretler["sure_saniye"] = (
        ziyaretler["bitis"] - ziyaretler["baslangic"]
    ).dt.total_seconds()

    return ziyaretler

def personel_lokasyon_sureleri(personel_id, baslangic, bitis):
    """
    Personelin her lokasyonda toplam ne kadar süre
    geçirdiğini hesaplar.
    """

    ziyaretler = personel_lokasyon_ziyaretleri(
        personel_id,
        baslangic,
        bitis
    )

    if ziyaretler.empty:
        return pd.DataFrame()

    sureler = (
        ziyaretler
        .groupby(
            ["location_id", "physical_zone_id", "lokasyon", "fiziksel_bolge"],
            dropna=False
        )["sure_saniye"]
        .sum()
        .reset_index()
    )

    sureler = sureler.sort_values(
        "sure_saniye",
        ascending=False
    ).reset_index(drop=True)

    sureler["sure_dakika"] = (
        sureler["sure_saniye"] / 60
    ).round(2)

    return sureler

def personel_belirli_zamanda_konum(
    personel_id,
    tarih_saat,
    tolerans_dakika=5
):
    """
    Personelin verilen tarih-saat civarında en son görüldüğü konumu bulur.

    tolerans_dakika:
    Verilen zamandan önce/sonra kaç dakikalık aralıkta kayıt aranacağını belirler.
    """

    baslangic = tarih_saat - timedelta(minutes=tolerans_dakika)
    bitis = tarih_saat + timedelta(minutes=tolerans_dakika)

    df = personel_hareketleri(
        personel_id,
        baslangic,
        bitis
    )

    if df.empty:
        return None

    df = df.dropna(
        subset=["LocationName", "PhysicalZoneName"],
        how="all"
    )

    if df.empty:
        return None

    df["zaman_farki"] = (
        (df["DeviceTime"] - tarih_saat)
        .abs()
    )

    sonuc = df.sort_values("zaman_farki").iloc[0]

    return {
        "personel_id": personel_id,
        "ad_soyad": (
            f"{sonuc['PersonnelName']} "
            f"{sonuc['PersonnelSurname']}"
        ),
        "istenen_zaman": tarih_saat,
        "gorulme_zamani": sonuc["DeviceTime"],
        "lokasyon": sonuc["LocationName"],
        "fiziksel_bolge": sonuc["PhysicalZoneName"],
        "zaman_farki_saniye": (
            sonuc["zaman_farki"].total_seconds()
        )
    }

sonuc = personel_belirli_zamanda_konum(
    9584,
    datetime(2026, 7, 31, 9, 21),
    tolerans_dakika=5
)

print(sonuc)