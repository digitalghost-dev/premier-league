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

@task
def task_fixtues():
    from etl.firestore.fixtures import load_firestore

@flow
def statistics():
    a = task_standings()
    b = task_teams(wait_for=[a])
    c = task_top_scorers(wait_for=[a, b])
    d = task_fixtues(wait_for=[a, b, c])

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

# --- Squads ---
@task
def task_squads():
    from etl.bigquery.squads import call_api

@flow
def squads():
    a = task_squads()

# --- Injuries ---
@task
def task_injuries():
    from etl.bigquery.injuries import call_api

@flow
def injuries():
    a = task_injuries()

# --- Current Round ---
@task
def task_current_round():
    from etl.bigquery.current_round import load_current_round

@flow
def current_round():
    a = task_current_round()
