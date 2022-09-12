import matplotlib.pyplot as plt
from config import rapid_api
import pandas as pd
import numpy as np
import requests
import json

url = "https://api-football-v1.p.rapidapi.com/v3/standings"

querystring = {"season":"2022","league":"140"}

headers = {
	"X-RapidAPI-Key": rapid_api,
	"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers, params=querystring)

json_res = response.json()

rank_list = []
team_list = []
wins_list = []
draws_list = []
loses_list = []
points_list = []

count = 0
while count < 20:
    rank_list.append(int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["rank"])))
    team_list.append(str(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["team"]["name"])))
    wins_list.append(int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["all"]["win"])))
    draws_list.append(int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["all"]["draw"])))
    loses_list.append(int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["all"]["lose"])))
    points_list.append(int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["points"])))
    count += 1

class espStandings:

    def table(self):
        headers = ['Rank', 'Team', 'Wins', 'Draws', 'Loses', 'Points']
        zipped = list(zip(rank_list, team_list, wins_list, draws_list, loses_list, points_list))

        df = pd.DataFrame(zipped, columns=headers)

        print(df)