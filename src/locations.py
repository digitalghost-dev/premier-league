# Importing needed libraries.
from config import locations_table, locations_api, project_id
from google.cloud import bigquery
import pandas as pd
import requests
import json

def call_api():
	# Building query to retrieve data.
	response = requests.request("GET", locations_api)
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
	headers = ['Team', 'Stadium', 'Latitude', 'Longitude']
	zipped = list(zip(team_list, stadium_list, lat_list, lon_list))

	df = pd.DataFrame(zipped, columns = headers)

	return df

class Locations:

	def drop(self):
		client = bigquery.Client()
		query = """
            DROP TABLE 
            {}
        """.format(locations_table)

		query_job = client.query(query)

		print("Location table dropped...")

	def load(self):
		df = dataframe() # Getting dataframe creating in dataframe() function.
		
		client = bigquery.Client(project=project_id)

		table_id = locations_table

		job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
		job.result()  # Wait for the job to complete.

		table = client.get_table(table_id)  # Make an API request.
		print(
            "Loaded {} rows and {} columns".format(
                table.num_rows, len(table.schema)
            )
        )