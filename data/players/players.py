"""
This file pulls data from an API relating to the English Premier League 
players data and loads it into BigQuery.
"""

# System libraries
import os
import json

# Importing needed libraries.
from google.cloud import secretmanager
from google.cloud import bigquery
import pandas as pd
import requests

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

# Settings the project environment.
PLAYERS_TABLE = "cloud-data-infrastructure.premier_league_dataset.players"


def gcp_secret():
    """ Fetching RapidAPI key from Secret Manager """

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


def call_api():
    """ Calling the API then filling in the empty lists """

    payload = gcp_secret()
    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": payload,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }

    # Standings endpoint from RapidAPI.
    url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"

    # Building GET request to retrieve data.
    query = {"league": "39", "season": "2022"}
    response = requests.request("GET", url, headers=headers, params=query, timeout=20)
    json_res = response.json()

    # Empty lists that will be filled and then used to create a dataframe.
    full_name_list = []
    goals_list = []
    assists_list = []
    team_list = []
    nationality_list = []
    photo_list = []

    count = 0
    while count < 5:
        # Retrieving player's first and last name then combining for full name.
        first_name = (
            str(
                json.dumps(
                    json_res["response"][count]["player"]["firstname"],
                    ensure_ascii=False,
                )
            )
        ).strip('"')
        last_name = (
            str(
                json.dumps(
                    json_res["response"][count]["player"]["lastname"],
                    ensure_ascii=False,
                )
            )
        ).strip('"')

        full_name = first_name + " " + last_name

        full_name_list.append(full_name)

        # Retrieving amount of goals per player.
        goals_list.append(
            int(json_res["response"][count]["statistics"][0]["goals"]["total"])
        )

        # Retrieving amount of assists per player.
        assists_list.append(
            int(json_res["response"][count]["statistics"][0]["goals"]["assists"])
        )

        # Retrieving player's team name.
        team_list.append(
            str(json_res["response"][count]["statistics"][0]["team"]["name"]).strip('"')
        )

        # Retrieving player's nationality.
        nationality_list.append(
            str(json_res["response"][count]["player"]["nationality"]).strip('"')
        )

        # Retrieving player's photo link.
        photo_list.append(
            str(json_res["response"][count]["player"]["photo"]).strip('"')
        )

        count += 1

    return full_name_list, goals_list, team_list, assists_list, nationality_list, photo_list


def create_dataframe():
    """ This function creates a datafreame from lists created in the last function: call_api() """

    full_name_list, goals_list, team_list, assists_list, nationality_list, photo_list = call_api()

    # Setting the headers then zipping the lists.
    headers = ["name", "goals", "team", "assists", "nationality", "photo"]
    zipped = list(
        zip(full_name_list, goals_list, team_list, assists_list, nationality_list, photo_list)
    )

    df = pd.DataFrame(zipped, columns=headers)

    return df


class Players:
    """ Functions to drop and load the players table """

    def drop(self):
        """ Dropping the BigQuery table """

        client = bigquery.Client()
        query = f"""
            DROP TABLE
            {PLAYERS_TABLE}
        """

        client.query(query)

        print("Players table dropped...")

    def load(self):
        """ Loading the dataframe to the BigQuery table """

        df = create_dataframe()

        # Construct a BigQuery client object.
        client = bigquery.Client()

        table_id = PLAYERS_TABLE

        job = client.load_table_from_dataframe(df, table_id)  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.

        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")


# Creating an instance of the class.
players = Players()

if __name__ == "__main__":
    # Calling the functions.
    players.drop()
    players.load()
