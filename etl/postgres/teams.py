"""
This file pulls data from an API relating to the English Premier League
teams data and loads it into a PostgreSQL database.
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
from sqlalchemy.types import SMALLINT, String  # type: ignore

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

# Database details
schema = "premier-league-schema"
standings_table = "standings"
teams_table = "teams"


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


def postgres_call():
    """Fetching the Standings table from PostgreSQL"""
    database_uri = gcp_secret_database_uri()

    sqlcon = create_engine(database_uri)

    # SQL query
    query_string = f"""
        SELECT team_id, rank
        FROM "{schema}"."{standings_table}"
        ORDER BY Rank
        """

    standings_df = pd.read_sql(query_string, sqlcon)
    return standings_df


def call_api():
    """Calling the API then filling in the empty lists"""

    rapid_api_key = gcp_secret_rapid_api()
    standings_df = postgres_call()

    # Iterate through bigquery_dataframe to get the team's id and create a list using list comprehension.
    id_list = [standings_df.iloc[i][0] for i in range(20)]

    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": rapid_api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }

    # Standings endpoint from RapidAPI.
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"

    # Empty lists that will be filled and then used to create a dataframe.
    team_id_list = []
    team_list = []
    logo_list = []
    form_list = []
    clean_sheets_list = []
    penalty_scored_list = []
    penalty_missed_list = []
    average_goals_list = []
    win_streak_list = []

    count = 0
    while count < 20:
        # Building GET request to retrieve data.
        query = {"league": "39", "season": "2023", "team": id_list[count]}
        response = requests.request("GET", url, headers=headers, params=query)
        json_res = response.json()

        # Team ID.
        team_id_list.append(int(json_res["response"]["team"]["id"]))

        # Team's name.
        team_list.append(str(json_res["response"]["team"]["name"]))

        # Team's logo.
        logo_list.append(str(json_res["response"]["team"]["logo"]))

        # Team's form.
        form_list.append(str(json_res["response"]["form"]))

        # Team's total clean sheets.
        clean_sheets_list.append(int(json_res["response"]["clean_sheet"]["total"]))

        # Team's total penalties scored.
        penalty_scored_list.append(
            int(json_res["response"]["penalty"]["scored"]["total"])
        )

        # Team's total penalties missed.
        penalty_missed_list.append(
            int(json_res["response"]["penalty"]["missed"]["total"])
        )

        # Team's average goals.
        average_goals_list.append(
            float(json_res["response"]["goals"]["for"]["average"]["total"])
        )

        # Team's win streak.
        win_streak_list.append(int(json_res["response"]["biggest"]["streak"]["wins"]))

        count += 1

    return (
        team_id_list,
        team_list,
        logo_list,
        form_list,
        clean_sheets_list,
        penalty_scored_list,
        penalty_missed_list,
        average_goals_list,
        win_streak_list,
    )


def create_dataframe():
    """This function creates a datafreame from lists created in the last function: call_api()"""

    (
        team_id_list,
        team_list,
        logo_list,
        form_list,
        clean_sheets_list,
        penalty_scored_list,
        penalty_missed_list,
        average_goals_list,
        win_streak_list,
    ) = call_api()

    # Setting the headers then zipping the lists to create a dataframe.
    headers = [
        "team_id",
        "team",
        "logo",
        "form",
        "clean_sheets",
        "penalties_scored",
        "penalties_missed",
        "average_goals",
        "win_streak",
    ]
    zipped = list(
        zip(
            team_id_list,
            team_list,
            logo_list,
            form_list,
            clean_sheets_list,
            penalty_scored_list,
            penalty_missed_list,
            average_goals_list,
            win_streak_list,
        )
    )

    df = pd.DataFrame(zipped, columns=headers)

    return df


def define_table_schema() -> Dict[str, type]:
    schema_definition = {
        "team_id": SMALLINT,
        "team": String(64),
        "logo": String(256),
        "form": String(24),
        "clean_sheets": SMALLINT,
        "penalties_scored": SMALLINT,
        "penalties_missed": SMALLINT,
        "average_goals": SMALLINT,
        "win_streak": SMALLINT,
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
    table_name = "teams"
    df = create_dataframe()
    schema_definition = define_table_schema()

    send_dataframe_to_postgresql(database_uri, schema_name, table_name, df)
    print(f"Data loaded into {table_name}!")
