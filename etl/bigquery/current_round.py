"""
This file pulls data from an API relating to the English Premier League
current round data and loads it into a BigQuery table.
"""

import os

import pandas as pd
import requests  # type: ignore

# Importing needed libraries.
from google.cloud import secretmanager, run_v2, bigquery
from pandas import DataFrame

# Settings the project environment.
PROJECT_ID = "cloud-data-infrastructure"
os.environ["GCLOUD_PROJECT"] = PROJECT_ID


class DataRetrieval:
	def __init__(self, project_id):
		self.project_id = project_id

	def _get_rapid_api_key(self) -> str:
		"""Retrieve the Rapid API key from GCP Secret Manager"""
		client = secretmanager.SecretManagerServiceClient()
		name = f"projects/{self.project_id}/secrets/rapid-api/versions/1"
		response = client.access_secret_version(request={"name": name})
		return response.payload.data.decode("UTF-8")

	def _call_api(self) -> str:
		"""Call the API and return the current round"""
		payload = self._get_rapid_api_key()
		headers = {
			"X-RapidAPI-Key": payload,
			"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
		}
		url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/rounds"
		querystring = {"league": "39", "season": "2023", "current": "true"}
		response = requests.get(url, headers=headers, params=querystring, timeout=10)
		return response.json()["response"][0]

	def _call_bigquery(self) -> int:
		"""Call BigQuery to pull the latest round number"""
		client = bigquery.Client()
		query = f"""
            SELECT round
            FROM `{self.project_id}.premier_league_dataset.current_round`
            ORDER BY round DESC
            LIMIT 1
        """
		query_job = client.query(query)
		results = query_job.result()
		for row in results:
			bigquery_current_round = row.round
		return bigquery_current_round

	def retrieve_data(self) -> tuple[str, int]:
		"""Retrieve data for the current round"""
		rapid_api_current_round = self._call_api()
		bigquery_current_round = self._call_bigquery()
		return rapid_api_current_round, bigquery_current_round


rapid_api_current_round, bigquery_current_round = DataRetrieval(
	PROJECT_ID
).retrieve_data()

if rapid_api_current_round == bigquery_current_round:
	print("Current round is already loaded!")
	exit()
else:
	print("Current round is not loaded!")

	def create_dataframe() -> DataFrame:
		"""This function creates a dataframe from the API response."""

		# Spliting a string that looks like: "Regular Season - 12"
		regular_season = [rapid_api_current_round[:14]]
		round_number = [rapid_api_current_round[17:]]
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

	def sample_run_job():
		client = run_v2.JobsClient()

		request = run_v2.RunJobRequest(
			name="projects/463690670206/locations/us-central1/jobs/pl-fixtures",
		)

		operation = client.run_job(request=request)

		print("Waiting for operation to complete...")

		response = operation.result()

		print(response)

	current_round_dataframe = create_dataframe()
	schema_definition = define_table_schema()
	send_dataframe_to_bigquery(current_round_dataframe, schema_definition)
	sample_run_job()
