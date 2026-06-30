# predictve-agritech-engine

  **Maize Watch 1.0** is a climate-tech and agricultural intelligence dashboard designed to help farmers, agricultural stakeholders, NGOs, and government agencies      make data-driven planting decisions through rainfall forecasting, drought risk assessment, and climate analytics.

The project uses historical weather observations, predictive analytics, and interactive data visualization to transform raw climate data into actionable agricultural intelligence.

## Problem Statement
   Agriculture in Northern Nigeria faces significant challenges due to:
    1) Unpredictable rainfall patterns
    2) False starts to the rainy season
    3) Increasing drought frequency
    4) Poor access to localized climate intelligence
    5) Limited decision-support tools for farmers
    
  These challenges often result in:

   1) Crop failures
   2) Reduced yields
   3) Inefficient irrigation
   4) Economic losses
   5) Food insecurity

   Maize Watch was developed to address these challenges by providing predictive insights to these issues.

   ## Project Objectives
   
   1) **Rainfall Intelligence:** Forecast rainfall patterns and seasonal trends affecting maize production.
   2) **Drought Risk Assessment:** Identify high-risk regions using moisture stress indicators and Standardized Precipitation Index (SPI) calculations.
   3)  **Planting Decision Support:** Provide actionable recommendations through a simple traffic-light signal system (PLANT, CAUTION, WAIT).
   4) **Agricultural Monitoring:** Visualize climate conditions across Northern Nigeria through interactive dashboards.
   5) **Data-Driven Planning:** Support agricultural agencies, NGOs, and policymakers with climate intelligence for food security planning.

  ## Study Area
  
   The project focuses on five major maize-producing states in Northern Nigeria:
    1) Kano
    2) Kaduna
    3) Katsina
    4) Jigawa
    5) Sokoto

   ## System Architecture
    
    `Weather Data Sources` ➔ `SQL Server Database` ➔ `Python Analytics Engine` ➔ `SPI Calculation` ➔ `Prophet Forecasting Model` ➔ `Planting Signal Generator` ➔ `Excel Data Export` ➔ `Tableau Dashboard`

  ## Technology Stack
  
   1) **Data Engineering:** Python (Pandas, NumPy, SQLAlchemy, PyODBC)
   2) **Database:** Microsoft SQL Server
   3) **Forecasting & Analytics:** Facebook Prophet
   4) **Statistical Analysis:** Standardized Precipitation Index (SPI)
   5) **Data Sources:** Open-Meteo Historical Weather API
   6) **Data Visualization:** Tableau Public
   7) **Version Control:** Git & GitHub

  **Rainfall Forecasting**
    Utilizes Prophet to forecast rainfall patterns and identify future moisture conditions.

  **SPI-Based Drought Monitoring**
    Calculates drought severity using the Standardized Precipitation Index:
     `SPI = (X - Mean) / Standard Deviation`

  **Automated Analytics Pipeline**
   The Python analytics engine automatically retrieves historical weather data, calculates SPI scores, runs Prophet forecasts, generates planting recommendations,    and exports dashboard-ready datasets.

   ## How It Works
  **Step 1**
    Collect historical rainfall and temperature observations from Open-Meteo.
  **Step 2**
    Store weather records in SQL Server.
  **Step 3**
    Run the analytics engine:
    python analytics.py
  **Step 4**
    Generate:
    SPI scores
    Rainfall forecasts
    Planting recommendations
  **Step 5**
    Export processed data to:
    MaizeWatch_Data.xlsx
  **Step 6**
    Refresh Tableau dashboard

 ## Author
  **Oba-Adeleke Ohunoluwa Elias**
    Data Analyst


  ## This project is developed for educational, research, and portfolio purposes.
