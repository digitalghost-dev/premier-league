import os
from datetime import datetime
from datetime import timedelta as td

import requests  # type: ignore
from google.cloud import secretmanager
from pandas import DataFrame

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


def gcp_secret_news_api() -> str:
	client = secretmanager.SecretManagerServiceClient()
	name = "projects/463690670206/secrets/news-api/versions/1"
	response = client.access_secret_version(request={"name": name})
	news_api_key = response.payload.data.decode("UTF-8")

	return news_api_key


def call_api() -> tuple[list[str], list[str], list[str], list[str]]:
	news_api_key = gcp_secret_news_api()

	# Getting yesterday's date.
	yesteryday = datetime.now() - td(days=1)
	yesteryday_str = yesteryday.strftime("%Y-%m-%d")

	url = (
		"https://newsapi.org/v2/everything?"
		"q=Premier League&"
		f"from={yesteryday_str}&"
		"language=en&"
		"domains=skysports.com,theguardian.com,90min.com&"
		"sortBy=popularity&"
		f"apiKey={news_api_key}"
	)

	response = requests.request("GET", url, timeout=20)
	json_res = response.json()

	title_list = []
	url_list = []
	url_to_image_list = []
	published_at_list = []

	for article in json_res["articles"]:
		title_list.append(str(article["title"]))
		url_list.append(str(article["url"]))
		url_to_image_list.append(str(article["urlToImage"]))

		published_at = datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
		published_at_list.append(published_at.strftime("%H:%M:%S"))

	return title_list, url_list, url_to_image_list, published_at_list


def create_dataframe() -> DataFrame:
	title_list, url_list, url_to_image_list, published_at_list = call_api()

	df = DataFrame(
		{
			"title": title_list,
			"url": url_list,
			"url_to_image": url_to_image_list,
			"published_at": published_at_list,
		}
	).sort_values(by="published_at", ascending=False)

	return df


def define_table_schema() -> list[dict[str, str]]:
	schema_definition = [
		{"name": "title", "type": "STRING"},
		{"name": "url", "type": "STRING"},
		{"name": "url_to_image", "type": "STRING"},
		{"name": "published_at", "type": "STRING"},
	]

	return schema_definition


def send_dataframe_to_bigquery(
	standings_dataframe: DataFrame, schema_definition: list[dict[str, str]]
) -> None:
	standings_dataframe.to_gbq(
		destination_table="premier_league_dataset.news",
		if_exists="replace",
		table_schema=schema_definition,
	)

	print("News table loaded!")


if __name__ != "__main__":
	news_dataframe = create_dataframe()
	schema_definition = define_table_schema()
	send_dataframe_to_bigquery(news_dataframe, schema_definition)
