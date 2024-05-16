import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re




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
                '60 YARD DASH': "60",
                '10 YARD SPLIT': "10",
                'IF VELO': "IF",
                'OF VELO': "OF",
                '1B VELO': "1B",
                'EXIT VELO': "ExitVelo",
                'C POP': "CPop",
                'C VELO': "CVelo"
            }

            for i, date in enumerate(event_dates):
                metrics = {'Date': date.text.strip()}
                for key, suffix in metric_ids.items():
                    metric_id = f"ContentTopLevel_ContentPlaceHolder1_rptEvents_lbl{suffix}_{i}"
                    metrics[key] = safe_get_text(soup_updated, metric_id)

                
                metric_dicts.append(metrics)

            for metric in metric_dicts:
                print(metric)

        except Exception as e:
            print("Error navigating to the events tab:", str(e))
        finally:
            driver.quit()

if __name__ == "__main__":
    open_event_tab()
