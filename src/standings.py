# Importing needed modules
from config import table_name, rapid_api, project_id
from google.cloud import bigquery
import pandas as pd
import numpy as np
import requests
import json

url = "https://api-football-v1.p.rapidapi.com/v3/standings"

querystring = {"season":"2022","league":"39"}

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

# Removing the quotation marks from the team name.
stripped_team = []
for team in team_list:
    team = team.strip('"')
    stripped_team.append(team)

class Standings:

    # Dropping BigQuery table
    def drop(self):
        client = bigquery.Client()
        query = """
            DROP TABLE 
            {}.european_football_leagues.england
        """.format(project_id)

        query_job = client.query(query)

        print("Table dropped...")

    def table(self):
        headers = ['Rank', 'Team', 'Wins', 'Draws', 'Loses', 'Points']
        zipped = list(zip(rank_list, stripped_team, wins_list, draws_list, loses_list, points_list))

        df = pd.DataFrame(zipped, columns=headers)

        # Construct a BigQuery client object.
        client = bigquery.Client(project=project_id)

        table_id = table_name

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