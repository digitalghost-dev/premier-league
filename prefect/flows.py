from prefect import flow

@flow
def premier_league_flow():
    from etl.postgres.standings import send_dataframe_to_postgresql