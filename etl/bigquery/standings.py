"""
This file pulls data from the Football API relating to the English Premier League
standings data and loads it into a BigQuery table.
"""

# Importing needed libraries.
import json
import os

import pandas as pd
import requests  # type: ignore
from google.cloud import secretmanager
from pandas import DataFrame

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


def gcp_secret_rapid_api() -> str:
	"""This function retrieves the Rapid API key from GCP Secret Manager"""

	client = secretmanager.SecretManagerServiceClient()
	name = "projects/463690670206/secrets/rapid-api/versions/1"
	response = client.access_secret_version(request={"name": name})
	rapid_api_key = response.payload.data.decode("UTF-8")

	return rapid_api_key


def call_api() -> (
	tuple[
		list[int],
		list[int],
		list[str],
		list[int],
		list[int],
		list[int],
		list[int],
		list[str],
		list[int],
		list[int],
		list[int],
		list[int],
		list[str],
		list[str],
	]
):
	"""This function calls the API then fills in the empty lists"""

	payload = gcp_secret_rapid_api()

	# Headers used for RapidAPI.
	headers = {
		"X-RapidAPI-Key": payload,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	# Standings endpoint from RapidAPI.
	url = "https://api-football-v1.p.rapidapi.com/v3/standings"

	# Building GET request to retrieve data.
	query = {"season": "2023", "league": "39"}
	response = requests.get(url, headers=headers, params=query, timeout=10)
	json_res = response.json()

	# Empty lists that will be filled and then used to create a dataframe.
	team_id_list = []
	rank_list = []
	team_list = []
	games_played = []
	wins_list = []
	draws_list = []
	loses_list = []
	form_list = []
	points_list = []
	goals_for = []
	goals_against = []
	goals_diff = []
	status_list = []
	logo_list = []

	# Filling in empty lists.
	count = 0
	while count < 20:
		# Team ID.
		team_id_list.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["team"]["id"])
		)

		# Team rank.
		rank_list.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["rank"])
		)

		# Team names.
		team_list.append(
			str(
				json.dumps(
					json_res["response"][0]["league"]["standings"][0][count]["team"][
						"name"
					]
				)
			).strip('"')
		)

		# Amount of games played.
		games_played.append(
			int(
				json_res["response"][0]["league"]["standings"][0][count]["all"][
					"played"
				]
			)
		)

		# Number of wins.
		wins_list.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["all"]["win"])
		)

		# Number of draws.
		draws_list.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["all"]["draw"])
		)

		# Number of loses.
		loses_list.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["all"]["lose"])
		)

		# Team forms.
		form_list.append(
			str(
				json.dumps(
					json_res["response"][0]["league"]["standings"][0][count]["form"]
				)
			).strip('"')
		)

		# Number of points.
		points_list.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["points"])
		)

		# Number of goals for.
		goals_for.append(
			int(
				json_res["response"][0]["league"]["standings"][0][count]["all"][
					"goals"
				]["for"]
			)
		)

		# Number of goals against.
		goals_against.append(
			int(
				json_res["response"][0]["league"]["standings"][0][count]["all"][
					"goals"
				]["against"]
			)
		)

		# Number of goal differential.
		goals_diff.append(
			int(json_res["response"][0]["league"]["standings"][0][count]["goalsDiff"])
		)

		# Each team's position status.
		status_list.append(
			str(json_res["response"][0]["league"]["standings"][0][count]["status"])
		)

		# Team's logo.
		logo_list.append(
			str(
				json_res["response"][0]["league"]["standings"][0][count]["team"]["logo"]
			)
		)

		count += 1

	return (
		team_id_list,
		rank_list,
		team_list,
		games_played,
		wins_list,
		draws_list,
		loses_list,
		form_list,
		points_list,
		goals_for,
		goals_against,
		goals_diff,
		status_list,
		logo_list,
	)


def create_dataframe() -> DataFrame:
	"""This function creates a datafreame from lists created in the last function: call_api()"""

	(
		team_id_list,
		rank_list,
		team_list,
		games_played,
		wins_list,
		draws_list,
		loses_list,
		form_list,
		points_list,
		goals_for,
		goals_against,
		goals_diff,
		status_list,
		logo_list,
	) = call_api()

	# Setting the headers then zipping the lists to create a dataframe.
	headers = [
		"team_id",
		"rank",
		"team",
		"games_played",
		"wins",
		"draws",
		"loses",
		"recent_form",
		"points",
		"goals_for",
		"goals_against",
		"goal_difference",
		"position_status",
		"logo",
	]
	zipped = list(
		zip(
			team_id_list,
			rank_list,
			team_list,
			games_played,
			wins_list,
			draws_list,
			loses_list,
			form_list,
			points_list,
			goals_for,
			goals_against,
			goals_diff,
			status_list,
			logo_list,
		)
	)

	df = pd.DataFrame(zipped, columns=headers)

	return df


def define_table_schema() -> list[dict[str, str]]:
	"""This function defines the schema for the table in BigQuery"""

	schema_definition = [
		{"name": "team_id", "type": "INTEGER"},
		{"name": "rank", "type": "INTEGER"},
		{"name": "team", "type": "STRING"},
		{"name": "games_played", "type": "INTEGER"},
		{"name": "wins", "type": "INTEGER"},
		{"name": "draws", "type": "INTEGER"},
		{"name": "loses", "type": "INTEGER"},
		{"name": "recent_form", "type": "STRING"},
		{"name": "points", "type": "STRING"},
		{"name": "goals_for", "type": "INTEGER"},
		{"name": "goals_against", "type": "INTEGER"},
		{"name": "goal_difference", "type": "INTEGER"},
		{"name": "position_status", "type": "STRING"},
		{"name": "logo", "type": "STRING"},
	]

	return schema_definition


def send_dataframe_to_bigquery(
	standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]
) -> None:
	"""This function sends the dataframe to BigQuery"""

	standings_dataframe.to_gbq(
		destination_table="premier_league_dataset.standings",
		if_exists="replace",
		table_schema=schema_definition,
	)

	print("Standings table loaded!")


if __name__ != "__main__":
	standings_dataframe = create_dataframe()
	schema_definition = define_table_schema()
	send_dataframe_to_bigquery(standings_dataframe, schema_definition)
