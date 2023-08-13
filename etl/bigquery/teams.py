"""
This file pulls data from an API relating to the English Premier League
teams data and loads it into a PostgreSQL database.
"""

import os

import pandas as pd
import requests  # type: ignore

# Importing needed libraries.
from google.cloud import bigquery, secretmanager
from pandas import DataFrame

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

# Setting table names.
STANDINGS_TABLE = "premier_league_dataset.standings"
TEAMS_TABLE = "premier_league_dataset.teams"


def gcp_secret_rapid_api():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    rapid_api_key = response.payload.data.decode("UTF-8")

    return rapid_api_key


# Function to call the Teams table in BigQuery.
def bigquery_call():
    bqclient = bigquery.Client()

    # SQL query
    query_string = f"""
        SELECT *
        FROM {STANDINGS_TABLE}
        ORDER BY Rank
    """

    pd.dataframe = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(
            create_bqstorage_client=True,
        )
    )

    bigquery_dataframe = pd.dataframe

    return bigquery_dataframe


def call_api() -> (
    tuple[
        list[int],
        list[str],
        list[str],
        list[str],
        list[int],
        list[int],
        list[int],
        list[float],
        list[int],
    ]
):
    """Calling the API then filling in the empty lists"""

    rapid_api_key = gcp_secret_rapid_api()
    bigquery_dataframe = bigquery_call()

    # Iterate through bigquery_dataframe to get the team's id and create a list using list comprehension.
    id_list = [bigquery_dataframe.iloc[i][0] for i in range(20)]

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


def create_dataframe() -> DataFrame:
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


def define_table_schema() -> list[dict[str, str]]:
    schema_definition = [
        {"name": "team_id", "type": "INTEGER"},
        {"name": "team", "type": "STRING"},
        {"name": "logo", "type": "STRING"},
        {"name": "form", "type": "STRING"},
        {"name": "clean_sheets", "type": "INTEGER"},
        {"name": "penalties_scored", "type": "INTEGER"},
        {"name": "penalties_missed", "type": "INTEGER"},
        {"name": "average_goals", "type": "INTEGER"},
        {"name": "win_streak", "type": "INTEGER"},
    ]

    return schema_definition


def send_dataframe_to_bigquery(
    standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]
) -> None:
    teams_dataframe.to_gbq(
        destination_table="premier_league_dataset.teams",
        if_exists="replace",
        table_schema=schema_definition,
    )

    print("Teams table loaded!")


if __name__ == "__main__":
    teams_dataframe = create_dataframe()
    schema_definition = define_table_schema()
    send_dataframe_to_bigquery(teams_dataframe, schema_definition)
