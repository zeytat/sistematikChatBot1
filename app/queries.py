import pandas as pd

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
