from config import location_name, rapid_api, project_id
from google.cloud import bigquery
import pandas as pd
import requests
import json

# Standings endpoint from RapidAPI. Retrieving the ID for each team for the current season.
url_standings = "https://api-football-v1.p.rapidapi.com/v3/standings"

querystring_standings = {"season":"2022","league":"39"}

headers = {
	"X-RapidAPI-Key": rapid_api,
	"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

response_standings = requests.request("GET", url_standings, headers=headers, params=querystring_standings)

json_res_standings = response_standings.json()

id_list = []

count_standings = 0
while count_standings < 20:
	id_list.append(str(json.dumps(json_res_standings
	["response"][0]["league"]["standings"][0][count_standings]["team"]["id"])))

	count_standings += 1

id_int = [eval(team_id) for team_id in id_list]

# Team Information endpoint from RapidAPI.
team_list = []
city_list = []

for id in id_list:
	querystring = {"id":id}
	
	url = "https://api-football-v1.p.rapidapi.com/v3/teams"

	response = requests.request("GET", url, headers=headers, params=querystring)

	json_res = response.json()

	team_list.append(str(json.dumps(json_res
		["response"][0]["team"]["name"])))

	city_list.append(str(json.dumps(json_res
		["response"][0]["venue"]["city"])))

stripped_team = []
for team in team_list:
    team = team.strip('"')
    stripped_team.append(team)

stripped_city = []
for city in city_list:
    city = city.strip('"')
    city = city.split(',', 1)[0]
    stripped_city.append(city)

class Location:

	def drop(self):
		client = bigquery.Client()
		query = """
            DROP TABLE 
            {}.premier_league.location
        """.format(project_id)

		query_job = client.query(query)

		print("Location table dropped...")

	def table(self):
		headers = ['ID', 'Team', 'City']
		zipped = list(zip(id_int, stripped_team, stripped_city))

		df = pd.DataFrame(zipped, columns=headers)
		
		client = bigquery.Client(project=project_id)

		table_id = location_name

		job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
		job.result()  # Wait for the job to complete.

		table = client.get_table(table_id)  # Make an API request.
		print(
            "Loaded {} rows and {} columns".format(
                table.num_rows, len(table.schema)
            )
        )