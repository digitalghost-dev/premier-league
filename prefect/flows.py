from prefect import task, flow
from prefect.context import get_run_context  # type: ignore
from prefect_soda_core.soda_configuration import SodaConfiguration  # type: ignore
from prefect_soda_core.sodacl_check import SodaCLCheck  # type: ignore
from prefect_soda_core.tasks import soda_scan_execute  # type: ignore

# --- Statistics ---
@task
def task_standings():
    from etl.bigquery.standings import send_dataframe_to_bigquery

@task
def task_teams():
    from etl.bigquery.teams import send_dataframe_to_bigquery

@task
def task_top_scorers():
    from etl.bigquery.top_scorers import send_dataframe_to_bigquery

@flow
def statistics():
    a = task_standings()
    b = task_teams(wait_for=[a])
    c = task_top_scorers(wait_for=[a, b])

# --- News ---
@task
def task_news():
    from etl.bigquery.news import send_dataframe_to_bigquery

@flow
def news():
    a = news()

# --- Highlights ---
@task
def task_highlights():
    from etl.bigquery.highlights import send_dataframe_to_bigquery

@flow
def highlights():
    a = task_highlights()

# --- Stocks ---
@task
def task_stocks():
    from etl.postgres.stock import send_dataframe_to_postgres

@flow
def stocks():
    a = task_stocks()

# --- Data Quality ---
@flow
def run_soda_scan():
	soda_configuration_block = SodaConfiguration(
		configuration_yaml_path="./soda/configuration.yaml"
	)
	soda_check_block = SodaCLCheck(sodacl_yaml_path="./soda/checks.yaml")

	# Using the flow_run_name as the name of the file to store the scan results
	flow_run_name = get_run_context().flow_run.name
	scan_results_file_path = f"{flow_run_name}.json"

	return soda_scan_execute(
		data_source_name="bigquery_connection",
		configuration=soda_configuration_block,
		checks=soda_check_block,
		variables={"var": "value"},
		scan_results_file=scan_results_file_path,
		verbose=True,
		return_scan_result_file_content=False,
	)


run_soda_scan()