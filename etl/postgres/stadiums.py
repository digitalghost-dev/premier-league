"""
This file pulls data from an API relating to the English Premier League
stadium location data and loads it into a PostgreSQL database.
"""

import os

# Standard libraries
from typing import Dict, Optional

import pandas as pd
import requests  # type: ignore

# Importing needed libraries.
from google.cloud import secretmanager
from pandas import DataFrame
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.types import DECIMAL, String  # type: ignore

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


def gcp_secret_rapid_api():
    """Fetching RapidAPI key from Secret Manager"""

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/go-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    go_api_key = response.payload.data.decode("UTF-8")

    return go_api_key


def gcp_secret_database_uri():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/premier-league-database-connection-uri/versions/3"
    response = client.access_secret_version(request={"name": name})
    database_uri = response.payload.data.decode("UTF-8")

    return database_uri


def call_api():
    """Calling the API then filling in the empty lists"""

    go_api_key = gcp_secret_rapid_api()

    # Building GET request to retrieve data.
    response = requests.request("GET", go_api_key, timeout=20)
    json_res = response.json()

    # Empty lists that will be filled and then used to create a dataframe.
    team_list = []
    stadium_list = []
    lat_list = []
    lon_list = []
    capacity_list = []
    year_opened = []

    count = 0
    while count < 20:
        # Retrieving team name.
        team_list.append(str(json_res[count]["team"]))

        # Retrieving stadium name.
        stadium_list.append(str(json_res[count]["stadium"]))

        # Retrieving stadium's latitude.
        lat_list.append(float(json_res[count]["latitude"]))

        # Retrieving stadium's longitude.
        lon_list.append(float(json_res[count]["longitude"]))

        # Retrieving stadium's capacity.
        capacity_list.append(str(json_res[count]["capacity"]))

        # Retrieving stadium's year opened.
        year_opened.append(str(json_res[count]["year_opened"]))

        count += 1

    return team_list, stadium_list, lat_list, lon_list, capacity_list, year_opened


def create_dataframe():
    """This function creates a datafreame from lists created in the last function: call_api()"""

    team_list, stadium_list, lat_list, lon_list, capacity_list, year_opened = call_api()

    # Setting the headers then zipping the lists to create a dataframe.
    headers = ["team", "stadium", "latitude", "longitude", "capacity", "year_opened"]
    zipped = list(
        zip(team_list, stadium_list, lat_list, lon_list, capacity_list, year_opened)
    )

    df = pd.DataFrame(zipped, columns=headers)

    return df


def define_table_schema() -> Dict[str, type]:
    schema_definition = {
        "team": String(64),
        "stadium": String(64),
        "latitude": DECIMAL(8, 6),
        "longitude": DECIMAL(8, 6),
        "capacity": String(10),
        "year_opened": String(4),
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
    database_uri = gcp_secret_database_uri()
    schema_name = "premier-league-schema"
    table_name = "stadiums"
    df = create_dataframe()
    schema_definition = define_table_schema()

    send_dataframe_to_postgresql(database_uri, schema_name, table_name, df)
    print(f"Data loaded into {table_name}!")
