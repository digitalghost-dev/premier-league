import os

import pandas as pd
import requests  # type: ignore
from google.cloud import bigquery, secretmanager
from pandas import DataFrame

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

STANDINGS_TABLE = "premier_league_dataset.standings"
TEAMS_TABLE = "premier_league_dataset.teams"


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


def call_api() -> (
	tuple[
		list[int],
		list[str],
		list[str],
		list[str],
		list[int],
		list[int],
		list[int],
		list[float],
		list[int],
	]
):
	rapid_api_key = gcp_secret_rapid_api()
	bigquery_dataframe = bigquery_call()

	# Iterate through bigquery_dataframe to get the team's id and create a list using list comprehension.
	id_list = [bigquery_dataframe.iloc[i, 0] for i in range(20)]

	headers = {
		"X-RapidAPI-Key": rapid_api_key,
		"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
	}

	url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"

	team_id_list = []
	team_list = []
	logo_list = []
	form_list = []
	clean_sheets_list = []
	penalty_scored_list = []
	penalty_missed_list = []
	average_goals_list = []
	win_streak_list = []

	count = 0
	while count < 20:
		query = {"league": "39", "season": "2023", "team": id_list[count]}
		response = requests.get(url, headers=headers, params=query, timeout=10)
		json_res = response.json()

		team_id_list.append(int(json_res["response"]["team"]["id"]))

		team_list.append(str(json_res["response"]["team"]["name"]))

		logo_list.append(str(json_res["response"]["team"]["logo"]))

		form_list.append(str(json_res["response"]["form"]))

		clean_sheets_list.append(int(json_res["response"]["clean_sheet"]["total"]))

		penalty_scored_list.append(int(json_res["response"]["penalty"]["scored"]["total"]))

		penalty_missed_list.append(int(json_res["response"]["penalty"]["missed"]["total"]))

		average_goals_list.append(float(json_res["response"]["goals"]["for"]["average"]["total"]))

		win_streak_list.append(int(json_res["response"]["biggest"]["streak"]["wins"]))

		count += 1

	return (
		team_id_list,
		team_list,
		logo_list,
		form_list,
		clean_sheets_list,
		penalty_scored_list,
		penalty_missed_list,
		average_goals_list,
		win_streak_list,
	)


def create_dataframe() -> DataFrame:
	(
		team_id_list,
		team_list,
		logo_list,
		form_list,
		clean_sheets_list,
		penalty_scored_list,
		penalty_missed_list,
		average_goals_list,
		win_streak_list,
	) = call_api()

	headers = [
		"team_id",
		"team",
		"logo",
		"form",
		"clean_sheets",
		"penalties_scored",
		"penalties_missed",
		"average_goals",
		"win_streak",
	]
	zipped = list(
		zip(
			team_id_list,
			team_list,
			logo_list,
			form_list,
			clean_sheets_list,
			penalty_scored_list,
			penalty_missed_list,
			average_goals_list,
			win_streak_list,
		)
	)

	df = pd.DataFrame(zipped, columns=headers)

	return df


def define_table_schema() -> list[dict[str, str]]:
	schema_definition = [
		{"name": "team_id", "type": "INTEGER"},
		{"name": "team", "type": "STRING"},
		{"name": "logo", "type": "STRING"},
		{"name": "form", "type": "STRING"},
		{"name": "clean_sheets", "type": "INTEGER"},
		{"name": "penalties_scored", "type": "INTEGER"},
		{"name": "penalties_missed", "type": "INTEGER"},
		{"name": "average_goals", "type": "FLOAT"},
		{"name": "win_streak", "type": "INTEGER"},
	]

	return schema_definition


def send_dataframe_to_bigquery(standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]) -> None:
	teams_dataframe.to_gbq(
		destination_table="premier_league_dataset.teams",
		if_exists="replace",
		table_schema=schema_definition,
	)

	print("Teams table loaded!")


if __name__ != "__main__":
	teams_dataframe = create_dataframe()
	schema_definition = define_table_schema()
	send_dataframe_to_bigquery(teams_dataframe, schema_definition)
