"""
This file pulls data from an API relating to the English Premier League standings data and loads it into BigQuery.
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

# Setting table names.
STANDINGS_TABLE = "cloud-data-infrastructure.premier_league_dataset.standings"


def gcp_secret():
    """Fetching RapidAPI key from Secret Manager"""

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


def call_api():
    """Calling the API then filling in the empty lists"""

    payload = gcp_secret()
    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": payload,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }

    # Standings endpoint from RapidAPI.
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"

    # Building GET request to retrieve data.
    query = {"season": "2023", "league": "39"}
    response = requests.request("GET", url, headers=headers, params=query)
    json_res = response.json()

    # Empty lists that will be filled and then used to create a dataframe.
    team_id_list = []
    rank_list = []
    team_list = []
    wins_list = []
    draws_list = []
    loses_list = []
    form_list = []
    points_list = []
    goals_for = []
    goals_against = []
    goals_diff = []
    status_list = []

    # Filling in empty lists.
    count = 0
    while count < 20:
        # Team ID.
        team_id_list.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["team"]["id"])
        )

        # Team rank.
        rank_list.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["rank"])
        )

        # Team names.
        team_list.append(
            str(
                json.dumps(
                    json_res["response"][0]["league"]["standings"][0][count]["team"][
                        "name"
                    ]
                )
            ).strip('"')
        )

        # Number of wins.
        wins_list.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["all"]["win"])
        )

        # Number of draws.
        draws_list.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["all"]["draw"])
        )

        # Number of loses.
        loses_list.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["all"]["lose"])
        )

        # Team forms.
        form_list.append(
            str(
                json.dumps(
                    json_res["response"][0]["league"]["standings"][0][count]["form"]
                )
            ).strip('"')
        )

        # Number of points.
        points_list.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["points"])
        )

        # Number of goals for.
        goals_for.append(
            int(
                json_res["response"][0]["league"]["standings"][0][count]["all"][
                    "goals"
                ]["for"]
            )
        )

        # Number of goals against.
        goals_against.append(
            int(
                json_res["response"][0]["league"]["standings"][0][count]["all"][
                    "goals"
                ]["against"]
            )
        )

        # Number of goal differential.
        goals_diff.append(
            int(json_res["response"][0]["league"]["standings"][0][count]["goalsDiff"])
        )

        # Each team's position status.
        status_list.append(
            str(json_res["response"][0]["league"]["standings"][0][count]["status"])
        )

        count += 1

    return (
        team_id_list,
        rank_list,
        team_list,
        wins_list,
        draws_list,
        loses_list,
        form_list,
        points_list,
        goals_for,
        goals_against,
        goals_diff,
        status_list,
    )


def dataframe():
    """This function creates a datafreame from lists created in the last function: call_api()"""

    (
        team_id_list,
        rank_list,
        team_list,
        wins_list,
        draws_list,
        loses_list,
        form_list,
        points_list,
        goals_for,
        goals_against,
        goals_diff,
        status_list,
    ) = call_api()

    # Setting the headers then zipping the lists to create a dataframe.
    headers = [
        "Team_ID",
        "Rank",
        "Team",
        "Wins",
        "Draws",
        "Loses",
        "Recent_Form",
        "Points",
        "GF",
        "GA",
        "GD",
        "Status",
    ]
    zipped = list(
        zip(
            team_id_list,
            rank_list,
            team_list,
            wins_list,
            draws_list,
            loses_list,
            form_list,
            points_list,
            goals_for,
            goals_against,
            goals_diff,
            status_list,
        )
    )

    df = pd.DataFrame(zipped, columns=headers)

    return df


class Standings:
    """Functions to drop and load the standings table"""

    def drop(self):
        """Dropping the BigQuery table"""

        client = bigquery.Client()

        query = f"""
            DROP TABLE 
            {STANDINGS_TABLE}
        """

        query_job = client.query(query)

        print("Standings table dropped...")

    def load(self):
        """Loading the dataframe to the BigQuery table"""

        df = dataframe()

        # Construct a BigQuery client object.
        client = bigquery.Client()

        job = client.load_table_from_dataframe(
            df, STANDINGS_TABLE
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(STANDINGS_TABLE)  # Make an API request.

        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")


# Creating an instance of the class.
standings = Standings()

if __name__ == "__main__":
    # Calling the functions.
    standings.drop()
    standings.load()
