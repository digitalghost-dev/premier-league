from config import rapid_api
import requests
import json
 
url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
 
# League 135 is Italy
querystring = {"league":"135","season":"2022"}
 
headers = {
    "X-RapidAPI-Key": rapid_api,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}
 
response = requests.request("GET", url, headers=headers, params=querystring)
 
new = response.json()
 
game_1 = json.dumps(new["response"][0], indent=4)
game_2 = json.dumps(new["response"][1], indent=4)
 
print(game_1, game_2)