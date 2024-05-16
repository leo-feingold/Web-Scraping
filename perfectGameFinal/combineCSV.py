# combine individual events tabs into one csv

import pandas as pd
import re
import numpy as np 

# Function to load individual DataFrames
def getDFs():
    DFs = []
    for i in range(18): # need to change this depending on the number of commits in each year
        df = pd.read_csv(f"/Users/leofeingold/Desktop/Web Scraping/{i}_perfectGameYearlyMetrics.csv")
        DFs.append(df)
    return DFs

# Function to extract (metric, year) from a column name
def extract_metric_and_year(column_name):
    # Extract year using regex
    year_match = re.search(r'\b(20\d{2})\b', column_name)
    year = year_match.group(1) if year_match else None
    # Extract the metric by removing the year
    metric = re.sub(r'\b(20\d{2})\b', '', column_name).strip()
    return metric, year

# Function to reorder columns based on metric and year
def reorder_columns(df):
    # Create a sorting key based on (metric, year)
    sorted_columns = sorted(df.columns, key=lambda col: extract_metric_and_year(col))
    # Reorder the DataFrame columns
    return df[sorted_columns]

# Main function to combine and reorder columns
def create_all_players_individual_best_yearly_csv_fixed_v2():
    dataFrames = getDFs()
    
    # Combine all DataFrames into one and add an identifier column for each player
    combined_df = pd.concat(dataFrames, ignore_index=True)
    
    # Reorder columns
    combined_df = reorder_columns(combined_df)
    
    # Display all columns for validation
    pd.set_option('display.max_columns', None)
    print(combined_df.columns)

    combined_df.to_csv('2024CommitsOverTime.csv', index=False)

    return combined_df

# Execute the main function
if __name__ == "__main__":
    create_all_players_individual_best_yearly_csv_fixed_v2()
