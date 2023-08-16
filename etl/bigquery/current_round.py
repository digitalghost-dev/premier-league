"""
This file pulls data from an API relating to the English Premier League
current round data and loads it into a BigQuery table.
"""

import os

import pandas as pd
import requests  # type: ignore

# Importing needed libraries.
from google.cloud import secretmanager
from pandas import DataFrame

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


# Retrieving GCP Secret and calling RapidAPI.
def gcp_secret_rapid_api() -> str:
    """This function retrieves the Rapid API key from GCP Secret Manager"""

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    rapid_api_key = response.payload.data.decode("UTF-8")

    return rapid_api_key


# Retrieving data for the current round.
def call_api() -> str:
    """This function calls the API then returns the current round"""

    payload = gcp_secret_rapid_api()
    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": payload,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/rounds"
    querystring = {"league": "39", "season": "2023", "current": "true"}
    response = requests.get(url, headers=headers, params=querystring, timeout=10)

    current_round_response = response.json()["response"][0]

    return current_round_response


def create_dataframe() -> DataFrame:
    """This function creates a dataframe from the API response."""

    current_round_response = call_api()

    # Spliting a string that looks like: "Regular Season - 12"
    regular_season = [current_round_response[:14]]
    round_number = [current_round_response[17:]]
    round_number_int = int(round_number[0])

    data = {"season": regular_season, "round": round_number_int}

    # create a pandas dataframe from the dictionary
    df = pd.DataFrame(data, columns=["season", "round"])

    return df, round_number_int


def define_table_schema() -> list[dict[str, str]]:
    """This function defines the table schema for the BigQuery table."""

    schema_definition = [
        {"name": "season", "type": "STRING"},
        {"name": "round", "type": "INTEGER"},
    ]

    return schema_definition


# Tranforming data and loading into the PostgreSQL database.
def send_dataframe_to_bigquery(
    current_round_dataframe: DataFrame, schema_definition: list[dict[str, str]]
) -> None:
    """This function sends the dataframe to BigQuery."""
    current_round_dataframe, round_number_int = create_dataframe()

    current_round_dataframe.to_gbq(
        destination_table="premier_league_dataset.current_round",
        if_exists="append",
        table_schema=schema_definition,
    )

    print(f"Current round: {round_number_int} loaded!")


if __name__ == "__main__":
    current_round_dataframe = create_dataframe()
    schema_definition = define_table_schema()
    send_dataframe_to_bigquery(current_round_dataframe, schema_definition)
