# Importing needed modules.
from google.cloud import bigquery
import pandas as pd
import requests
import json
import os

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

standings_table = "cloud-data-infrastructure.football_data_dataset.standings"
teams_table = "cloud-data-infrastructure.football_data_dataset.teams"


def gcp_secret():
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


# Function to call the Teams table in BigQuery.
def bigquery_call():
    bqclient = bigquery.Client()

    # SQL query
    query_string = f"""
    SELECT *
    FROM {standings_table}
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


# Function to call the Football API.
def call_api():
    payload = gcp_secret()
    bigquery_dataframe = bigquery_call()

    # Iterate through bigquery_dataframe to get the team's id and create a list using list comprehension.
    id_list = [bigquery_dataframe.iloc[i][0] for i in range(20)]

    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": payload,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }

    # Standings endpoint from RapidAPI.
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"

    # Empty lists that will be filled and then used to create a dataframe.
    team_list = []
    logo_list = []
    form_list = []
    clean_sheets_list = []
    penalty_scored_list = []
    penalty_missed_list = []

    count = 0
    while count < 20:
        # Building query to retrieve data.
        query = {"league": "39", "season": "2022", "team": id_list[count]}
        response = requests.request("GET", url, headers=headers, params=query)
        json_res = response.json()

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

        count += 1

    return (
        team_list,
        logo_list,
        form_list,
        clean_sheets_list,
        penalty_scored_list,
        penalty_missed_list,
    )


# Function to build the dataframe from the lists in the previous function.
def create_dataframe():
    (
        team_list,
        logo_list,
        form_list,
        clean_sheets_list,
        penalty_scored_list,
        penalty_missed_list,
    ) = call_api()

    # Setting the headers then zipping the lists to create a dataframe.
    headers = [
        "team",
        "logo",
        "form",
        "clean_sheets",
        "penalties_scored",
        "penalties_missed",
    ]
    zipped = list(
        zip(
            team_list,
            logo_list,
            form_list,
            clean_sheets_list,
            penalty_scored_list,
            penalty_missed_list,
        )
    )

    df = pd.DataFrame(zipped, columns=headers)

    return df


class Teams:
    # Dropping BigQuery table.
    def drop(self):
        client = bigquery.Client()
        query = f"""
            DROP TABLE 
            {teams_table}
        """

        query_job = client.query(query)

        print("Teams table dropped...")

    def load(self):
        df = create_dataframe()  # Getting dataframe creating in dataframe() function.

        # Construct a BigQuery client object.
        client = bigquery.Client(project="cloud-data-infrastructure")

        table_id = teams_table

        job = client.load_table_from_dataframe(df, table_id)  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.

        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")


# Creating an instance of the class.
teams = Teams()

# Calling the functions.
teams.drop()
teams.load()
