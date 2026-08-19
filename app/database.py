import pyodbc

server = r"ZEYNEP\MSSQLSERVER03"
database = "IoTShipyard"

sql_connection = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)

print("SQL bağlantısı başarılı!")