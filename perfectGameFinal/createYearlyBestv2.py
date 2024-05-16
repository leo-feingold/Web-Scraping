# Scraping Events Tab

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
import logging
import numpy as np


main_url = "https://www.perfectgame.org/college/CollegeCommitments.aspx?college=1658"

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    player_links = [a for a in soup.find_all('a', href=True) if 'PlayerProfile' in a['href']]
    return ["https://www.perfectgame.org/" + link['href'].replace('../', '') for link in player_links]

def safe_get_text(soup, id):
    element = soup.find(id=id)
    return element.text.strip() if element else "NA"

def open_event_tab():
    links = get_links(main_url)
    driver = webdriver.Safari()  # Initialize the driver outside the loop

    dataFrames = []
    try:
        for link in links:
            try:
                driver.get(link)
                print("Navigated to:", link)
                
                # Find and click the events button
                event_button = driver.find_element(By.ID, "ContentTopLevel_ContentPlaceHolder1_lbEvents")
                event_button.click()
                time.sleep(5)  # Wait for the page to load after click

                # Use BeautifulSoup to parse the updated HTML
                updated_html = driver.page_source # what does this do
                soup_updated = BeautifulSoup(updated_html, 'html.parser')

                event_dates = soup_updated.find_all('span', id=re.compile(r"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblEventDate_\d+"))
                metric_dicts = []

                metric_ids = {
                    'FB VELO': "FB",
                    'SL VELO': "SL",
                    'CB VELO': "CB",
                    'CH VELO': "CH",
                    '60 YARD DASH': "60",
                    '10 YARD SPLIT': "10",
                    'IF VELO': "IF",
                    'OF VELO': "OF",
                    '1B VELO': "1B",
                    'EXIT VELO': "PocketRadarExit",
                    'C POP': "Pop",
                    'C VELO': "C"
                }

                for i, date in enumerate(event_dates):
                    metrics = {
                        'Date': date.text.strip(),
                        'Weight': safe_get_text(soup_updated, f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblEventWt_{i}"),
                        'Height': safe_get_text(soup_updated, f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblEventHt_{i}")
                    }

                    for key, suffix in metric_ids.items():
                        metric_id = f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lbl{suffix}_{i}"
                        metrics[key] = safe_get_text(soup_updated, metric_id)

                    metric_dicts.append(metrics)

                df = pd.DataFrame(metric_dicts)
                #print(df.head())
                dataFrames.append(df)


            except Exception as e:
                print(f"Error processing link {link}: {str(e)}")

    finally:
        driver.quit()

    return dataFrames


def createYearlyBestDF():
    logging.basicConfig(level=logging.DEBUG) # what does this do
    CSVs = []
    dataFrames = open_event_tab()
    
    if not dataFrames:  
        logging.warning("No data to process.")
        return CSVs

    i = 0
    for df in dataFrames:
        # Log DataFrame columns to identify potential issues
        logging.debug(f"DataFrame Columns Before Processing: {df.columns}")

        if 'Date' not in df.columns:
            logging.error("Missing 'Date' column in DataFrame.")
            continue

        # Extract the year from the 'Date' column
        df['Year'] = pd.to_datetime(df['Date'].str.extract(r'(\d{4})')[0], errors='coerce').dt.year

        # Exclude non-numeric columns from conversion
        exclude_columns = ['Date', 'Height']

        for col in df.columns:
            if col not in exclude_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df['Height'] = df['Height'].apply(lambda x: int(x.split('-')[0]) * 12 + int(x.split('-')[1]) if pd.notna(x) and '-' in x else None)

        max_metrics_by_year = df.groupby('Year').max() # what does this do
        result = max_metrics_by_year.unstack().to_frame().T # what does this do
        result.columns = [f'{metric} {year}' for metric, year in result.columns]

        csv_filename = f"{i}_perfectGameYearlyMetrics.csv"
        #result.to_csv(csv_filename, index=False)
        i += 1
        #CSVs.append(csv_filename)

    return CSVs



if __name__ == "__main__":
   createYearlyBestDF()