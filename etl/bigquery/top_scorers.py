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


def call_api() -> tuple[list[str], list[int], list[str], list[int], list[str], list[str]]:
	rapid_api_key = gcp_secret_rapid_api()
	headers = {
		"X-RapidAPI-Key": rapid_api_key,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"

	query = {"league": "39", "season": "2023"}
	response = requests.get(url, headers=headers, params=query, timeout=10)
	json_res = response.json()

	full_name_list = []
	goals_list = []
	assists_list = []
	team_list = []
	nationality_list = []
	photo_list = []

	count = 0
	while count < 5:
		# Retrieving player's first and last name then combining for full name.
		first_name = (
			str(
				json.dumps(
					json_res["response"][count]["player"]["firstname"],
					ensure_ascii=False,
				)
			)
		).strip('"')
		last_name = (
			str(
				json.dumps(
					json_res["response"][count]["player"]["lastname"],
					ensure_ascii=False,
				)
			)
		).strip('"')

		full_name = first_name + " " + last_name

		full_name_list.append(full_name)

		goals_list.append(int(json_res["response"][count]["statistics"][0]["goals"]["total"]))

		try:
			assists = json_res["response"][count]["statistics"][0]["goals"]["assists"]
			if assists is not None:
				assists_list.append(int(assists))
			else:
				assists_list.append(None)  # type: ignore
		except (ValueError, TypeError):
			assists_list.append(0)

		team_list.append(str(json_res["response"][count]["statistics"][0]["team"]["name"]).strip('"'))

		nationality_list.append(str(json_res["response"][count]["player"]["nationality"]).strip('"'))

		photo_list.append(str(json_res["response"][count]["player"]["photo"]).strip('"'))

		count += 1

	return (
		full_name_list,
		goals_list,
		team_list,
		assists_list,
		nationality_list,
		photo_list,
	)


def create_dataframe() -> DataFrame:
	(
		full_name_list,
		goals_list,
		team_list,
		assists_list,
		nationality_list,
		photo_list,
	) = call_api()

	headers = ["name", "goals", "team", "assists", "nationality", "photo"]
	zipped = list(
		zip(
			full_name_list,
			goals_list,
			team_list,
			assists_list,
			nationality_list,
			photo_list,
		)
	)

	df = pd.DataFrame(zipped, columns=headers)

	return df


def define_table_schema() -> list[dict[str, str]]:
	schema_definition = [
		{"name": "name", "type": "STRING"},
		{"name": "goals", "type": "INTEGER"},
		{"name": "team", "type": "STRING"},
		{"name": "assists", "type": "INTEGER"},
		{"name": "nationality", "type": "STRING"},
		{"name": "photo", "type": "STRING"},
	]

	return schema_definition


def send_dataframe_to_bigquery(standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]) -> None:
	top_scorers_dataframe.to_gbq(
		destination_table="premier_league_dataset.top_scorers",
		if_exists="replace",
		table_schema=schema_definition,
	)

	print("Top Scorers table loaded!")


if __name__ != "__main__":
	top_scorers_dataframe = create_dataframe()
	schema_definition = define_table_schema()
	send_dataframe_to_bigquery(top_scorers_dataframe, schema_definition)
