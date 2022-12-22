# Importing needed modules.
from google.oauth2 import service_account
from google.cloud import bigquery
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
    locations_table = st.secrets["football_db"]["locations"]
    players_table = st.secrets["football_db"]["players"]
    standings_table = st.secrets["football_db"]["standings"]
    teams_table = st.secrets["football_db"]["teams"]

    # Running SQL query to retrieve data from the following tables:

    # Locations table.
    locations_data = run_query(f"""
        SELECT latitude, longitude
        FROM {locations_table}
        """
    )

    # Players table.
    players_data = run_query(f"""
        SELECT *
        FROM {players_table}
        ORDER BY Goals DESC
        """
    )

    # Standings table.
    standings_data = run_query(f"""
        SELECT Rank, Team, Wins, Draws, Loses, Points, GF, GA, GD
        FROM {standings_table}
        ORDER BY Rank
        """
    )

    # Teams table.
    teams_data = run_query(f"""
        SELECT logo, form, clean_sheets, penalties_scored, penalties_missed
        FROM {teams_table} AS t
        LEFT JOIN {standings_table} AS s
        ON t.team = s.Team
        ORDER BY s.Rank
        LIMIT 5
        """
    )

    # Creating dataframes from BigQuery tables.
    locations_df = pd.DataFrame(data = locations_data)
    players_df = pd.DataFrame(data = players_data)
    standings_df = pd.DataFrame(data = standings_data)
    teams_df = pd.DataFrame(data = teams_data)

    return locations_df, players_df, standings_df, teams_df

