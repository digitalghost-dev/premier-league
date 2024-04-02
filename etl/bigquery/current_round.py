import os

import pandas as pd
import requests  # type: ignore

import google.auth
from google.cloud import secretmanager, bigquery
from pandas import DataFrame

PROJECT_ID = "cloud-data-infrastructure"
os.environ["GCLOUD_PROJECT"] = PROJECT_ID
credentials, project_id = google.auth.default()


class DataRetrieval:
	def __init__(self, project_id):
		self.project_id = project_id

	def _get_rapid_api_key(self) -> str:
		client = secretmanager.SecretManagerServiceClient()
		name = f"projects/{self.project_id}/secrets/rapid-api/versions/1"
		response = client.access_secret_version(request={"name": name})
		return response.payload.data.decode("UTF-8")

	def _call_api(self) -> str:
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
		client = bigquery.Client()
		query = f"""
            SELECT CONCAT(season, " - ", MAX(round)) AS max_round
            FROM `{self.project_id}.premier_league_dataset.current_round`
			GROUP BY season
			LIMIT 1
        """
		query_job = client.query(query)
		results = query_job.result()
		for row in results:
			bigquery_current_round = row.max_round
		return bigquery_current_round

	def retrieve_data(self) -> tuple[str, int]:
		"""Retrieve data for the current round"""
		rapid_api_current_round = self._call_api()
		bigquery_current_round = self._call_bigquery()
		return rapid_api_current_round, bigquery_current_round


rapid_api_current_round, bigquery_current_round = DataRetrieval(PROJECT_ID).retrieve_data()


def load_current_round() -> None:
	if rapid_api_current_round == bigquery_current_round:
		print("Current round is already loaded!")
	else:
		print("Current round is not loaded!")

		def create_dataframe() -> DataFrame:
			# Spliting a string that looks like: "Regular Season - 12"
			regular_season = [rapid_api_current_round[:14]]
			round_number = [rapid_api_current_round[17:]]
			round_number_int = int(round_number[0])

			data = {"season": regular_season, "round": round_number_int}

			# create a pandas dataframe from the dictionary
			df = pd.DataFrame(data, columns=["season", "round"])

			return df, round_number_int

		def define_table_schema() -> list[dict[str, str]]:
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

		current_round_dataframe = create_dataframe()
		schema_definition = define_table_schema()
		send_dataframe_to_bigquery(current_round_dataframe, schema_definition)

if __name__ != "__main__":
	load_current_round()
