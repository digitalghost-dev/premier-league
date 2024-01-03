"""
This file pulls data from the YouTube API relating to the English Premier League
highlights and loads it into a BigQuery table.
"""

import googleapiclient.discovery
from google.cloud import secretmanager
from datetime import datetime, timedelta, timezone

import pandas as pd
from pandas import DataFrame


def gcp_secret_rapid_api() -> str:
	"""This function retrieves the Rapid API key from GCP Secret Manager"""

	client = secretmanager.SecretManagerServiceClient()
	name = "projects/463690670206/secrets/youtube-api/versions/1"
	response = client.access_secret_version(request={"name": name})
	youtube_api_key = response.payload.data.decode("UTF-8")

	return youtube_api_key


def call_api(part, channel_id, max_results, query, publishedAfter) -> list:
	"""This function calls the API then returns a list with the YouTube data"""

	youtube_api_key = gcp_secret_rapid_api()

	# Initialize YouTube Data API v3 service
	youtube = googleapiclient.discovery.build(
		"youtube", "v3", developerKey=youtube_api_key
	)

	search_response = (
		youtube.search()
		.list(
			part=part,
			channelId=channel_id,
			maxResults=max_results,
			q=query,
			publishedAfter=publishedAfter,
		)
		.execute()
	)

	videos = search_response.get("items", [])

	return videos


def create_dataframe():
	"""This function creates a dataframe from the API call"""

	current_date = datetime.now(timezone.utc)
	ten_days_ago = current_date - timedelta(days=10)
	published_date = ten_days_ago.strftime("%Y-%m-%dT00:00:00Z")
	videos = call_api(
		"snippet",
		"UCqZQlzSHbVJrwrn5XvzrzcA",
		10,
		"PREMIER LEAGUE HIGHLIGHTS",
		published_date,
	)

	video_list = []
	for video in videos:
		video_sublist = []

		video_sublist.append(str(video["id"]["videoId"]))
		video_sublist.append(
			str("https://www.youtube.com/watch?v=") + str(video["id"]["videoId"])
		)
		video_sublist.append(str(video["snippet"]["title"]))
		video_sublist.append(str(video["snippet"]["thumbnails"]["high"]["url"]))
		video_sublist.append(str(video["snippet"]["description"]))

		# Setting the publish time to a datetime object.
		publish_time_str = video["snippet"]["publishTime"]
		publish_time_datetime = pd.to_datetime(publish_time_str)
		video_sublist.append(publish_time_datetime)

		video_list.append(video_sublist)

	headers = [
		"video_id",
		"video_url",
		"title",
		"thumbnail",
		"description",
		"publish_time",
	]
	df = pd.DataFrame(video_list, columns=headers)

	return df


def define_table_schema() -> list[dict[str, str]]:
	"""This function defines the schema for the table in BigQuery"""

	schema_definition = [
		{"name": "video_id", "type": "STRING"},
		{"name": "video_url", "type": "STRING"},
		{"name": "title", "type": "STRING"},
		{"name": "thumbnail", "type": "STRING"},
		{"name": "description", "type": "STRING"},
		{"name": "publish_time", "type": "DATETIME"},
	]

	return schema_definition


def send_dataframe_to_bigquery(
	standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]
) -> None:
	"""This function sends the dataframe to BigQuery"""

	highlights_dataframe.to_gbq(
		destination_table="premier_league_dataset.highlights",
		if_exists="replace",
		table_schema=schema_definition,
	)

	print("Highlights table loaded!")


if __name__ != "__main__":
	highlights_dataframe = create_dataframe()
	schema_definition = define_table_schema()
	send_dataframe_to_bigquery(highlights_dataframe, schema_definition)
