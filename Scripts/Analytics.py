import pandas as pd
import numpy as np
from prophet import Prophet
from sqlalchemy import create_engine
import urllib
import logging
from sqlalchemy.types import Float, DateTime, String
from datetime import datetime

# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================
# ENGINE
# ==========================================
class MaizeWatchEngine:
    def __init__(self, server, database):
        params = urllib.parse.quote_plus(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )

        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            fast_executemany=True
        )

        logging.info("SQL Server connection established.")

    # ==========================================
    # FETCH DATA
    # ==========================================
    def fetch_data(self):
        logging.info("Fetching historical rainfall data...")
        query = """
            SELECT *
            FROM HistoricalRainfall
        """
        df = pd.read_sql(query, self.engine)

        df['ds'] = pd.to_datetime(df['ds'])
        df = df.sort_values(['state', 'ds'])

        return df

    # ==========================================
    # SPI CALCULATION
    # ==========================================
    def calculate_spi(self, df):
        logging.info("Calculating SPI...")

        df = df.sort_values(['state', 'ds'])

        # Rolling 30-day rainfall sum per state
        df['rolling_30'] = (
            df.groupby('state')['rainfall_mm']
            .transform(lambda x: x.rolling(window=30, min_periods=5).sum())
        )

        # State-level stats
        stats = df.groupby('state')['rolling_30'].agg(['mean', 'std']).reset_index()
        df = df.merge(stats, on='state', how='left')

        # Avoid division by zero
        df['std'] = df['std'].replace(0, np.nan)

        # SPI formula
        df['spi_score'] = (df['rolling_30'] - df['mean']) / df['std']
        df['spi_score'] = df['spi_score'].fillna(0)

        return df

    # ==========================================
    # FORECAST PER STATE
    # ==========================================
    def run_regional_forecast(self, df, horizon=75):
        logging.info("Running Prophet forecasts...")

        all_forecasts = []
        states = df['state'].unique()

        for state in states:
            try:
                logging.info(f"Forecasting: {state}")

                state_df = df[df['state'] == state][['ds', 'rainfall_mm', 'spi_score']].copy()

                # Prophet requires y column
                state_df = state_df.rename(columns={'rainfall_mm': 'y'})
                state_df = state_df.dropna()

                model = Prophet(
                    yearly_seasonality=True,
                    daily_seasonality=False
                )

                model.fit(state_df[['ds', 'y']])

                future = model.make_future_dataframe(periods=horizon)
                forecast = model.predict(future).tail(horizon)

                forecast['state'] = state
                forecast['current_spi'] = state_df['spi_score'].iloc[-1]

                all_forecasts.append(
                    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'state', 'current_spi']]
                )

            except Exception as e:
                logging.error(f"Failed for {state}: {e}")

        return pd.concat(all_forecasts, ignore_index=True)

    # ==========================================
    # SIGNAL ENGINE
    # ==========================================
    def generate_signals(self, forecast_df):
        logging.info("Generating planting signals...")

        def logic(row):
            spi = row['current_spi']
            rain = row['yhat']

            # Strong condition: good moisture + good rain forecast
            if spi > -0.5 and rain > np.percentile(forecast_df['yhat'], 60):
                return "🟢 PLANT"
 
            # Severe drought
            elif spi < -1.5:
                return "🔴 WAIT: Drought Risk"

            # Dry forecast
            elif rain < np.percentile(forecast_df['yhat'], 30):
                return "🔴 WAIT: Low Rain Forecast"

            else:
                return "🟡 CAUTION: Unstable Conditions"

        forecast_df['signal'] = forecast_df.apply(logic, axis=1)
        return forecast_df

    # ==========================================
    # SAVE TO SQL
    # ==========================================
    def save_results_to_sql(self, df):
        logging.info("Saving results to SQL Server...")

        df.to_sql(
            name="PlantingSignals",
            con=self.engine,
            if_exists="replace",
            index=False,
            dtype={
                "ds": DateTime(),
                "state": String(50),
                "signal": String(50),
                "yhat": Float(),
                "current_spi": Float()
            }
        )




 # ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":

    mw = MaizeWatchEngine(
        server=r'OHUNOLUWA\SQLEXPRESS',
        database='MaizeWatch'
    )

    # 1. DATA
    data = mw.fetch_data()

    # 2. SPI
    data_spi = mw.calculate_spi(data)

    # 3. FORECAST
    forecast = mw.run_regional_forecast(data_spi)

    print(forecast[['ds','state','yhat']].tail(20))

    print("\nLatest forecast date:")
    print(forecast['ds'].max())

    # 4. SIGNALS
    
    final = mw.generate_signals(forecast)
    
    #REFRESH TIMESTAMP

    final['RefreshTimestamp'] = datetime.now()
 
    

    # 5. SAVE (Export to Excel instead of SQL)
    # mw.save_results_to_sql(final)  <-- I commented this out since you are using Excel now!
    
    print("Exporting data to Excel for Tableau...")
    
    # 🛑 PASTE YOUR EXACT FILE PATH HERE:
    file_path = r"C:\Users\Ohunoluwa\Desktop\Maize Watch\MaizeWatch_Data.xlsx"
    
    
    # Write both dataframes to separate sheets in the same file
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        data_spi.to_excel(writer, sheet_name='HistoricalRainfall', index=False)
        final.to_excel(writer, sheet_name='PlantingSignals', index=False)
        
    print("✅ Both tables successfully exported to Excel!")

    print("\n--- PLANTING SIGNALS ---")
    print(final[['ds', 'state', 'signal']].head(10))

    print("\nSUCCESS: Pipeline executed successfully.")

    print(data['ds'].max())