# Importing needed libraries.
from google.cloud import bigquery
import pandas as pd
import requests
import json

locations_table = "cloud-data-infrastructure.football_data_dataset.locations"

def gcp_secret():
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = "projects/463690670206/secrets/locations_api/versions/1"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    payload = response.payload.data.decode("UTF-8")
    return payload

def call_api():
	payload = gcp_secret()
	# Building query to retrieve data.
	response = requests.request("GET", payload)
	json_res = response.json()

	return json_res

def locations():
	json_res = call_api()	

	# Empty lists that will be filled and then used to create a dataframe.
	team_list = []
	stadium_list = []
	lat_list = []
	lon_list = []

	count = 0
	while count < 20:

		# Retrieving team name.
		team_list.append(json_res[count]["team"])

		# Retrieving stadium name.
		stadium_list.append(json_res[count]["stadium"])

		# Retrieving stadium's latitude.
		lat_list.append(json_res[count]["latitude"])

		# Retrieving stadium's longitude.
		lon_list.append(json_res[count]["longitude"])

		count += 1

	return team_list, stadium_list, lat_list, lon_list

def dataframe():
	team_list, stadium_list, lat_list, lon_list = locations()

	# Setting the headers then zipping the lists to create a dataframe.
	headers = ['team', 'stadium', 'latitude', 'longitude']
	zipped = list(zip(team_list, stadium_list, lat_list, lon_list))

	df = pd.DataFrame(zipped, columns = headers)

	return df

class Locations:

	def drop(self):
		client = bigquery.Client()
		query = f"""
            DROP TABLE 
            {locations_table}
        """

		query_job = client.query(query)

		print("Location table dropped...")

	def load(self):
		df = dataframe() # Getting dataframe creating in dataframe() function.
		
		client = bigquery.Client(project="cloud-data-infrastructure")

		table_id = locations_table

		job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
		job.result()  # Wait for the job to complete.

		table = client.get_table(table_id)  # Make an API request.
		
		print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns")