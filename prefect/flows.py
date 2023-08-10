from prefect import task, flow

@task
def standings():
    from etl.postgres.standings import send_dataframe_to_postgresql

@task
def teams():
    from etl.postgres.teams import send_dataframe_to_postgresql

@task
def top_scorers():
    from etl.postgres.top_scorers import send_dataframe_to_postgresql

@flow
def premier_league_flow():
    a = standings()
    b = teams(wait_for=[a])
    c = top_scorers(wait_for=[a, b])