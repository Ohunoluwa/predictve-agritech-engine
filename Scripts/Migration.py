
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Float, DateTime, String
import urllib

# =========================================
# MAIZE WATCH 1.0
# SQL SERVER DATA MIGRATION PIPELINE
# =========================================

# SQL Server Connection Details
params = urllib.parse.quote_plus(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=OHUNOLUWA\SQLEXPRESS;"
    r"DATABASE=MaizeWatch;"
    r"Trusted_Connection=yes;"
)

# Create SQLAlchemy Engine
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    fast_executemany=True
)

# =========================================
# LOAD MASTER DATASET
# =========================================

# Read CSV
df = pd.read_csv("Datasets/maize_watch_master_weather_data.csv")

# Convert date column properly
df["ds"] = pd.to_datetime(df["ds"])

# Fill missing rainfall values
df["rainfall_mm"] = df["rainfall_mm"].fillna(0)

print("===================================")
print("STARTING SQL SERVER MIGRATION")
print("===================================")

print(f"Rows to migrate: {len(df)}")

# =========================================
# MIGRATE TO SQL SERVER
# =========================================

try:

    df.to_sql(
        name="HistoricalRainfall",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        dtype={
            "ds": DateTime(),
            "rainfall_mm": Float(),
            "temp_max": Float(),
            "temp_min": Float(),
            "state": String(50),
            "y": Float()
        }
    )

    print("===================================")
    print("MIGRATION SUCCESSFUL")
    print("Climate data stored in SQL Server.")
    print("===================================")

except Exception as e:

    print("===================================")
    print("MIGRATION FAILED")
    print(f"ERROR: {e}")
    print("===================================")