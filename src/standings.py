# Importing needed modules.
from google.cloud import bigquery
import pandas as pd
import requests
import json

standings_table = "cloud-data-infrastructure.football_data_dataset.standings"

def gcp_secret():
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = "projects/463690670206/secrets/rapid-api/versions/1"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    payload = response.payload.data.decode("UTF-8")
    return payload

# Function to call the Football API.
def call_api():
    payload = gcp_secret()
    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": payload,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    # Standings endpoint from RapidAPI.
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"

    # Building query to retrieve data.
    query = {"season":"2022","league":"39"}
    response = requests.request("GET", url, headers=headers, params=query)
    json_res = response.json()

    return json_res

def standings():
    json_res = call_api()

    # Empty lists that will be filled and then used to create a dataframe.
    id_list = []
    rank_list = []
    team_list = []
    wins_list = []
    draws_list = []
    loses_list = []
    points_list = []
    goals_for = []
    goals_against = []
    goals_diff = []

    # Filling in empty lists.
    count = 0
    while count < 20:
        # Team ID.
        id_list.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["team"]["id"])))

        # Team rank.
        rank_list.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["rank"])))

        # Team names.
        team_list.append(str(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["team"]["name"])).strip('"'))

        # Number of wins.
        wins_list.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["all"]["win"])))

        # Number of draws.
        draws_list.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["all"]["draw"])))

        # Number of loses.
        loses_list.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["all"]["lose"])))

        # Number of points.
        points_list.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["points"])))

        # Number of goals for.
        goals_for.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["all"]["goals"]["for"])))

        # Number of goals against.
        goals_against.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["all"]["goals"]["against"])))

        # Number of goal differential.
        goals_diff.append(int(json.dumps(json_res
            ["response"][0]["league"]["standings"][0][count]["goalsDiff"])))
            
        count += 1

    return id_list, rank_list, team_list, wins_list, draws_list, loses_list, points_list, goals_for, goals_against, goals_diff

# Function to build the dataframe from the lists in the previous function.
def dataframe():
	id_list, rank_list, team_list, wins_list, draws_list, loses_list, points_list, goals_for, goals_against, goals_diff = standings()

	# Setting the headers then zipping the lists to create a dataframe.
	headers = ['ID', 'Rank', 'Team', 'Wins', 'Draws', 'Loses', 'Points', 'GF', 'GA', 'GD']
	zipped = list(zip(id_list, rank_list, team_list, wins_list, draws_list, loses_list, points_list, goals_for, goals_against, goals_diff))

	df = pd.DataFrame(zipped, columns=headers)

	return df

class Standings:

    # Dropping BigQuery table.
    def drop(self):
        client = bigquery.Client()
        query = f"""
            DROP TABLE 
            {standings_table}
        """

        query_job = client.query(query)

        print("Standings table dropped...")

    def load(self):
        df = dataframe() # Getting dataframe creating in dataframe() function.

        # Construct a BigQuery client object.
        client = bigquery.Client(project="cloud-data-infrastructure")

        table_id = standings_table

        job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        
        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")