from prefect import task, flow

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
    a = task_news()

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
