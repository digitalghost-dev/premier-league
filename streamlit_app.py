# Importing needed modules.
from google.oauth2 import service_account
from google.cloud import bigquery
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

    # Calling variables from toml file.
    standings_table = st.secrets["football_db"]["standings"]
    players_table = st.secrets["football_db"]["players"]

    # Running SQL query to retrieve data.
    standings_data = run_query("""
        SELECT * FROM
        {}
        ORDER BY Rank
        """.format(standings_table)
    )

    players_data = run_query("""
        SELECT * FROM
        {}
        ORDER BY Goals DESC
        """.format(players_table)
    )

    standings_df = pd.DataFrame(data = standings_data)
    players_df = pd.DataFrame(data = players_data)

    return standings_df, players_df

def streamlit_app():
    standings_df, players_df = background_processing()

    logo = st.secrets["elements"]["logo_image"]

    # Setting page layout by columns.
    col1, col2 = st.columns((3, 2))
    
    col3, col4, col5, col6, col7 = st.columns((1, 1, 1, 1, 1))

    with st.container():
        # Column one
        col1.title("Premier League Statistics for 2022/23 " + "⚽️")

        col1.subheader("Current Standings:")
        col1.table(standings_df)

        col1.subheader("Top Scorers")

        # Column two
        col2.image(logo)

        col2.subheader("Points per Team:")

        # Creating the slider.
        points = standings_df['Points'].tolist()
        points_selection = col2.slider(
            'Select a Range of Points:',
            min_value = min(points),
            max_value = max(points),
            value = (min(points), max(points))
        )

        # Picking colors to use for the bar chart.
        colors = ['indigo',] * 20

        # Making sure the bar chart changes with the slider.
        mask = standings_df['Points'].between(*points_selection)
        results = standings_df[mask].shape[0]
        col2.markdown(f'*Teams within range of selected points: {results}*')
        df_grouped = standings_df[mask]
        df_grouped = df_grouped.reset_index()

        # Creating the bar chart.
        points_chart = go.Figure(data=[go.Bar(
            x = df_grouped['Team'],
            y = df_grouped['Points'],
            marker_color = colors,
            text = df_grouped['Points'],
            textposition = 'auto'
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

        col2.plotly_chart(points_chart, use_container_width = True)

    with st.container():
        # First top scorer
        col3.markdown("![Image]({})".format(players_df.iloc[0][4]))
        col3.markdown("**{}**".format(players_df.iloc[0][0]))
        col3.markdown("**Goals:** {}".format(players_df.iloc[0][1]))
        col3.markdown("**Team:** {}".format(players_df.iloc[0][2]))
        col3.markdown("**Nationality:** {}".format(players_df.iloc[0][3]))
        
        # Second top scorer
        col4.markdown("![Image]({})".format(players_df.iloc[1][4]))
        col4.markdown("**{}**".format(players_df.iloc[1][0]))
        col4.markdown("**Goals:** {}".format(players_df.iloc[1][1]))
        col4.markdown("**Team:** {}".format(players_df.iloc[1][2]))
        col4.markdown("**Nationality:** {}".format(players_df.iloc[1][3]))

        # Third top scorer
        col5.markdown("![Image]({})".format(players_df.iloc[2][4]))
        col5.markdown("**{}**".format(players_df.iloc[2][0]))
        col5.markdown("**Goals:** {}".format(players_df.iloc[2][1]))
        col5.markdown("**Team:** {}".format(players_df.iloc[2][2]))
        col5.markdown("**Nationality:** {}".format(players_df.iloc[2][3]))

        # Fourth top scorer
        col6.markdown("![Image]({})".format(players_df.iloc[3][4]))
        col6.markdown("**{}**".format(players_df.iloc[3][0]))
        col6.markdown("**Goals:** {}".format(players_df.iloc[3][1]))
        col6.markdown("**Team:** {}".format(players_df.iloc[3][2]))
        col6.markdown("**Nationality:** {}".format(players_df.iloc[3][3]))

        # Fifth top scorer
        col7.markdown("![Image]({})".format(players_df.iloc[4][4]))
        col7.markdown("**{}**".format(players_df.iloc[4][0]))
        col7.markdown("**Goals:** {}".format(players_df.iloc[4][1]))
        col7.markdown("**Team:** {}".format(players_df.iloc[4][2]))
        col7.markdown("**Nationality:** {}".format(players_df.iloc[4][3]))

streamlit_app()