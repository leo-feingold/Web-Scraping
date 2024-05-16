import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re

def getPlayerLinks():
    url = "https://www.perfectgame.org/college/CollegeCommitments.aspx?college=1658"
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
        #print(player.text.strip(), clean_url)
        links.append(clean_url)

    return links


def scrapeData(player_url):
    response = requests.get(player_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Fetch Name, Grad Year, Hometown and Positions Here:
    name = soup.find(class_="PlayerName").text.strip()
    grad_year = soup.find(id="ContentTopLevel_ContentPlaceHolder1_lblHSGrad").text.strip()
    positions = soup.find(id="ContentTopLevel_ContentPlaceHolder1_lblPos").text.strip()
    hometown = soup.find(id="ContentTopLevel_ContentPlaceHolder1_lblHomeTown").text.strip()


    # Fetch performance metrics here:
    metrics = {}
    titles = [t.text.strip() for t in soup.find_all(class_="BestResultsTitle")]
    best_numbers = [n.text.strip() for n in soup.find_all(class_="BestResultsNumber")]
    units = [u.text.strip() for u in soup.find_all(class_="unit")]

    date_ids = {
        'FB VELO': "ContentTopLevel_ContentPlaceHolder1_lblFBDate",
        '60 YARD DASH': "ContentTopLevel_ContentPlaceHolder1_lbl60Date",
        '10 YARD SPLIT': "ContentTopLevel_ContentPlaceHolder1_lbl10Date",
        'IF VELO': "ContentTopLevel_ContentPlaceHolder1_lblIFDate",
        'OF VELO': "ContentTopLevel_ContentPlaceHolder1_lblOFDate",
        '1B VELO': "ContentTopLevel_ContentPlaceHolder1_lbl1BDate",
        'EXIT VELO': "ContentTopLevel_ContentPlaceHolder1_lblExitVeloDate",
        'C POP': "ContentTopLevel_ContentPlaceHolder1_lblCPopDate",
        'C VELO': "ContentTopLevel_ContentPlaceHolder1_lblCVeloDate",

    }

    #dates = [d.text.strip() for d in soup.find_all(id="ContentTopLevel_ContentPlaceHolder1_lblFBDate")] #problem here is that each date for each metric has a different name
    for title, best_number, unit in zip(titles, best_numbers, units):
        title_text = title
        number_text = best_number
        unit_text = unit
        date_id = date_ids.get(title_text)  # Retrieve date id based on the metric title
        date_element = soup.find(id=date_id) if date_id else None
        date_text = date_element.text.strip() if date_element else "Date not available"
        
        metric_key = title_text
        #metric_value = f"{number_text} {unit_text}, Date: {date_text}" # this includes date
        metric_value = f"{number_text} {unit_text}" #this does not
        metrics[metric_key] = metric_value


    '''
    # Diagnostic prints to check what is being captured
    print("Name:", name)
    print("\n")
    print("Titles:", titles)
    print("\n")
    print("Numbers:", best_numbers)
    print("\n")
    print("Units:", units)
    print("\n")
    print("Dates:", dates)

    print(grad_year)
    print(positions)
    print(dates)
    '''

    # Constructing the player's stats dictionary
    player_tag = (name, grad_year, positions, hometown)
    player_stats = {player_tag: metrics}


    return player_stats

def getPlayerData():
    links = getPlayerLinks()
    data = []
    for i in range(len(links)):
        data.append(scrapeData(links[i]))
    print("\nData:")
    print(data)
    print("\n")
    return data


def createDF(input_data):
    data = input_data

    # Flatten the data into a list of dictionaries suitable for DataFrame creation
    rows = []
    for player_dict in data:
        for player_info, stats in player_dict.items():
            row = {
                'Name': player_info[0],
                'Grad Year': player_info[1],
                'Positions': player_info[2],
                'Hometown': player_info[3]  # Adding location to the row dictionary
            }
            row.update(stats)  # Add the stats into the row dictionary
            rows.append(row)

    # Create a DataFrame
    df = pd.DataFrame(rows)

    # Display the first 5 rows
    print(df.head(2))
    print(df.columns)
    return df

def plotData(df):
    # need to make the exit velo column numeric first and aslo need to drop NaN's
    df.dropna(subset=['EXIT VELO'], inplace=True)
    df['EXIT VELO'] = df['EXIT VELO'].apply(lambda x: float(re.search(r"(\d+\.?\d*)", x).group(1)) if pd.notnull(x) else x)

    plt.bar(df['Name'], df['EXIT VELO'])
    plt.xlabel('Name')  # Label for x-axis
    plt.ylabel('Exit Velocity (mph)')  # Label for y-axis
    plt.title('Player Exit Velocities, LSU Commits, Scraped From Perfect Game')  # Title of the plot
    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
    plt.tight_layout()  # Adjust layout to make room for rotated x-axis labels
    plt.show()

def createCSV(df):
    csv = df.to_csv('pefectGameBestMetrics.csv', index=False)
    return csv

if __name__ == "__main__":
    data = getPlayerData()
    df = createDF(data)
    print(df.head())
    print(df.columns)
    createCSV(df)