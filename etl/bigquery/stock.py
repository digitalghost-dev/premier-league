import os

import polars as pl
import requests

from google.cloud import secretmanager
from google.cloud import bigquery
from io import BytesIO
import io


# Settings the project environment.
os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

def gcp_secret_stock_api() -> str:
    """This function retrieves the Rapid API key from GCP Secret Manager"""

    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/stock-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    stock_api_key = response.payload.data.decode("UTF-8")

    return stock_api_key

stock_api_key = gcp_secret_stock_api()

url = f"https://financialmodelingprep.com/api/v3/quote/MANU?apikey={stock_api_key}"

response = requests.request("GET", url)

json_res = response.json()
df = pl.DataFrame(json_res)

print(df)

client = bigquery.Client()

with io.BytesIO() as stream:
    df.write_parquet(stream)
    stream.seek(0)
    job = client.load_table_from_file(
        stream, 
        destination = "premier_league_dataset.stock",
        project="cloud-data-infrastructure",
        job_config=bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
        ),
    )

job.result()