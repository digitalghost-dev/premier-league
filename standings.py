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

rank = int(json.dumps(json_res["response"][0]["league"]["standings"][0][0]["rank"], indent=4))
team = str(json.dumps(json_res["response"][0]["league"]["standings"][0][0]["team"]["name"], indent=4))
wins = int(json.dumps(json_res["response"][0]["league"]["standings"][0][0]["all"]["win"], indent=4))
draws = int(json.dumps(json_res["response"][0]["league"]["standings"][0][0]["all"]["draw"], indent=4))
loses = int(json.dumps(json_res["response"][0]["league"]["standings"][0][0]["all"]["lose"], indent=4))
rank2 = int(json.dumps(json_res["response"][0]["league"]["standings"][0][1]["rank"], indent=4))
team2 = str(json.dumps(json_res["response"][0]["league"]["standings"][0][1]["team"]["name"], indent=4))
wins2 = int(json.dumps(json_res["response"][0]["league"]["standings"][0][1]["all"]["win"], indent=4))
draws2 = int(json.dumps(json_res["response"][0]["league"]["standings"][0][1]["all"]["draw"], indent=4))
loses2 = int(json.dumps(json_res["response"][0]["league"]["standings"][0][1]["all"]["lose"], indent=4))

table = {
    'rank': [rank, rank2], 
    'team': [team, team2], 
    'wins': [wins, wins2], 
    'draws': [draws, draws2], 
    'loses': [loses, loses2]
}

dataframe = pd.DataFrame(data = table)

print(dataframe)