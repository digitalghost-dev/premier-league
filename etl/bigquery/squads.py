import os

import pandas as pd
import requests  # type: ignore
from google.cloud import bigquery, secretmanager
from pandas import DataFrame

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

STANDINGS_TABLE = "premier_league_dataset.standings"


def gcp_secret_rapid_api() -> str:
	client = secretmanager.SecretManagerServiceClient()
	name = "projects/463690670206/secrets/rapid-api/versions/1"
	response = client.access_secret_version(request={"name": name})
	rapid_api_key = response.payload.data.decode("UTF-8")

	return rapid_api_key


# Calling the Standings table from BigQuery to get each team's id.
def bigquery_call() -> DataFrame:
	bqclient = bigquery.Client()

	query_string = f"""
        SELECT team_id
        FROM {STANDINGS_TABLE}
        ORDER BY Rank
    """

	bigquery_dataframe = (
		bqclient.query(query_string)
		.result()
		.to_dataframe(
			create_bqstorage_client=True,
		)
	)

	return bigquery_dataframe


def call_api() -> None:
	rapid_api_key = gcp_secret_rapid_api()
	bigquery_dataframe = bigquery_call()

	# Iterate through bigquery_dataframe to get the team's id and create a list using list comprehension.
	id_list = [bigquery_dataframe.iloc[i, 0] for i in range(20)]

	headers = {
		"X-RapidAPI-Key": rapid_api_key,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	url = "https://api-football-v1.p.rapidapi.com/v3/players/squads"

	outer_count = 0
	while outer_count < 20:
		team_id_list = []
		team_name_list = []
		player_id_list = []
		player_photo_list = []
		player_name_list = []
		player_age_list = []
		player_number_list = []
		player_position_list = []

		query = {"team": id_list[outer_count]}

		response = requests.get(url, headers=headers, params=query, timeout=10)
		json_res = response.json()

		players_length = len(response.json()["response"][0]["players"])

		inner_count = 0
		while inner_count < players_length:
			team_id_list.append(int(json_res["response"][0]["team"]["id"]))
			team_name_list.append(str(json_res["response"][0]["team"]["name"]))
			player_id_list.append(int(json_res["response"][0]["players"][inner_count]["id"]))
			player_photo_list.append(str(json_res["response"][0]["players"][inner_count]["photo"]))
			player_name_list.append(str(json_res["response"][0]["players"][inner_count]["name"]))

			# The API is missing some player's age and number. Adding try/except blocks.
			try:
				player_age = json_res["response"][0]["players"][inner_count]["age"]
				if player_age is not None:
					player_age_list.append(int(player_age))
				else:
					player_age_list.append(None)  # type: ignore
			except (ValueError, TypeError):
				player_age_list.append(None)  # type: ignore

			try:
				player_number = json_res["response"][0]["players"][inner_count]["number"]
				if player_number is not None:
					player_number_list.append(int(player_number))
				else:
					player_number_list.append(None)  # type: ignore
			except (ValueError, TypeError):
				player_number_list.append(None)  # type: ignore

			player_position_list.append(str(json_res["response"][0]["players"][inner_count]["position"]))

			inner_count += 1

		table_headers = [
			"team_id",
			"team_name",
			"player_id",
			"player_photo",
			"player_name",
			"player_age",
			"player_number",
			"player_position",
		]
		zipped = list(
			zip(
				team_id_list,
				team_name_list,
				player_id_list,
				player_photo_list,
				player_name_list,
				player_age_list,
				player_number_list,
				player_position_list,
			)
		)

		df = pd.DataFrame(zipped, columns=table_headers)

		schema_definition = [
			{"name": "team_id", "type": "INTEGER"},
			{"name": "team_name", "type": "STRING"},
			{"name": "player_id", "type": "INTEGER"},
			{"name": "player_photo", "type": "STRING"},
			{"name": "player_name", "type": "STRING"},
			{"name": "player_age", "type": "INTEGER"},
			{"name": "player_number", "type": "INTEGER"},
			{"name": "player_position", "type": "STRING"},
		]

		formmated_team_name = team_name_list[0].replace(" ", "_").lower()

		df.to_gbq(
			destination_table=f"premier_league_squads.{formmated_team_name}",
			if_exists="replace",
			table_schema=schema_definition,
		)

		print(f"{team_name_list[0]}'s squad table loaded!")

		outer_count += 1


if __name__ != "__main__":
	call_api()
