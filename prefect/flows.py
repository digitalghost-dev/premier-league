from prefect import task, flow

# Defining tasks.
@task
def standings():
    from etl.bigquery.standings import send_dataframe_to_bigquery

@task
def teams():
    from etl.bigquery.teams import send_dataframe_to_bigquery

@task
def top_scorers():
    from etl.bigquery.top_scorers import send_dataframe_to_bigquery

@task
def news():
    from etl.bigquery.news import send_dataframe_to_bigquery

@task
def stocks():
    from etl.postgres.stock import send_dataframe_to_postgres

# Defining flows.
@flow
def premier_league_flow():
    a = standings()
    b = teams(wait_for=[a])
    c = top_scorers(wait_for=[a, b])

@flow
def news_flow():
    a = news()

@flow
def stocks_flow():
    a = stocks()