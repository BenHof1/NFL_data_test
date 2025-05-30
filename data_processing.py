# scheduled_update.py
import json
import requests
from datetime import datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def get_game(link, wk):
    url = "https://www.cbssports.com/nfl/gametracker/boxscore/" + link + '/'
    df_list = pd.read_html(url)
    data = df_list[3]
    data.set_index("Team Stats", inplace=True)
    data.rename(columns={'Unnamed: 1': str(df_list[1][0][0]), 'Unnamed: 2': str(df_list[2][0][0])}, inplace=True)
    data = data.transpose()
    try:
        data['score'] = df_list[5][6][1:3].values
    except:
        data['score'] = df_list[5][5][1:3].values
    data['conceeded'] = df_list[5][5][3::-1][:2].values
    data['opponent'] = [str(df_list[2][0][0]), str(df_list[1][0][0])]
    x, y = data['Time of Pos'].str.split(':')
    data["TOP"] = [int(x[0]) + int(x[1]) / 60, int(y[0]) + int(y[1]) / 60]

    x, y = data['3rd Down Conv'].str.split('-')
    data["3rd_Down_Att"] = [int(x[1]), int(y[1])]
    data["3rd_Down_G"] = [int(x[0]), int(y[0])]

    x, y = data['4th Down Conv'].str.split('-')
    data["4th_Down_Att"] = [int(x[1]), int(y[1])]
    data["4th_Down_G"] = [int(x[0]), int(y[0])]

    x, y = data['Red Zone Eff.'].str.split('-')
    data["Red_Att"] = [int(x[1]), int(y[1])]
    data["Red_G"] = [int(x[0]), int(y[0])]
    data['Week'] = [wk, wk]
    data.drop(columns=['3rd Down Conv', '4th Down Conv', 'Red Zone Eff.', 'Time of Pos'], inplace=True)
    if df_list[5][5][1] > df_list[5][5][2]:
        data['outcome'] = ["W", "L"]
    elif df_list[5][5][1] < df_list[5][5][2]:
        data['outcome'] = ["L", "W"]
    else:
        data['outcome'] = ["D", "D"]

    data = data.reset_index()
    # data.to_csv(loc, mode='a', header=False, index=False)
    return get_scoring(data)


def get_scoring(df):
    x = df.opponent.to_list()[0] + " vs " + df.opponent.to_list()[1]
    sum_points = pd.to_numeric(df.score).sum()

    win_margin = np.abs(int(df.score.to_list()[0]) - int(df.score.to_list()[1]))
    total_yards_div_100 = pd.to_numeric(df['Total Net Yards']).sum() / 100
    # team_wins_rank = 0
    # print(sum_points, win_margin, 3*total_yards_div_100)
    y = sum_points - win_margin + 3 * total_yards_div_100
    return x, int(y)


def fetch_nfl_data():
    # Fetch from NFL API or data source
    lsx2 = dict()
    for week in range(18):
        url = "https://www.cbssports.com/nfl/scoreboard/all/2024/regular/" + str(week + 1) + "/"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        ls = []
        d = soup.findAll('a')
        for i in d:
            x = i.get('href')
            if '/nfl/gametracker/recap/' in str(x):
                ls.append([x.split('/')[4], int(url.split('/')[-2])])
        lsx = []
        for i in ls:
            x, y = get_game(i[0], i[1])
            lsx.append([x, y])
            print(x, y)
        lsx2["Week "+str(week + 1)] = sorted(lsx, key=lambda x: -x[1])

    for week in [(19, 'Wildcard'),
                 (20, 'Divisional'),
                 (21, 'Championship'),
                 (23, 'Super Bowl')]:
        url = "https://www.cbssports.com/nfl/scoreboard/all/2024/postseason/" + str(week[0]) + "/"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        ls = []
        d = soup.findAll('a')
        for i in d:
            x = i.get('href')
            if '/nfl/gametracker/recap/' in str(x):
                ls.append([x.split('/')[4], int(url.split('/')[-2])])
        lsx = []
        for i in ls:
            x, y = get_game(i[0], i[1])
            lsx.append([x, y])
            print(x, y)
        lsx2[week[1]] = sorted(lsx, key=lambda x: -x[1])

    return lsx2


def process_results():
    # Process the data
    pass


def update_site_data():
    data = fetch_nfl_data()
    print(data)
    # Save to JSON file
    with open('data/nfl_results.json', 'w') as f:
        json.dump(data, f)


def html_table(data):
    html_tab = ''
    for i in data.keys():
        html_tab = '\n'.join((html_tab,'<h3>',i,'</h3>', '<table>'))
        for sublist in data[i]:
            html_tab = '\n'.join((html_tab,'  <tr><td>'))
            html_tab = '\n'.join((html_tab,'    </td><td>'.join(sublist)))
            html_tab = '\n'.join((html_tab,'  </td></tr>'))
        html_tab = '\n'.join((html_tab,'</table>'))
    print(html_tab)
    return html_tab


def update_static_data():
    data = fetch_nfl_data()
    for k in data.keys():
        data[k] = [[x[0], str(x[1])] for x in data[k]]
    print(data)
    a = '''
        <html>
        <head>
        <h1> NFL Game Rankings </h1>
        </head>
        '''
    b = '''
        <h2> Recent game results</h2>
        '''

    c = '''
        </html>
        '''
    tab = html_table(data)

    abc = '\n'.join((a, b, tab, c))
    f = open("index.html", "w")
    f.write(abc)
    f.close()

if __name__ == "__main__":
    update_site_data()
    # update_static_data()