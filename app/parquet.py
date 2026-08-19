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
