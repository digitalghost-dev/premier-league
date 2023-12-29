import os

import polars as pl
import requests  # type: ignore
from google.cloud import secretmanager

# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"


def gcp_secret_stock_api() -> str:
	"""This function retrieves the Rapid API key from GCP Secret Manager"""

	client = secretmanager.SecretManagerServiceClient()
	name = "projects/463690670206/secrets/stock-api/versions/1"
	response = client.access_secret_version(request={"name": name})
	stock_api_key = response.payload.data.decode("UTF-8")

	return stock_api_key


def gcp_secret_postgresql_uri() -> str:
	"""This function retrieves the Rapid API key from GCP Secret Manager"""

	client = secretmanager.SecretManagerServiceClient()
	name = "projects/463690670206/secrets/postgresql-uri/versions/1"
	response = client.access_secret_version(request={"name": name})
	postgresql_uri = response.payload.data.decode("UTF-8")

	return postgresql_uri


def send_dataframe_to_postgres() -> None:
	stock_api_key = gcp_secret_stock_api()
	postgresql_uri = gcp_secret_postgresql_uri()

	url = f"https://financialmodelingprep.com/api/v3/quote/MANU?apikey={stock_api_key}"

	response = requests.request("GET", url)

	json_res = response.json()
	df = pl.DataFrame(json_res)

	df.write_database(
		table_name="stocks", connection=postgresql_uri, if_table_exists="append"
	)


if __name__ != "__main__":
	send_dataframe_to_postgres()
