# Importing needed libraries.
from google.cloud import bigquery
import pandas as pd
import requests
import json
import os

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

players_table = "cloud-data-infrastructure.football_data_dataset.players"

def gcp_secret():
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
	
    return payload

def call_api():
	payload = gcp_secret()
	# Headers used for RapidAPI.
	headers = {
		"X-RapidAPI-Key": payload,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
	}

	# Standings endpoint from RapidAPI.
	url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"

	# Building query to retrieve data.
	query = {"league":"39","season":"2022"}
	response = requests.request("GET", url, headers=headers, params=query)
	json_res = response.json()

	# Empty lists that will be filled and then used to create a dataframe.
	full_name_list = []
	goals_list = []
	team_list = []
	nationality_list = []
	photo_list = []

	count = 0
	while count < 5:

		# Retrieving player's first and last name then combining for full name.
		first_name = (str(json.dumps(json_res["response"][count]["player"]["firstname"], ensure_ascii=False))).strip('"')
		last_name = (str(json.dumps(json_res["response"][count]["player"]["lastname"], ensure_ascii=False))).strip('"')

		full_name = first_name + " " + last_name
		
		full_name_list.append(full_name)

		# Retrieving amount of goals per player.
		goals_list.append(int(json.dumps(json_res["response"][count]["statistics"][0]["goals"]["total"])))

		# Retrieving player's team name.
		team_list.append(((str(json.dumps(json_res["response"][count]["statistics"][0]["team"]["name"])).strip('"'))))

		# Retrieving player's nationality.
		nationality_list.append((str(json.dumps(json_res["response"][count]["player"]["nationality"])).strip('"')))

		# Retrieving player's photo link.
		photo_list.append(str(json.dumps(json_res["response"][count]["player"]["photo"])).strip('"'))

		count += 1
	
	return full_name_list, goals_list, team_list, nationality_list, photo_list

def dataframe():
	full_name_list, goals_list, team_list, nationality_list, photo_list = call_api()

	# Setting the headers then zipping the lists to create a dataframe.
	headers = ['name', 'goals', 'team', 'nationality', 'photo']
	zipped = list(zip(full_name_list, goals_list, team_list, nationality_list, photo_list))

	df = pd.DataFrame(zipped, columns = headers)

	return df

class Players:

	# Dropping BigQuery table.
	def drop(self):
		client = bigquery.Client()
		query = f"""
            DROP TABLE 
            {players_table}
        """

		query_job = client.query(query)

		print("Players table dropped...")

	def load(self):
		df = dataframe() # Getting dataframe creating in dataframe() function.
		
		# Construct a BigQuery client object.
		client = bigquery.Client(project="cloud-data-infrastructure")

		table_id = players_table

		job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
		job.result()  # Wait for the job to complete.

		table = client.get_table(table_id)  # Make an API request.

		print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")

# Creating an instance of the class.
players = Players()

# Calling the functions.
players.drop()
players.load()