"""
This file pulls data from an API relating to the English Premier League standings data and loads it into a PostgreSQL database.
"""

# Standard libraries
from typing import Dict, Optional
import json
import os

# Importing needed libraries.
from google.cloud import secretmanager
from sqlalchemy import create_engine
from sqlalchemy.types import *
from pandas import DataFrame
import pandas as pd
import requests

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

def gcp_secret_rapid_api():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    rapid_api_key = response.payload.data.decode("UTF-8")

    return rapid_api_key

def gcp_secret_database_uri():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/premier-league-database-connection-uri/versions/2"
    response = client.access_secret_version(request={"name": name})
    database_uri = response.payload.data.decode("UTF-8")

    return database_uri


def call_api():
    """Calling the API then filling in the empty lists"""

    payload = gcp_secret_rapid_api()
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


def create_dataframe():
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
        "team_id",
        "rank",
        "team",
        "wins",
        "draws",
        "loses",
        "recent_form",
        "points",
        "goals_for",
        "goals_against",
        "goal_difference",
        "position_status",
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

def define_table_schema() -> Dict[str, type]:
    schema_definition = {
        "team_id": SMALLINT,    
        "rank": SMALLINT,
        "team": String(64),
        "wins": SMALLINT,
        "draws": SMALLINT,
        "loses": SMALLINT,
        "recent_form": String(5), 
        "points": String(4),
        "goals_for": SMALLINT,
        "goals_against": SMALLINT,
        "goal_difference": SMALLINT,
        "position_status": String(12)
    }

    return schema_definition

def send_dataframe_to_postgresql(
        database_uri: str, 
        schema_name: str, 
        table_name: str,
        df: DataFrame, 
        schema_definition: Optional[Dict[str, type]] = None
    ):
    """Sending dataframe to PostgreSQL.

    Args:
        database_uri (str): The URI to connect to the PostgreSQL database.
        schema (str): The schema name in which the table should be created.
        table_name (str): The name of the table to be created.
        df (DataFrame): The DataFrame containing the data to be inserted.
        schema_definition (Dict[str, type], optional): A dictionary defining the table schema with column names
                                                       as keys and their corresponding SQLAlchemy data types.
                                                       Defaults to None. If None, the function will use the schema
                                                       from the define_table_schema() function.

    Raises:
        ValueError: If the DataFrame is empty or schema_definition is not a valid dictionary.
    """

    if df.empty:
        raise ValueError("DataFrame is empty.")

    if schema_definition is None:
        schema_definition = define_table_schema()

    if not isinstance(schema_definition, dict):
        raise ValueError("schema_definition must be a dictionary.")

    engine = create_engine(database_uri)
    df.to_sql(table_name, con=engine, schema=schema_name, if_exists="replace", index=False, dtype=schema_definition)


if __name__ == "__main__":
    database_uri = gcp_secret_database_uri()
    schema_name = "premier-league-schema"
    table_name = "standings"
    df = create_dataframe()
    schema_definition = define_table_schema()

    send_dataframe_to_postgresql(database_uri, schema_name, table_name, df)
    print(f"Data loaded into {table_name}!")
