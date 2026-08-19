from database import sql_connection
import pandas as pd


def personel_ara(ad_soyad):
    parcalar = ad_soyad.strip().split()

    if len(parcalar) < 2:
        return {
            "durum": "belirsiz",
            "mesaj": "Lütfen ad ve soyadı birlikte belirtin."
        }

    ad = " ".join(parcalar[:-1])
    soyad = parcalar[-1]

    query = """
    SELECT
        Id AS PersonnelId,
        Name AS PersonnelName,
        Surname AS PersonnelSurname,
        RegistryNumber
    FROM dbo.Personnel
    WHERE UPPER(Name) = UPPER(?)
      AND UPPER(Surname) = UPPER(?)
      AND IsActive = 1
    """

    result = pd.read_sql(
        query,
        sql_connection,
        params=[ad, soyad]
    )

    if result.empty:
        return {
            "durum": "kayit_yok",
            "mesaj": f"{ad_soyad} adlı aktif personel bulunamadı."
        }

    if len(result) > 1:
        return {
            "durum": "belirsiz",
            "mesaj": (
                f"{len(result)} farklı {ad_soyad.upper()} bulundu. "
                "Lütfen personel ID'si veya sicil numarası belirtin."
            ),
            "aday_sayisi": len(result),
            "adaylar": result.to_dict("records")
        }

    row = result.iloc[0]

    return {
        "durum": "basarili",
        "personel_id": int(row["PersonnelId"]),
        "ad_soyad": f"{row['PersonnelName']} {row['PersonnelSurname']}",
        "sicil_no": row["RegistryNumber"]
    }

def personel_nerede(personel_id):
    query = """
    SELECT TOP 1
        p.Id AS PersonnelId,
        p.Name AS PersonnelName,
        p.Surname AS PersonnelSurname,
        l.Name AS LocationName,
        pz.Name AS PhysicalZoneName,
        p.LastOnlineDate
    FROM dbo.Personnel p
    LEFT JOIN dbo.Location l
        ON p.CurrentLocationId = l.Id
    LEFT JOIN dbo.PhysicalZone pz
        ON p.CurrentPhysicalZoneId = pz.Id
    WHERE p.Id = ?
    """

    result = pd.read_sql(
        query,
        sql_connection,
        params=[personel_id]
    )

    if result.empty:
        return {
            "durum": "kayit_yok",
            "mesaj": f"{personel_id} ID'li personel bulunamadı."
        }

    row = result.iloc[0]

    return {
        "durum": "basarili",
        "personel_id": int(row["PersonnelId"]),
        "ad_soyad": f"{row['PersonnelName']} {row['PersonnelSurname']}",
        "konum": row["LocationName"],
        "fiziksel_bolge": row["PhysicalZoneName"],
        "son_online": row["LastOnlineDate"]
    }
