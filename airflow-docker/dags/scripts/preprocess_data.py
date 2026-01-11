import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import os
from scripts.preprocess_data import *

def load_data(path):
    return pd.read_csv(path)

def convert_to_datetime(df, column='timestamp'):
    df[column] = pd.to_datetime(df[column], utc=True).dt.tz_convert(None)
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    # df.drop(['timestamp'],axis=1,inplace=True)
    return df

def round_df_values(df, decimal_places=2):
    
    rounded_df = df.copy()
    
    # Get only numeric columns
    numeric_cols = rounded_df.select_dtypes(include=['float', 'float64', 'int', 'int64']).columns
    
    # Round only numeric columns
    for col in numeric_cols:
        rounded_df[col] = rounded_df[col].round(decimal_places)
    
    return rounded_df

# def calculate_outlier_bounds(df, column):
#     """Calculate IQR bounds for a column based on the full dataset."""
#     Q1 = df[column].quantile(0.25)
#     Q3 = df[column].quantile(0.75)
#     IQR = Q3 - Q1
#     lower = Q1 - 1.5 * IQR
#     upper = Q3 + 1.5 * IQR
#     return lower, upper

# need to work on outlier removal logic




def remove_outliers_csv(df,column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    # print(f"{column} outlier bounds: lower={lower}, upper={upper}")
    
    return df[(df[column] >= lower) & (df[column] <= upper)]

def calculate_outlier_bounds(df, col):
    # Ensure numeric (invalid parsing becomes NaN)
    df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop NaN values (so they don’t mess up quantile calculation)
    clean_series = df[col].dropna()

    Q1 = clean_series.quantile(0.25)
    Q3 = clean_series.quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    return lower, upper

def return_bounds(col):
    match col:
        case "pm1 (µg/m³)":
            return (round(-20.208926965792973, 2), round(44.87398937344551, 2))
        case "pm25 (µg/m³)":
            return (round(-27.27049974103768, 2), round(68.11641622086364, 2))
        case "Relative Humidity (%)":
            return (round(28.95525964101156, 2), round(79.2494281133016, 2))
        case "Temperature (c)":
            return (round(18.014293412367497, 2), round(34.058733522892, 2))
        case "pm03 (µg/m³)":
            return (round(-463.40693283081043, 2), round(2010.7737820943194, 2))
        case _:
            raise ValueError(f"Unknown column: {col}")
        
def check_and_remove_outliers(df):
    outliers = {}
    for col in df.columns:
        try:
            lower, upper = return_bounds(col)
            col_outliers = df[
                (df[col] < lower) | (df[col] > upper)
            ]
            if not col_outliers.empty:
                outliers[col] = col_outliers
        except ValueError:
            continue

    return outliers
                


def scale_data(df):
    columns_to_scale = ['pm1 (µg/m³)', 'Relative Humidity (%)', 'Temperature (c)', 'pm03 (µg/m³)']
    scaler = StandardScaler()
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    return df

def save_to_csv(df, csv_path="../data/main_readings.csv"):
    """Save new data to CSV (append if exists, otherwise create)"""
 
    
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

    
    df = round_df_values(df, decimal_places=2)
    df = convert_to_datetime(df)
    # df = convert_to_datetime(df)
    
    # print("timestamp changes: ")
    # print(df.head())


    if os.path.exists(csv_path):
        # Read existing data
        existing_df = pd.read_csv(csv_path)
        # print("existing df: ")
        # print(existing_df.tail())
        
        # CRITICAL FIX: Convert existing timestamp to datetime too
        existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp']).dt.tz_localize(None)
        
        # Combine existing and new data
        # print("combined df: ")
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        # print(combined_df.tail())
        
        # Remove duplicates based on timestamp
        combined_df.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
        
        # Sort by timestamp (now both are datetime objects)
        combined_df.sort_values('timestamp', inplace=True)
        
        # Reset index after sorting
        combined_df.reset_index(drop=True, inplace=True)
        
        # Save combined data
        combined_df.to_csv(csv_path, index=False)
        print(f"Data appended to {csv_path}")
        print(f"Total records: {len(combined_df)}")
        # print(f"Date range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
        # return combined_df
    else:
        print("CSV file does not exist.")
        return 



if __name__ == "__main__":
    # Example usage
    df = pd.read_csv('../data/combined_readings.csv')
    
    # print(df.info())
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
   
    
    
    # df['timestamp'] = pd.to_datetime(df['timestamp'])
    # print(df.info())
    # print(df.head())

    df = remove_outliers_csv(df, 'pm1 (µg/m³)')
    df = remove_outliers_csv(df, 'pm25 (µg/m³)')
    df = remove_outliers_csv(df, 'Relative Humidity (%)')
    df = remove_outliers_csv(df, 'Temperature (c)')
    df = remove_outliers_csv(df, 'pm03 (µg/m³)')
    # print(df.shape)
    
    # df = df.dropna().reset_index(drop=True)
    
    # bounds_pm1 = return_bounds("pm1 (µg/m³)")
    # bounds_pm25 = return_bounds("pm25 (µg/m³)")
    # bounds_rh = return_bounds("Relative Humidity (%)")
    # bounds_temp = return_bounds("Temperature (c)")
    # bounds_pm03 = return_bounds("pm03 (µg/m³)")
    
    # print(f"pm1 bounds: {bounds_pm1}")
    # print(f"pm25 bounds: {bounds_pm25}")
    # print(f"RH bounds: {bounds_rh}")
    # print(f"Temp bounds: {bounds_temp}")
    # print(f"pm03 bounds: {bounds_pm03}")
    
    #export to csv
    # df.to_csv('../data/main_readings.csv', index=False)
    
    # df = scale_data(df)
    
    # print(df.head())





# change the logic for removing outliers