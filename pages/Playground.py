# System libraries
import os
from datetime import datetime

# Data libraries
import pandas as pd
import psycopg2

# Visualization Libraries
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# Google Cloud Libraries
import firebase_admin
from google.cloud import bigquery
from firebase_admin import firestore
from google.oauth2 import service_account

from streamlit_app import background_processing

def playground_page():
    locations_df, players_df, standings_df, teams_df, db, min_round_postgres, max_round_postgres = background_processing()

    logo = st.secrets["elements"]["logo_image"]

    # Premier League logo.
    col1, col = st.columns((2, 4))
    with st.container():
        col1.image(logo)

    st.write("This page includes interactive features to view data in a personalized way.")

    st.subheader("Points per Team:")

    # Creating the slider.
    points = standings_df["Points"].tolist()
    points_selection = st.slider(
        "Select a Range of Points:",
        min_value = min(points),
        max_value = max(points),
        value = (min(points), max(points))
    )

    # Picking colors to use for the bar chart.
    colors = ["indigo",] * 20

    # Making sure the bar chart changes with the slider.
    mask = standings_df["Points"].between(*points_selection)
    amount_of_teams = standings_df[mask].shape[0]
    
    df_grouped = standings_df[mask]
    df_grouped = df_grouped.reset_index()

    lowest_number = df_grouped["Points"].min()
    st.markdown(f"Number of teams with {lowest_number} or more points: {amount_of_teams}")

    # Creating the bar chart.
    points_chart = go.Figure(data=[go.Bar(
        x = df_grouped["Team"],
        y = df_grouped["Points"],
        marker_color = colors,
        text = df_grouped["Points"],
        textposition = "auto"
    )])

    # Rotating x axis lables.
    points_chart.update_layout(
        xaxis_tickangle = -35,
        autosize = False,
        margin = dict (
            l = 0, # left
            r = 0, # right
            b = 0, # bottom
            t = 0  # top
        )
    )

    st.plotly_chart(points_chart, use_container_width = True)

    st.subheader("Sortable Standings")

    st.write("Below is a sortable table. Sort any column in acsending or descensing order by clicking on the column name.")
    st.checkbox("Expand Table for Full Width", value=True, key="use_container_width")

    st.dataframe(
        standings_df, 
        hide_index=True, 
        use_container_width=st.session_state.use_container_width)

    # Map of stadiums.
    st.subheader("Location of Stadiums")

    mapbox_access_token = st.secrets["mapbox"]["mapbox_key"]

    px.set_mapbox_access_token(mapbox_access_token)

    stadium_map = px.scatter_mapbox(locations_df, lat="latitude", lon="longitude", hover_name="stadium", hover_data="team")

    stadium_map.update_layout(
        mapbox_style="light", 
        margin={"r":0,"t":0,"l":0,"b":0}, 
        mapbox_bounds={"west": -17, "east": 17, "south": 45, "north": 60})

    stadium_map.update_traces(marker=dict(size=8), marker_color="indigo") 

    stadium_map.update_mapboxes(zoom=4)

    st.plotly_chart(stadium_map, height=1000, use_container_width=True)

playground_page()