def streamlit_app():
    locations_df, players_df, standings_df, teams_df = background_processing()

    logo = st.secrets["elements"]["logo_image"]

    # Premier League logo.
    col1, col = st.columns((2, 4))
    with st.container():
        col1.image(logo)

    # Title.
    col1, col = st.columns((9, 1))
    with st.container():
        col1.title("Premier League Statistics / '22-'23")

    # Tab menu.
    tab1, tab2, tab3 = st.tabs(["📄 Overview", "⚽️ Top Teams", "🏃🏻‍♂️ Top Players"])

    # Tab 1, overview
    with tab1:

        col1, col2 = st.columns(2)

        # Standings table.
        with col1:
            st.subheader("Standings")

            st.table(standings_df)

        # Slider and bar graph.
        with col2:
            st.subheader("Points per Team:")

            # Creating the slider.
            points = standings_df['Points'].tolist()
            points_selection = st.slider(
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
            st.markdown(f'*Teams within range of selected points: {results}*')
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

            st.plotly_chart(points_chart, use_container_width = True)

        # Map of stadiums.
        st.subheader("Location of Stadiums")
        st.map(locations_df, use_container_width=True)

    # Tab 2, top teams
    with tab2:
        
        st.subheader("Top 5 Teams")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # First top team.
            st.markdown(f"![Image]({(teams_df.iloc[0][0])})")
            st.markdown(f"**Form (Last 5):** {((teams_df.iloc[0][1])[-5:])}")
            st.markdown(f"**Clean Sheets:** {(teams_df.iloc[0][2])}")
            st.markdown(f"**Penalties Scored:** {(teams_df.iloc[0][3])}")
            st.markdown(f"**Penalties Missed:** {(teams_df.iloc[0][4])}")

        with col2:
            # Second top team.
            st.markdown(f"![Image]({(teams_df.iloc[1][0])})")
            st.markdown(f"**Form (Last 5):** {((teams_df.iloc[1][1])[-5:])}")
            st.markdown(f"**Clean Sheets:** {(teams_df.iloc[1][2])}")
            st.markdown(f"**Penalties Scored:** {(teams_df.iloc[1][3])}")
            st.markdown(f"**Penalties Missed:** {(teams_df.iloc[1][4])}")

        with col3:
            # Third top team.
            st.markdown(f"![Image]({(teams_df.iloc[2][0])})")
            st.markdown(f"**Form (Last 5):** {((teams_df.iloc[2][1])[-5:])}")
            st.markdown(f"**Clean Sheets:** {(teams_df.iloc[2][2])}")
            st.markdown(f"**Penalties Scored:** {(teams_df.iloc[2][3])}")
            st.markdown(f"**Penalties Missed:** {(teams_df.iloc[2][4])}")

        with col4:
            # Fourth top team.
            st.markdown(f"![Image]({(teams_df.iloc[3][0])})")
            st.markdown(f"**Form (Last 5):** {((teams_df.iloc[3][1])[-5:])}")
            st.markdown(f"**Clean Sheets:** {(teams_df.iloc[3][2])}")
            st.markdown(f"**Penalties Scored:** {(teams_df.iloc[3][3])}")
            st.markdown(f"**Penalties Missed:** {(teams_df.iloc[3][4])}")

        with col5:
            # Fifth top team.
            st.markdown(f"![Image]({(teams_df.iloc[4][0])})")
            st.markdown(f"**Form (Last 5):** {((teams_df.iloc[4][1])[-5:])}")
            st.markdown(f"**Clean Sheets:** {(teams_df.iloc[4][2])}")
            st.markdown(f"**Penalties Scored:** {(teams_df.iloc[4][3])}")
            st.markdown(f"**Penalties Missed:** {(teams_df.iloc[4][4])}")

        team_forms = [[], [], [], [], []]

        forms = [teams_df.iloc[0][1], teams_df.iloc[1][1], teams_df.iloc[2][1], teams_df.iloc[3][1], teams_df.iloc[4][1]]

        count = 0
        while count < 5:
            points = 0
            for char in forms[count]:
                if char == "W":
                    points += 3
                elif char == "D":
                    points += 1
                else:
                    points += 0

                team_forms[count].append(points)

            count += 1

        games = [num for num in range(1, 39)]

        headers = [
            str(standings_df.iloc[0][1]),
            str(standings_df.iloc[1][1]),
            str(standings_df.iloc[2][1]),
            str(standings_df.iloc[3][1]),
            str(standings_df.iloc[4][1]),
            "matchday"
        ]
        zipped = list(zip(team_forms[0], team_forms[1], team_forms[2], team_forms[3], team_forms[4], games))

        df = pd.DataFrame(zipped, columns=headers)

        fig = px.line(
            df, 
            x='matchday', 
            y=df.columns[0:5], 
            markers=True, title="Top Five Teams / Matchday: " + str(len(df.index)), 
            labels={
                "matchday": "Matchday",
                "value": "Points",
                "variable": "Team"
            }
        )
        st.plotly_chart(fig)

    # Tab 3, top players
    with tab3:

        st.subheader("Top 5 Scorers")
        
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # First top scorer.
            st.markdown(f"![Image]({(players_df.iloc[0][4])})")
            st.markdown(f"**{(players_df.iloc[0][0])}**")
            st.markdown(f"**Goals:** {(players_df.iloc[0][1])}")
            st.markdown(f"**Team:** {(players_df.iloc[0][2])}")
            st.markdown(f"**Nationality:** {(players_df.iloc[0][3])}")
        
        with col2:
            # Second top scorer.
            st.markdown(f"![Image]({(players_df.iloc[1][4])})")
            st.markdown(f"**{(players_df.iloc[1][0])}**")
            st.markdown(f"**Goals:** {(players_df.iloc[1][1])}")
            st.markdown(f"**Team:** {(players_df.iloc[1][2])}")
            st.markdown(f"**Nationality:** {(players_df.iloc[1][3])}")

        with col3:
            # Third top scorer.
            st.markdown(f"![Image]({(players_df.iloc[2][4])})")
            st.markdown(f"**{(players_df.iloc[2][0])}**")
            st.markdown(f"**Goals:** {(players_df.iloc[2][1])}")
            st.markdown(f"**Team:** {(players_df.iloc[2][2])}")
            st.markdown(f"**Nationality:** {(players_df.iloc[2][3])}")

        with col4:
            # Fourth top scorer.
            st.markdown(f"![Image]({(players_df.iloc[3][4])})")
            st.markdown(f"**{(players_df.iloc[3][0])}**")
            st.markdown(f"**Goals:** {(players_df.iloc[3][1])}")
            st.markdown(f"**Team:** {(players_df.iloc[3][2])}")
            st.markdown(f"**Nationality:** {(players_df.iloc[3][3])}")
            
        with col5:
            # Fifth top scorer.
            col5.markdown(f"![Image]({(players_df.iloc[4][4])})")
            col5.markdown(f"**{(players_df.iloc[4][0])}**")
            col5.markdown(f"**Goals:** {(players_df.iloc[4][1])}")
            col5.markdown(f"**Team:** {(players_df.iloc[4][2])}")
            col5.markdown(f"**Nationality:** {(players_df.iloc[4][3])}")

local_css("style.css")
streamlit_app()