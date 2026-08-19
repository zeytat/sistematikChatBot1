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
