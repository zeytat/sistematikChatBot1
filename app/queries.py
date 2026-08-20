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
