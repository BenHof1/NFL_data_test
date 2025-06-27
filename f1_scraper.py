import requests
from bs4 import BeautifulSoup, SoupStrainer
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import time
year = 2025
offset = 1254
weights = [1,2,10,4]


def get_race(year, index, country, drivers):
    country = country.replace(' ', '-')
    print(country, year, index)
    base_url = 'https://www.formula1.com/en/results/'+ str(year)+'/races/'+\
               str(index)+'/' + country
    url = base_url + '/race-result'
    # print(base_url)
    time.sleep(1)
    res = pd.read_html(url)[0]
    # print(res)
    DNF = len([x for x in res['TIME / RETIRED'].to_list() if x == "DNF"])

    url = base_url + '/starting-grid'
    stg = pd.read_html(url)[0]

    url = base_url + '/pit-stop-summary'
    pit = pd.read_html(url)[0]
    num_pits = len(pit.STOPS)

    total = 0
    win_bonus = 0

    for d in drivers.DRIVER.to_list():

        # print(stg[stg.DRIVER == d])
        # print(res[res.DRIVER == d]['POS.'].to_list()[0])
        # print(drivers[drivers.DRIVER == d].POS.to_list()[0])
        try:
            x = int(stg[stg.DRIVER == d]['POS.'].to_list()[0])
        except:
            x=20
        try:
            y = int(res[res.DRIVER == d]['POS.'].to_list()[0])
        except:
            y=20
        try:
            z = int(drivers[drivers.DRIVER == d]['POS.'].to_list()[0])
        except:
            z=20
        # Value movement in the grid
        overtake_value =  10/(2*y) * np.abs(y-x)

        # Value change in expected performance
        rnd_value = 10/(2*z) * np.abs(y-z)

        if (y<4) & (z>6):
            win_bonus += 6
        total += overtake_value + rnd_value + win_bonus
    return total, num_pits, DNF

def weight_score(weights, data):
    return np.sum([ae*be for ae,be in zip(weights[0:-1],data)])/weights[-1]

year = 2025
offset = 1254
weights = [1,2,10,4]

url = 'https://www.formula1.com/en/results/' +str(year)+'/races'
source_code = requests.get(url)
soup = BeautifulSoup(source_code.content, 'lxml')
links = []
for link in soup.find_all('a', href=True):
    links.append(link['href'])

race_list = []
race_num = []
offset=1254

for i in range(40):
    for link in links:
        if ('/en/results/2025/races/'+str(offset+i)) in link:
            race_list.append(link.split('/')[-2])
            race_num .append(link.split('/')[-3])
            break


url = 'https://www.formula1.com/en/results/' +str(year)+'/races'
df_list = pd.read_html(url)[0]
# print(df_list)
df_list['Race'] = df_list.index+1
race_l = race_list[:df_list.Race.max()]
race_num = race_num[:df_list.Race.max()]
gps = df_list['GRAND PRIX'].to_list()
# print(df_list)

e_tab  = pd.DataFrame([], columns=['Grand prix', "R_index", 'Date', 'Laps', 'Time', 'Watchability'])
e_tab['Grand prix'] = race_l #df_list['GRAND PRIX']
e_tab['R_index'] = race_num
e_tab['Date'] = df_list['DATE']
e_tab['Laps'] = df_list['LAPS']
e_tab['Time'] = df_list['TIME']
e_tab['Watchability'] = 1
url = 'https://www.formula1.com/en/results/' +str(year)+'/drivers'
drivers = pd.read_html(url)[0]

ls = []
for index, ln in e_tab.iterrows():
    a,b,c = get_race(year, ln['R_index'], ln['Grand prix'], drivers)
    score = weight_score(weights, [a,b,c])
    e_tab.iloc[index, -1] = score
    # print(a,b,c, ln['Grand Prix'], score)
# print(e_tab)
e_tab.Watchability = e_tab.Watchability.round(2)
e_tab['Rank'] = e_tab.Watchability.rank()
# print(e_tab.Rank)
e_tab['Rel'] = (e_tab.Watchability)/e_tab.Watchability.max()
e_tab['Rel'] = e_tab['Rel'].round(2)
print(e_tab)

e_tab.drop('R_index',axis=1, inplace=True)
e_tab.T.to_json('data/f1_results.json')
