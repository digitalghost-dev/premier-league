# Importing needed modules.
from google.oauth2 import service_account
from google.cloud import bigquery
from config import standings_name
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

def background_processing():
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)

    # Perform query.
    # Uses st.experimental_memo to only rerun when the query changes or after 10 min.
    @st.experimental_memo(ttl=600)
    def run_query(query):
        query_job = client.query(query)
        raw_data = query_job.result()
        # Convert to list of dicts. Required for st.experimental_memo to hash the return value.
        data = [dict(data) for data in raw_data]
        return data


    # Running SQL query to retrieve data.
    data = run_query("""
        SELECT * FROM
        {}
        ORDER BY Rank
        """.format(standings_name)
    )

    df = pd.DataFrame(data=data)

    df_index = pd.DataFrame(data=data)

    return df

def streamlit_app():
    df = background_processing()

    st.title("Premier League Statistics for 2022/23 " + "⚽️")

    # Setting page layout by columns.
    col1, col2 = st.columns((3, 3))

    with col1:
        st.subheader("Current Standings:")
        st.table(df)

    with col2 :
        st.subheader("Points per Team:")

        # Creating the slider.
        points = df['Points'].tolist()
        points_selection = st.slider(
            'Select a Range of Points:',
            min_value = min(points),
            max_value = max(points),
            value = (min(points), max(points))
        )

        # Picking colors to use for the bar chart.
        colors = ['lightslategray',] * 20
        colors[0] = 'darkgreen'
        colors[1] = 'darkgreen'
        colors[2] = 'darkgreen'
        colors[3] = 'darkgreen'
        colors[4] = 'lightgreen'
        colors[-1] = 'crimson'
        colors[-2] = 'crimson'
        colors[-3] = 'crimson'

        # Making sure the bar chart changes with the slider.
        mask = df['Points'].between(*points_selection)
        results = df[mask].shape[0]
        st.markdown(f'*Teams within range of selected points: {results}*')
        df_grouped = df[mask]
        df_grouped = df_grouped.reset_index()

        # Creating the bar chart.
        points_chart = go.Figure(data=[go.Bar(
            x = df_grouped['Team'],
            y = df_grouped['Points'],
            marker_color = colors
        )])

        # Rotating x axis lables.
        points_chart.update_layout(
            xaxis_tickangle = -35,
            autosize = False,
            margin = dict (
                l = 0,
                r = 0,
                b = 0,
                t = 0
            )
        )

        st.plotly_chart(points_chart, use_container_width = True)

streamlit_app()