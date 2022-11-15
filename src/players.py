# Importing needed libraries.
from config import players_name, rapid_api, project_id
from google.cloud import bigquery
import pandas as pd
import requests
import json

def call_api():
	# Headers used for RapidAPI.
	headers = {
		"X-RapidAPI-Key": rapid_api,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
	}

	# Standings endpoint from RapidAPI.
	url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"

	# Building query to retrieve data.
	query = {"league":"39","season":"2022"}
	response = requests.request("GET", url, headers=headers, params=query)
	json_res = response.json()

	return json_res

def players():
	json_res = call_api()

	# Empty lists that will be filled and then used to create a dataframe.
	full_name_list = []
	goals_list = []
	team_list = []
	nationality_list = []

	count = 0
	while count < 5:

		# Getting player's first and last name then combining for full name.
		first_name = (str(json.dumps(json_res["response"][count]["player"]["firstname"], ensure_ascii=False))).strip('"')
		last_name = (str(json.dumps(json_res["response"][count]["player"]["lastname"], ensure_ascii=False))).strip('"')

		full_name = first_name + " " + last_name
		
		full_name_list.append(full_name)

		# Getting amount of goals per player.
		goals_list.append(int(json.dumps(json_res["response"][count]["statistics"][0]["goals"]["total"])))

		# Getting player's team name
		team_list.append(((str(json.dumps(json_res["response"][count]["statistics"][0]["team"]["name"])).strip('"'))))

		# Getting player's nationality
		nationality_list.append((str(json.dumps(json_res["response"][count]["player"]["nationality"])).strip('"')))

		count += 1
	
	return full_name_list, goals_list, team_list, nationality_list

def dataframe():
	full_name_list, goals_list, team_list, nationality_list = players()

	# Setting the headers then zipping the lists to create a dataframe.
	headers = ['Name', 'Goals', 'Team', 'Nationality']
	zipped = list(zip(full_name_list, goals_list, team_list, nationality_list))

	df = pd.DataFrame(zipped, columns=headers)

	return df

class Players:

	# Dropping BigQuery table.
	def drop(self):
		client = bigquery.Client()
		query = """
            DROP TABLE 
            {}.premier_league.players
        """.format(project_id)

		query_job = client.query(query)

		print("Players table dropped...")

	def load(self):
		df = dataframe() # Getting dataframe creating in dataframe() function.
		
		# Construct a BigQuery client object.
		client = bigquery.Client(project=project_id)

		table_id = players_name

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