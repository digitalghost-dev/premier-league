"""
This file pulls data from an API relating to the English Premier League stadium location data and loads it into BigQuery.
"""

# System libraries
import os

# Importing needed libraries.
from google.cloud import secretmanager
from google.cloud import bigquery
import pandas as pd
import requests

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

# Settings the project environment.
LOCATIONS_TABLE = "cloud-data-infrastructure.football_data_dataset.locations"


def gcp_secret():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/locations_api/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload


def call_api():
    payload = gcp_secret()
    # Building query to retrieve data.
    response = requests.request("GET", payload, timeout=20)
    json_res = response.json()

    # Empty lists that will be filled and then used to create a dataframe.
    team_list = []
    stadium_list = []
    lat_list = []
    lon_list = []

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

        count += 1

    return team_list, stadium_list, lat_list, lon_list


def dataframe():
    team_list, stadium_list, lat_list, lon_list = call_api()

    # Setting the headers then zipping the lists to create a dataframe.
    headers = ["team", "stadium", "latitude", "longitude"]
    zipped = list(zip(team_list, stadium_list, lat_list, lon_list))

    locations_df = pd.DataFrame(zipped, columns=headers)

    return locations_df


class Locations:
    """Functions to drop and load the locations table."""

    def drop(self):
        client = bigquery.Client()
        query = f"""
            DROP TABLE 
            {LOCATIONS_TABLE}
        """

        client.query(query)

        print("Location table dropped...")

    def load(self):
        locations_df = (
            dataframe()
        )  # Getting dataframe creating in dataframe() function.

        client = bigquery.Client()

        job = client.load_table_from_dataframe(
            locations_df, LOCATIONS_TABLE
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(LOCATIONS_TABLE)  # Make an API request.

        print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")


# Creating an instance of the class.
locations = Locations()

# Calling the functions.
locations.drop()
locations.load()
