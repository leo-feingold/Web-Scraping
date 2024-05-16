import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

main_url = "https://www.perfectgame.org/college/CollegeCommitments.aspx?college=1658"

def getLinks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <a> tags within a specific container, which needs to be identified.
    # For example, if player names are in a table or a list with a specific class or id:
    player_links = soup.find_all('a', href=True)  # Find all <a> elements with href attribute meaning they have a link

    # Filter out links that don't contain the path to players
    players = [a for a in player_links if 'PlayerProfile' in a['href']]

    links = []

    # Print each player's name and link
    for player in players:
        clean_url =  "https://www.perfectgame.org/" + player['href'].replace('../', '')
        links.append(clean_url)
    return links


def openEventTab():
    links = getLinks(main_url)
    driver = webdriver.Safari()  # Ensure the driver matches the browser

    if links:
        driver.get(links[0])  # Navigate to the first player's page
        print("Navigated to:", links[0])

        try:
            # Find and click the events button
            event_button = driver.find_element(By.ID, "ContentTopLevel_ContentPlaceHolder1_lbEvents")
            event_button.click()
            time.sleep(5)  # Wait for the page to load after click

            # Step 3: Use BeautifulSoup to parse the updated HTML
            updated_html = driver.page_source
            soup_updated = BeautifulSoup(updated_html, 'html.parser')

            # Fetch event dates using regex to match incremental IDs
            event_dates = soup_updated.find_all('span', id=re.compile(r"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblEventDate_\d+"))
            # Extract text and print each date
            dates = [date.text.strip() for date in event_dates]

            # Dictionary to store metrics for each date
            metric_dicts = []
            for i, date in enumerate(dates):
                metrics = {}
                metrics['Date'] = date
                metrics['Weight'] = soup_updated.find(id=f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblEventWt_{i}").text.strip()
                metrics['Height'] = soup_updated.find(id=f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblEventHt_{i}").text.strip()

#plan: each metric is stored like the following, so maybe make dictrionary that stored each metric and its coressponding ID tag, then filter through each event (by iterating), looking for that ID
#<span id="ContentTopLevel_ContentPlaceHolder1_rptEvents_lbl60_1" class="BestResultsNumber">6.36</span>

                my_dict = {
                    #title: tag,
                    'FB VELO': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblFB_{i}",
                    '60 YARD DASH': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lbl60_{i}",
                    '10 YARD SPLIT': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lbl10_{i}",
                    'IF VELO': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblIF_{i}",
                    'OF VELO': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblOF_{i}",
                    '1B VELO': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lbl1B_{i}",
                    'EXIT VELO': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblExitVelo_{i}",
                    'C POP': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblCPop_{i}",
                    'C VELO': f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lblCVelo_{i}"
                }



                # Find additional metrics
                metric_names = soup_updated.find_all(class_="BestResultsTitle")
                metric_values = soup_updated.find_all(class_="BestResultsNumber")
                additional_metrics = {name.text.strip(): value.text.strip() for name, value in zip(metric_names, metric_values)}

                # Combine all metrics
                metrics.update(additional_metrics)
                metric_dicts.append(metrics)

            # Output extracted data
            for metric in metric_dicts:
                print(metric)




        except Exception as e:
            print("Error navigating to the events tab:", str(e))
        finally:
            driver.quit()


if __name__ == "__main__":
    openEventTab()