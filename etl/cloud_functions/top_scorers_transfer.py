from google.cloud import bigquery
import pandas as pd
import time

client = bigquery.Client()
bucket_name = "premier_league_bucket"
project = "cloud-data-infrastructure"
dataset_id = "premier_league_dataset"
table_id = "top_scorers"


def transfer(request) -> str:
	destination_uri = f"gs://{bucket_name}/top_scorers.csv"
	dataset_ref = bigquery.DatasetReference(project, dataset_id)
	table_ref = dataset_ref.table(table_id)

	extract_job = client.extract_table(
		table_ref,
		destination_uri,
		location="US",
	)
	extract_job.result()

	print(f"Exported {project}.{dataset_id}.{table_id} to {destination_uri}")

	time.sleep(5)

	df = pd.read_csv("https://storage.googleapis.com/premier_league_bucket/top_scorers.csv")
	sorted_df = df.sort_values(by=["goals"], ascending=False)
	removed_columns = sorted_df.drop(columns=["photo"])
	removed_columns.to_csv(destination_uri, index=False)

	return "OK"
