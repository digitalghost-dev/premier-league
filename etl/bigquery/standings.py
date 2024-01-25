import json
import os

import pandas as pd
import requests  # type: ignore
from google.cloud import secretmanager
from pandas import DataFrame

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


def gcp_secret_rapid_api() -> str:
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
	]
):
	payload = gcp_secret_rapid_api()

	headers = {
		"X-RapidAPI-Key": payload,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	url = "https://api-football-v1.p.rapidapi.com/v3/standings"

	query = {"season": "2023", "league": "39"}
	response = requests.get(url, headers=headers, params=query, timeout=10)
	json_res = response.json()

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

	count = 0
	while count < 20:
		team_id_list.append(int(json_res["response"][0]["league"]["standings"][0][count]["team"]["id"]))

		rank_list.append(int(json_res["response"][0]["league"]["standings"][0][count]["rank"]))

		team_list.append(
			str(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["team"]["name"])).strip('"')
		)

		games_played.append(int(json_res["response"][0]["league"]["standings"][0][count]["all"]["played"]))

		wins_list.append(int(json_res["response"][0]["league"]["standings"][0][count]["all"]["win"]))

		draws_list.append(int(json_res["response"][0]["league"]["standings"][0][count]["all"]["draw"]))

		loses_list.append(int(json_res["response"][0]["league"]["standings"][0][count]["all"]["lose"]))

		form_list.append(str(json.dumps(json_res["response"][0]["league"]["standings"][0][count]["form"])).strip('"'))

		points_list.append(int(json_res["response"][0]["league"]["standings"][0][count]["points"]))

		goals_for.append(int(json_res["response"][0]["league"]["standings"][0][count]["all"]["goals"]["for"]))

		goals_against.append(int(json_res["response"][0]["league"]["standings"][0][count]["all"]["goals"]["against"]))

		goals_diff.append(int(json_res["response"][0]["league"]["standings"][0][count]["goalsDiff"]))

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
	)


def create_dataframe() -> DataFrame:
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
	) = call_api()

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
		)
	)

	df = pd.DataFrame(zipped, columns=headers)

	return df


def define_table_schema() -> list[dict[str, str]]:
	schema_definition = [
		{"name": "team_id", "type": "INTEGER"},
		{"name": "rank", "type": "INTEGER"},
		{"name": "team", "type": "STRING"},
		{"name": "games_played", "type": "INTEGER"},
		{"name": "wins", "type": "INTEGER"},
		{"name": "draws", "type": "INTEGER"},
		{"name": "loses", "type": "INTEGER"},
		{"name": "recent_form", "type": "STRING"},
		{"name": "points", "type": "INTEGER"},
		{"name": "goals_for", "type": "INTEGER"},
		{"name": "goals_against", "type": "INTEGER"},
		{"name": "goal_difference", "type": "INTEGER"},
	]

	return schema_definition


def send_dataframe_to_bigquery(standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]) -> None:
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
