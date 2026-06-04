import requests
import pandas as pd
import time
from datetime import datetime
from sqlalchemy import create_engine
import urllib

# ==============================
# MAIZE WATCH 1.0
# Historical Rainfall Pipeline
# ==============================

# Target States + Coordinates
states = {
    "Kano": {"lat": 12.0022, "lon": 8.5920},
    "Kaduna": {"lat": 10.5105, "lon": 7.4165},
    "Katsina": {"lat": 12.9816, "lon": 7.6223},
    "Sokoto": {"lat": 13.0627, "lon": 5.2438},
    "Jigawa": {"lat": 11.7483, "lon": 9.3370}
}

# Time Window

START_DATE = "2016-01-01"

# Automatically use today's date
END_DATE = datetime.today().strftime("%Y-%m-%d")

# Store all states together
all_data = []

print("======================================")
print("MAIZE WATCH 1.0 DATA COLLECTION START")
print("======================================")

for state_name, coords in states.items():

    print(f"\nFetching data for {state_name}...")

    # Open-Meteo Historical API
    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={coords['lat']}&"
        f"longitude={coords['lon']}&"
        f"start_date={START_DATE}&"
        f"end_date={END_DATE}&"
        "daily=precipitation_sum,"
        "temperature_2m_max,"
        "temperature_2m_min&"
        "timezone=Africa%2FLagos"
    )

    try:
        # API Request
        response = requests.get(url, timeout=60)

        # Check if request worked
        response.raise_for_status()

        # Convert JSON response
        data = response.json()

        # Build DataFrame
        df = pd.DataFrame({
            "ds": data["daily"]["time"],
            "rainfall_mm": data["daily"]["precipitation_sum"],
            "temp_max": data["daily"]["temperature_2m_max"],
            "temp_min": data["daily"]["temperature_2m_min"]
        })

        # Convert date column
        df["ds"] = pd.to_datetime(df["ds"])

        # Add state name
        df["state"] = state_name

        # Handle missing values
        df["rainfall_mm"] = df["rainfall_mm"].fillna(0)

        # Prophet-ready target column
        df["y"] = df["rainfall_mm"]

        # Append to master list
        all_data.append(df)

        # Save individual file
        filename = f"{state_name.lower()}_weather_history.csv"
        df.to_csv(filename, index=False)

        print(f"SUCCESS: Saved {filename}")

    except requests.exceptions.RequestException as e:
        print(f"API Error for {state_name}: {e}")

    except KeyError as e:
        print(f"Missing expected data for {state_name}: {e}")

    except Exception as e:
        print(f"Unexpected error for {state_name}: {e}")

    # Respect API rate limits
    time.sleep(1)

# ==============================
# CREATE MASTER DATASET & PUSH TO SQL
# ==============================

if all_data:

    master_df = pd.concat(all_data, ignore_index=True)

    # Save combined dataset locally
    master_df.to_csv("maize_watch_master_weather_data.csv", index=False)

    print("\n======================================")
    print("MASTER DATASET CREATED SUCCESSFULLY")
    print("File: maize_watch_master_weather_data.csv")
    
    print("\nPushing fresh data to SQL Server...")
    
    # Connect to your local SQL Server
    params = urllib.parse.quote_plus(
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=OHUNOLUWA\SQLEXPRESS;"
        r"DATABASE=MaizeWatch;"
        r"Trusted_Connection=yes;"
    )
    
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)
    
    # Overwrite the old HistoricalRainfall table with the fresh data
    master_df.to_sql('HistoricalRainfall', con=engine, if_exists='replace', index=False)
    
    print("SUCCESS: SQL Server table 'HistoricalRainfall' updated to today!")
    print("======================================")

else:
    print("\nNo data collected.")

print("\nDATA COLLECTION COMPLETE")