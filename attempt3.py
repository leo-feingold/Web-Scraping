import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd

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
    driver = webdriver.Safari()  # Make sure to match the driver with your browser

    if links:
        driver.get(links[0])
        print("Navigated to:", links[0])

        try:
            # Find and click the events button
            event_button = driver.find_element(By.ID, "ContentTopLevel_ContentPlaceHolder1_lbEvents")
            event_button.click()
            time.sleep(5)  # Wait for the page to load after click

            # Step 3: Use BeautifulSoup to parse the updated HTML
            updated_html = driver.page_source
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
                'C POP': "CPop",
                'C VELO': "CVelo"
            }



# correct exit velo tag
#<span id="ContentTopLevel_ContentPlaceHolder1_rptEvents_lblPocketRadarExit_9">93</span>     

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


            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(metric_dicts)
            return df


        except Exception as e:
            print("Error navigating to the events tab:", str(e))
        finally:
            driver.quit()

import pandas as pd

def createYearlyBestDF(df):
    # Extract the year from the 'Date' column
    df['Year'] = pd.to_datetime(df['Date'].str.extract(r'(\d{4})')[0]).dt.year

    # Define the columns to exclude from numeric conversion
    exclude_columns = ['Date', 'Height']

    # Apply numeric conversion to all other columns
    for col in df.columns:
        if col not in exclude_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convert 'Height' into a numeric format (total inches)
    df['Height'] = df['Height'].apply(lambda x: int(x.split('-')[0]) * 12 + int(x.split('-')[1]) if pd.notna(x) and '-' in x else None)

    # Group by year and get the maximum of each metric
    max_metrics_by_year = df.groupby('Year').max()

    # Reshape the DataFrame so that each metric/year combination is a separate column
    result = max_metrics_by_year.unstack().to_frame().T
    result.columns = [f'{metric} {year}' for metric, year in result.columns]

    return result


def createCSV():
    csv = df.to_csv('pefectGameYearlyMetrics.csv', index=False)
    return csv


if __name__ == "__main__":
    df = pd.read_csv("/Users/leofeingold/Desktop/Web Scraping/pefectGameCareerMetrics.csv")
    df1 = createYearlyBestDF(df)
    createCSV(df1)
