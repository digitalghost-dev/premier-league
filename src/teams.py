# Importing needed modules.
from config import standings_table, teams_table, rapid_api, project_id
from google.cloud import bigquery
import pandas as pd
import requests
import json

# Function to call the Teams table in BigQuery.
def call_bigquery():

    bqclient = bigquery.Client()

    # SQL query
    query_string = f"""
    SELECT *
    FROM {standings_table}
    ORDER BY Rank
    LIMIT 5
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
    bigquery_dataframe = call_bigquery()

    id_list = [bigquery_dataframe.iloc[0][0], 
                bigquery_dataframe.iloc[1][0], 
                bigquery_dataframe.iloc[2][0],
                bigquery_dataframe.iloc[3][0],
                bigquery_dataframe.iloc[4][0]]

    # Headers used for RapidAPI.
    headers = {
        "X-RapidAPI-Key": rapid_api,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    # Standings endpoint from RapidAPI.
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"

    # Empty lists that will be filled and then used to create a dataframe.
    logo_list = []
    form_list = []
    clean_sheets_list = []
    penalty_scored_list = []
    penalty_missed_list = []

    count = 0
    while count < 5:
        # Building query to retrieve data.
        query = {"league": "39", "season": "2022", "team": id_list[count]}
        response = requests.request("GET", url, headers=headers, params=query)
        json_res = response.json()

        # Team's logo.
        logo_list.append(str(json_res["response"]["team"]["logo"]))

        # Team's form.
        form_list.append(str(json_res["response"]["form"]))

        # Team's total clean sheets.
        clean_sheets_list.append(int(json_res["response"]["clean_sheet"]["total"]))

        # Team's total penalties scored.
        penalty_scored_list.append(int(json_res["response"]["penalty"]["scored"]["total"]))

        # Team's total penalties missed.
        penalty_missed_list.append(int(json_res["response"]["penalty"]["missed"]["total"]))

        count += 1

    return logo_list, form_list, clean_sheets_list, penalty_scored_list, penalty_missed_list

# Function to build the dataframe from the lists in the previous function.
def dataframe():
    logo_list, form_list, clean_sheets_list, penalty_scored_list, penalty_missed_list = call_api()

    # Setting the headers then zipping the lists to create a dataframe.
    headers = ['logo', 'form', 'clean_sheets', 'penalties_scored', 'penalties_missed']
    zipped = list(zip(logo_list, form_list, clean_sheets_list, penalty_scored_list, penalty_missed_list))

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
        df = dataframe() # Getting dataframe creating in dataframe() function.

        # Construct a BigQuery client object.
        client = bigquery.Client(project=project_id)

        table_id = teams_table

        job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        
        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")