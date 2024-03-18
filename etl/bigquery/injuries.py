import os

from datetime import datetime
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
        SELECT *
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


def get_teams_with_injuries() -> list:
	rapid_api_key = gcp_secret_rapid_api()
	bigquery_dataframe = bigquery_call()

	id_list = [bigquery_dataframe.iloc[i, 0] for i in range(20)]

	headers = {
		"X-RapidAPI-Key": rapid_api_key,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	url = "https://api-football-v1.p.rapidapi.com/v3/injuries"
	injuried_teams_list = []

	for id in id_list:
		current_date = datetime.now()
		formatted_date = current_date.strftime("%Y-%m-%d")

		query = {"league": "39", "season": "2023", "team": id, "date": formatted_date}

		response = requests.get(url, headers=headers, params=query, timeout=10)
		json_res = response.json()

		if json_res["response"] == []:
			pass
		else:
			injuried_teams_list.append(id)

	return injuried_teams_list


def call_api():
	rapid_api_key = gcp_secret_rapid_api()
	injuried_teams_list = get_teams_with_injuries()

	headers = {
		"X-RapidAPI-Key": rapid_api_key,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	url = "https://api-football-v1.p.rapidapi.com/v3/injuries"

	for id in injuried_teams_list:
		team_id_list = []
		team_name_list = []
		player_id_list = []
		player_name_list = []
		injury_type_list = []
		injury_reason_list = []
		date_list = []

		current_date = datetime.now()
		formatted_date = current_date.strftime("%Y-%m-%d")

		query = {"league": "39", "season": "2023", "team": id, "date": formatted_date}

		response = requests.get(url, headers=headers, params=query, timeout=10)
		json_res = response.json()

		response_length = len(json_res["response"])

		inner_count = 0
		while inner_count < response_length:
			team_id_list.append(int(json_res["response"][0]["team"]["id"]))
			team_name_list.append(str(json_res["response"][inner_count]["team"]["name"]))
			player_id_list.append(int(json_res["response"][inner_count]["player"]["id"]))
			player_name_list.append(str(json_res["response"][inner_count]["player"]["name"]))
			injury_type_list.append(str(json_res["response"][inner_count]["player"]["type"]))
			injury_reason_list.append(str(json_res["response"][inner_count]["player"]["reason"]))

			date_convert = datetime.strptime(
				json_res["response"][inner_count]["fixture"]["date"], "%Y-%m-%dT%H:%M:%S%z"
			)
			date_list.append(date_convert.strftime("%Y-%m-%d"))

			inner_count += 1

		table_headers = [
			"team_id",
			"team_name",
			"player_id",
			"player_name",
			"injury_type",
			"injury_reason",
			"injury_date",
		]
		zipped = list(
			zip(
				team_id_list,
				team_name_list,
				player_id_list,
				player_name_list,
				injury_type_list,
				injury_reason_list,
				date_list,
			)
		)

		df = pd.DataFrame(zipped, columns=table_headers)

		schema_definition = [
			{"name": "team_id", "type": "INTEGER"},
			{"name": "team_name", "type": "STRING"},
			{"name": "player_id", "type": "INTEGER"},
			{"name": "player_name", "type": "STRING"},
			{"name": "injury_type", "type": "STRING"},
			{"name": "injury_reason", "type": "STRING"},
			{"name": "injury_date", "type": "DATE"},
		]

		formatted_team_name = team_name_list[0].replace(" ", "_").lower()

		df.to_gbq(
			f"premier_league_injuries.{formatted_team_name}",
			project_id="cloud-data-infrastructure",
			if_exists="replace",
			table_schema=schema_definition,
		)

		print(f"{team_name_list[0]}'s injuries table loaded!")


if __name__ != "__main__":
	call_api()
