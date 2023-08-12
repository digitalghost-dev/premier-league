"""
This file pulls data from an API relating to the English Premier League 
top scoring players data and loads it into a PostgreSQL database.
"""

import json
import os
from typing import Dict, Optional

import pandas as pd
import requests  # type: ignore
from google.cloud import secretmanager
from pandas import DataFrame
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.types import SMALLINT, String  # type: ignore

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


def gcp_secret_rapid_api() -> str:
    """This function retrieves the Rapid API key from GCP Secret Manager."""

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    rapid_api_key = response.payload.data.decode("UTF-8")

    return rapid_api_key


def gcp_secret_database_uri() -> str:
    """This function retrieves the database URI from GCP Secret Manager."""

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/premier-league-database-connection-uri/versions/3"
    response = client.access_secret_version(request={"name": name})
    database_uri = response.payload.data.decode("UTF-8")

    return database_uri


def call_api() -> (
    tuple[list[str], list[int], list[str], list[int], list[str], list[str]]
):
    """Calling the API then filling in the empty lists"""

    rapid_api_key = gcp_secret_rapid_api()
    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
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

    return (
        full_name_list,
        goals_list,
        team_list,
        assists_list,
        nationality_list,
        photo_list,
    )


def create_dataframe() -> DataFrame:
    """This function creates a datafreame from lists created in the last function: call_api()"""

    (
        full_name_list,
        goals_list,
        team_list,
        assists_list,
        nationality_list,
        photo_list,
    ) = call_api()

    # Setting the headers then zipping the lists.
    headers = ["name", "goals", "team", "assists", "nationality", "photo"]
    zipped = list(
        zip(
            full_name_list,
            goals_list,
            team_list,
            assists_list,
            nationality_list,
            photo_list,
        )
    )

    df = pd.DataFrame(zipped, columns=headers)

    return df


def define_table_schema() -> Dict[str, type]:
    """This function defines the table schema for the PostgreSQL table."""

    schema_definition = {
        "name": String(64),
        "goals": SMALLINT,
        "team": String(64),
        "assists": SMALLINT,
        "nationality": String(64),
        "photo": String(256),
    }

    return schema_definition


def send_dataframe_to_postgresql(
    database_uri: str,
    schema_name: str,
    table_name: str,
    df: DataFrame,
    schema_definition: Optional[Dict[str, type]] = None,
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
    df.to_sql(
        table_name,
        con=engine,
        schema=schema_name,
        if_exists="replace",
        index=False,
        dtype=schema_definition,
    )


if __name__ != "__main__":
    uri = gcp_secret_database_uri()
    schema = "premier-league-schema"
    table = "top_scorers"
    dataframe = create_dataframe()

    send_dataframe_to_postgresql(uri, schema, table, dataframe)
    print(f"Data loaded into {table}!")
