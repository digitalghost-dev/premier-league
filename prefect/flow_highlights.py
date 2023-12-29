from prefect import task, flow

@task
def task_highlights():
    from etl.bigquery.highlights import send_dataframe_to_bigquery

@flow
def highlights():
    a = task_highlights()