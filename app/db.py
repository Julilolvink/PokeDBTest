import os
import pyodbc

def get_connection():
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")
    driver   = os.getenv("AZURE_SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")
    encrypt  = os.getenv("AZURE_SQL_ENCRYPT", "yes")
    trust    = os.getenv("AZURE_SQL_TRUST_CERT", "no")
    timeout  = os.getenv("AZURE_SQL_TIMEOUT", "30")

    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};DATABASE={database};"
        f"UID={username};PWD={password};"
        f"Encrypt={encrypt};TrustServerCertificate={trust};"
        f"Connection Timeout={timeout};"
    )
    return pyodbc.connect(conn_str)
