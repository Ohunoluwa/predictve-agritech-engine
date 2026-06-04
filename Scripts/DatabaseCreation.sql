
CREATE DATABASE MaizeWatch;
GO

USE MaizeWatch;
GO

CREATE TABLE HistoricalRainfall (
    RecordID INT IDENTITY(1,1) PRIMARY KEY, -- Keeps your data indexed and organized
    state VARCHAR(50),                      -- Matches your script's 'state' column
    ds DATETIME,                            -- The date column Prophet needs
    rainfall_mm FLOAT,                      -- Raw rainfall data
    temp_max FLOAT,                         -- New: Maximum Temperature
    temp_min FLOAT,                         -- New: Minimum Temperature
    y FLOAT                                 -- The target column Prophet will predict (matches rainfall)
);
GO