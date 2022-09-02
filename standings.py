from config import rapid_api
import pandas as pd
import requests
import json

import requests

url = "https://api-football-v1.p.rapidapi.com/v3/standings"

querystring = {"season":"2022","league":"135"}

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

count = 0
while count < 20:
    rank = int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["rank"]))
    team = str(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["team"]["name"]))
    wins = int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["all"]["win"]))
    draws = int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["all"]["draw"]))
    loses = int(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["all"]["lose"]))
    rank_list.append(rank)
    team_list.append(team)
    wins_list.append(wins)
    draws_list.append(draws)
    loses_list.append(loses)
    count += 1

zipped = list(zip(rank_list, team_list, wins_list, draws_list, loses_list))

df = pd.DataFrame(zipped, columns=['Rank', 'Team', 'Wins', 'Draws', 'Loses'])

print(df)