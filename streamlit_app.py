import time
from datetime import datetime

import firebase_admin  # type: ignore
import pandas as pd
import streamlit as st
from firebase_admin import firestore  # type: ignore
from google.cloud import bigquery
from google.oauth2 import service_account  # type: ignore
from streamlit.delta_generator import DeltaGenerator

# Importing classes from components/ directory.
from components.social_media import SocialMediaSection
from components.stadiums_map import StadiumMapSection
from components.about import AboutSection

social_media_section = SocialMediaSection()
stadium_map_instance = StadiumMapSection()
about_section = AboutSection()

st.set_page_config(page_title="Streamlit: Premier League", layout="wide")

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
	st.secrets["gcp_service_account"]
)

# Authenticating with Google Cloud.
firestore_database = firestore.Client(credentials=credentials)
client = bigquery.Client(credentials=credentials)


def firestore_connection():
	# Check to see if firebase app has been initialized.
	if not firebase_admin._apps:
		firebase_admin.initialize_app()

	return firestore_database


def bigquery_connection():
	@st.cache_data(ttl=600)
	def run_query(query):
		query_job = client.query(query)
		raw_data = query_job.result()
		# Convert to list of dicts. Required for st.experimental_memo to hash the return value.
		data = [dict(data) for data in raw_data]
		return data

	# ---- Stadium query and dataframe ----
	stadiums_data = run_query(
		"""
            SELECT latitude, longitude, stadium, team
            FROM `premier_league_dataset.stadiums`;
        """
	)

	stadiums_df = pd.DataFrame(data=stadiums_data)

	# ---- Standings query and dataframe ----
	standings_data = run_query(
		"""
            SELECT rank, logo, team, points, wins, draws, loses, goals_for, goals_against, goal_difference
            FROM `premier_league_dataset.standings`
			ORDER BY rank ASC;
        """
	)

	standings_df = pd.DataFrame(data=standings_data)

	# Splitting Standings table to get values to build metric cards.
	status_data = run_query(
		"""
            SELECT rank, team, points, position_status
            FROM `premier_league_dataset.standings`
            ORDER BY rank ASC;
        """
	)

	status_df = pd.DataFrame(data=status_data)

	# ---- Teams query and dataframe ----
	teams_data = run_query(
		"""
            SELECT t.logo, form, t.team, clean_sheets, penalties_scored, penalties_missed, average_goals, win_streak
            FROM `premier_league_dataset.teams` AS t
            LEFT JOIN `premier_league_dataset.standings` AS s
            ON t.team = s.Team
            ORDER BY s.rank;
        """
	)

	teams_df = pd.DataFrame(data=teams_data)

	# --- Top Scorers query and dataframe ----
	top_scorers_data = run_query(
		"""
            SELECT *
            FROM `premier_league_dataset.top_scorers`
            ORDER BY Goals DESC;
        """
	)

	top_scorers_df = pd.DataFrame(data=top_scorers_data)

	# --- News query and dataframe ----
	news_data = run_query(
		"""
            SELECT *
            FROM `premier_league_dataset.news`
            ORDER BY published_at DESC;
        """
	)

	news_df = pd.DataFrame(data=news_data)

	# Fetching the minimun round number from the 'rounds' table.
	min_round_row = run_query(
		"""
            SELECT MIN(round) AS round
            FROM `premier_league_dataset.current_round`;
        """
	)
	# Converting tuple to list.
	min_round = min_round_row[0]["round"]

	# Fetching the maximum round number from the 'rounds' table.
	max_round_row = run_query(
		"""
            SELECT MAX(round) AS round 
            FROM `cloud-data-infrastructure.premier_league_dataset.current_round`;
        """
	)
	# Converting tuple to list.
	max_round = max_round_row[0]["round"]

	league_statistics = run_query(
		"""
            SELECT 
                SUM(goals_for) AS league_goals_scored,
                SUM(penalties_scored) AS league_penalties_scored,
                SUM(clean_sheets) AS league_clean_sheets     
            FROM premier_league_dataset.teams AS t
            JOIN premier_league_dataset.standings AS s
            ON t.team_id = s.team_id;
        """
	)

	league_statistics_df = pd.DataFrame(data=league_statistics)

	return (
		stadiums_df,
		standings_df,
		status_df,
		teams_df,
		top_scorers_df,
		news_df,
		min_round,
		max_round,
		league_statistics_df,
	)


def streamlit_app():
	# Calling varibles from database connection functions.
	(
		stadiums_df,
		standings_df,
		status_df,
		teams_df,
		top_scorers_df,
		news_df,
		min_round,
		max_round,
		league_statistics_df,
	) = bigquery_connection()
	firestore_database = firestore_connection()

	logo = st.secrets["elements"]["logo_image"]

	col1, col = st.columns((2, 4))
	# Premier League logo.
	with st.container():
		col1.image(logo)

	# Title.
	col1, col = st.columns((9, 1))
	with st.container():
		col1.title("Premier League Statistics / 2023-24")

		st.subheader(f"Current Round: {max_round}")

		# Get the current date
		def get_suffix(day):
			if 10 < day % 100 < 20:
				suffix = "th"
			else:
				suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
			return suffix

		current_date = datetime.now()
		day = current_date.day
		suffix = get_suffix(day)
		formatted_day = str(day).lstrip("0")
		formatted_date = (
			current_date.strftime("%B ")
			+ formatted_day
			+ suffix
			+ current_date.strftime(", %Y")
		)

		st.write(f"{formatted_date}")

	def toast():
		msg = st.toast("Loading Data...", icon="⏳")
		time.sleep(3)
		msg.toast(":green[Data Loaded!]", icon="✅")

	toast()

	# Tab menu.
	tab1, tab2, tab3, tab4, tab5 = st.tabs(
		["Standings & Overview", "Top Teams & Scorers", "Fixtures", "News", "About"]
	)

	# --------- Overview Tab ---------
	with tab1:
		st.subheader("League Statistics")
		col1, col2, col3, col4 = st.columns(4)

		# Average goals scored column.
		with col1:
			teams_df_average_goals = teams_df.sort_values(
				by=["average_goals"], ascending=False
			)

			average_goals_df = pd.DataFrame(
				{
					"Average Goals": [
						teams_df_average_goals.iloc[0][6],
						teams_df_average_goals.iloc[1][6],
						teams_df_average_goals.iloc[2][6],
						teams_df_average_goals.iloc[3][6],
						teams_df_average_goals.iloc[4][6],
					],
					"Team": [
						teams_df_average_goals.iloc[0][2],
						teams_df_average_goals.iloc[1][2],
						teams_df_average_goals.iloc[2][2],
						teams_df_average_goals.iloc[3][2],
						teams_df_average_goals.iloc[4][2],
					],
				}
			)

			st.dataframe(
				average_goals_df,
				column_config={
					"Average Goals": st.column_config.ProgressColumn(
						"Average Goals",
						help="The Average Goals Scored by Each Team.",
						format="%f",
						min_value=0,
						max_value=20,
					),
				},
				hide_index=True,
			)

		with col2:
			teams_df_penalties_scored = teams_df.sort_values(
				by=["penalties_scored"], ascending=False
			)

			penalties_scored_df = pd.DataFrame(
				{
					"Penalties Scored": [
						teams_df_penalties_scored.iloc[0][4],
						teams_df_penalties_scored.iloc[1][4],
						teams_df_penalties_scored.iloc[2][4],
						teams_df_penalties_scored.iloc[3][4],
						teams_df_penalties_scored.iloc[4][4],
					],
					"Team": [
						teams_df_penalties_scored.iloc[0][2],
						teams_df_penalties_scored.iloc[1][2],
						teams_df_penalties_scored.iloc[2][2],
						teams_df_penalties_scored.iloc[3][2],
						teams_df_penalties_scored.iloc[4][2],
					],
				}
			)

			st.dataframe(
				penalties_scored_df,
				column_config={
					"Penalties Scored": st.column_config.ProgressColumn(
						"Penalties Scored",
						help="The Amount of Penalties Scored by Each Team.",
						format="%d",
						min_value=0,
						max_value=20,
					),
				},
				hide_index=True,
			)

		with col3:
			teams_df_win_streak = teams_df.sort_values(
				by=["win_streak"], ascending=False
			)

			win_streak_df = pd.DataFrame(
				{
					"Win Streak": [
						teams_df_win_streak.iloc[0][7],
						teams_df_win_streak.iloc[1][7],
						teams_df_win_streak.iloc[2][7],
						teams_df_win_streak.iloc[3][7],
						teams_df_win_streak.iloc[4][7],
					],
					"Team": [
						teams_df_win_streak.iloc[0][2],
						teams_df_win_streak.iloc[1][2],
						teams_df_win_streak.iloc[2][2],
						teams_df_win_streak.iloc[3][2],
						teams_df_win_streak.iloc[4][2],
					],
				}
			)

			st.dataframe(
				win_streak_df,
				column_config={
					"Win Streak": st.column_config.ProgressColumn(
						"Win Streak",
						help="The Win Streak by Each Team.",
						format="%d",
						min_value=0,
						max_value=15,
					),
				},
				hide_index=True,
			)

		with col4:
			st.markdown("**League Statistics**")

			with st.container():
				league_statistics_df = pd.DataFrame(
					{
						"labels": ["Goals Scored", "Penalties Scored", "Clean Sheets"],
						"metrics": [
							league_statistics_df.iloc[0][0],
							league_statistics_df.iloc[0][1],
							league_statistics_df.iloc[0][2],
						],
					}
				)

				st.dataframe(
					league_statistics_df,
					column_config={
						"metrics": st.column_config.NumberColumn(
							"Amount",
							help="The Amount of Goals, Penalties Scored, and Clean Sheets in the League.",
							min_value=0,
							max_value=1000,
							step=1,
						),
						"labels": st.column_config.TextColumn(
							"Metric",
						),
					},
					hide_index=True,
				)

		# Function to create the standings table (dataframe).
		def standings_table() -> DeltaGenerator:
			st.subheader("Current Standings")

			standings_table = st.dataframe(
				standings_df.style.set_table_styles(
					[{"selector": "th", "props": [("background-color", "yellow")]}]
				),
				column_config={
					"logo": st.column_config.ImageColumn("Icon", width="small"),
					"rank": "Rank",
					"team": "Club",
					"points": "Points",
					"wins": "Wins",
					"draws": "Draws",
					"loses": "Loses",
					"goals_for": "Goals For",
					"goals_against": "Goals Against",
					"goal_difference": "Goal Difference",
				},
				hide_index=True,
				use_container_width=True,
			)

			return standings_table

		standings_table()

		stadium_map_instance.create_stadium_map(stadiums_df)

		social_media_section.display()

	# --------- Statistics Tab ---------
	with tab2:
		st.subheader("Top 5 Teams")

		col1, col2, col3, col4, col5 = st.columns(5)

		# First top team.
		with col1:
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(teams_df.iloc[0][0])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>1st / Form (Last 5):</b> {((teams_df.iloc[0][1])[-5:])}</p>",
				f"<p style='text-align: center;'><b>Clean Sheets:</b> {(teams_df.iloc[0][3])}</p>",
				f"<p style='text-align: center;'><b>Penalties Scored:</b> {(teams_df.iloc[0][4])}</p>",
				f"<p style='text-align: center;'><b>Penalties Missed:</b> {(teams_df.iloc[0][5])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col2:
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(teams_df.iloc[1][0])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>1st / Form (Last 5):</b> {((teams_df.iloc[1][1])[-5:])}</p>",
				f"<p style='text-align: center;'><b>Clean Sheets:</b> {(teams_df.iloc[1][3])}</p>",
				f"<p style='text-align: center;'><b>Penalties Scored:</b> {(teams_df.iloc[1][4])}</p>",
				f"<p style='text-align: center;'><b>Penalties Missed:</b> {(teams_df.iloc[1][5])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col3:
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(teams_df.iloc[2][0])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>1st / Form (Last 5):</b> {((teams_df.iloc[2][1])[-5:])}</p>",
				f"<p style='text-align: center;'><b>Clean Sheets:</b> {(teams_df.iloc[2][3])}</p>",
				f"<p style='text-align: center;'><b>Penalties Scored:</b> {(teams_df.iloc[2][4])}</p>",
				f"<p style='text-align: center;'><b>Penalties Missed:</b> {(teams_df.iloc[2][5])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col4:
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(teams_df.iloc[3][0])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>1st / Form (Last 5):</b> {((teams_df.iloc[3][1])[-5:])}</p>",
				f"<p style='text-align: center;'><b>Clean Sheets:</b> {(teams_df.iloc[3][3])}</p>",
				f"<p style='text-align: center;'><b>Penalties Scored:</b> {(teams_df.iloc[3][4])}</p>",
				f"<p style='text-align: center;'><b>Penalties Missed:</b> {(teams_df.iloc[3][5])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col5:
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(teams_df.iloc[4][0])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>1st / Form (Last 5):</b> {((teams_df.iloc[4][1])[-5:])}</p>",
				f"<p style='text-align: center;'><b>Clean Sheets:</b> {(teams_df.iloc[4][3])}</p>",
				f"<p style='text-align: center;'><b>Penalties Scored:</b> {(teams_df.iloc[4][4])}</p>",
				f"<p style='text-align: center;'><b>Penalties Missed:</b> {(teams_df.iloc[4][5])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		team_forms = [[], [], [], [], []]

		forms = [
			teams_df.iloc[0][1],
			teams_df.iloc[1][1],
			teams_df.iloc[2][1],
			teams_df.iloc[3][1],
			teams_df.iloc[4][1],
		]

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

		# Legend for line chart.
		headers = [
			str(standings_df.iloc[0][2]),
			str(standings_df.iloc[1][2]),
			str(standings_df.iloc[2][2]),
			str(standings_df.iloc[3][2]),
			str(standings_df.iloc[4][2]),
		]

		zipped = list(
			zip(
				team_forms[0],
				team_forms[1],
				team_forms[2],
				team_forms[3],
				team_forms[4],
			)
		)

		df = pd.DataFrame(zipped, columns=headers)

		st.subheader("")

		st.subheader("Point Progression thoughout the Season")

		st.line_chart(data=df)

		st.subheader("Top 5 Scorers")

		col1, col2, col3, col4, col5 = st.columns(5)

		with col1:
			# First top scorer.
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(top_scorers_df.iloc[0][5])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>{(top_scorers_df.iloc[0][0])}</b></p>",
				f"<p style='text-align: center;'><b>Goals:</b> {(top_scorers_df.iloc[0][1])}</p>",
				f"<p style='text-align: center;'><b>Assists:</b> {(top_scorers_df.iloc[0][3])}</p>",
				f"<p style='text-align: center;'><b>Team:</b> {(top_scorers_df.iloc[0][2])}</p>",
				f"<p style='text-align: center;'><b>Nationality:</b> {(top_scorers_df.iloc[0][4])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col2:
			# Second top scorer.
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(top_scorers_df.iloc[1][5])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>{(top_scorers_df.iloc[1][0])}</b></p>",
				f"<p style='text-align: center;'><b>Goals:</b> {(top_scorers_df.iloc[1][1])}</p>",
				f"<p style='text-align: center;'><b>Assists:</b> {(top_scorers_df.iloc[1][3])}</p>",
				f"<p style='text-align: center;'><b>Team:</b> {(top_scorers_df.iloc[1][2])}</p>",
				f"<p style='text-align: center;'><b>Nationality:</b> {(top_scorers_df.iloc[1][4])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col3:
			# Third top scorer.
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(top_scorers_df.iloc[2][5])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>{(top_scorers_df.iloc[2][0])}</b></p>",
				f"<p style='text-align: center;'><b>Goals:</b> {(top_scorers_df.iloc[2][1])}</p>",
				f"<p style='text-align: center;'><b>Assists:</b> {(top_scorers_df.iloc[2][3])}</p>",
				f"<p style='text-align: center;'><b>Team:</b> {(top_scorers_df.iloc[2][2])}</p>",
				f"<p style='text-align: center;'><b>Nationality:</b> {(top_scorers_df.iloc[2][4])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col4:
			# Fourth top scorer.
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(top_scorers_df.iloc[3][5])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>{(top_scorers_df.iloc[3][0])}</b></p>",
				f"<p style='text-align: center;'><b>Goals:</b> {(top_scorers_df.iloc[3][1])}</p>",
				f"<p style='text-align: center;'><b>Assists:</b> {(top_scorers_df.iloc[3][3])}</p>",
				f"<p style='text-align: center;'><b>Team:</b> {(top_scorers_df.iloc[3][2])}</p>",
				f"<p style='text-align: center;'><b>Nationality:</b> {(top_scorers_df.iloc[3][4])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with col5:
			# Fifth top scorer.
			markdown_list = [
				f"<img style='display: block; margin-left: auto; margin-right: auto; width: 150px;' src='{(top_scorers_df.iloc[4][5])}'/>",
				f"<p style='text-align: center; padding-top: 0.8rem;'><b>{(top_scorers_df.iloc[4][0])}</b></p>",
				f"<p style='text-align: center;'><b>Goals:</b> {(top_scorers_df.iloc[4][1])}</p>",
				f"<p style='text-align: center;'><b>Assists:</b> {(top_scorers_df.iloc[4][3])}</p>",
				f"<p style='text-align: center;'><b>Team:</b> {(top_scorers_df.iloc[4][2])}</p>",
				f"<p style='text-align: center;'><b>Nationality:</b> {(top_scorers_df.iloc[4][4])}</p>",
			]

			for item in markdown_list:
				st.markdown(item, unsafe_allow_html=True)

		with st.container():
			st.subheader("")
			st.subheader("Forms for the Rest of the League")

			col1, col2, col3, col4, col5 = st.columns(5)

			with col1:
				markdown_list = [
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[5][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>6th / {((teams_df.iloc[5][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[10][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>11th / {((teams_df.iloc[10][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[15][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>16th / {((teams_df.iloc[15][1])[-5:])}</p>",
				]

				for item in markdown_list:
					st.markdown(item, unsafe_allow_html=True)

			with col2:
				markdown_list = [
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[6][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>7th / {((teams_df.iloc[6][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[11][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>12th / {((teams_df.iloc[11][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[16][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>17th / {((teams_df.iloc[16][1])[-5:])}</p>",
				]

				for item in markdown_list:
					st.markdown(item, unsafe_allow_html=True)

			with col3:
				markdown_list = [
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[7][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>8th / {((teams_df.iloc[7][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[12][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>13th / {((teams_df.iloc[12][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[17][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>18th / {((teams_df.iloc[17][1])[-5:])}</p>",
				]

				for item in markdown_list:
					st.markdown(item, unsafe_allow_html=True)

			with col4:
				markdown_list = [
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[8][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>9th / {((teams_df.iloc[8][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[13][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>14th / {((teams_df.iloc[13][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[18][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>19th / {((teams_df.iloc[18][1])[-5:])}</p>",
				]

				for item in markdown_list:
					st.markdown(item, unsafe_allow_html=True)

			with col5:
				markdown_list = [
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[9][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>10th / {((teams_df.iloc[9][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[14][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>15th / {((teams_df.iloc[14][1])[-5:])}</p>",
					f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{(teams_df.iloc[19][0])}'/>",
					f"<p style='text-align: center; padding-top: 0.8rem;'>20th / {((teams_df.iloc[19][1])[-5:])}</p>",
				]

				for item in markdown_list:
					st.markdown(item, unsafe_allow_html=True)

		# Social media icons section.
		social_media_section.display()

	# --------- Fixtures Tab ---------
	with tab3:
		st.subheader("Fixtures per Round")

		# Looping through each collection to get each round.
		round_count = int(max_round)
		while round_count >= int(min_round):
			# Function to pull collection and documents.
			def firestore_pull():
				# Calling each document in the collection in ascending order by date.
				collection_ref = firestore_database.collection(
					f"Regular Season - {round_count}"
				)
				query = collection_ref.order_by(
					"date", direction=firestore.Query.ASCENDING
				)
				results = query.stream()

				# Setting an empty list. This list will contain each fixtures' details that can later be called by referecing its index.
				documents = []

				# Iterating through the query results to get the document ID (ex: 'Manchester City vs Burnley') and its data.
				for doc in results:
					document_dict = {"id": doc.id, "data": doc.to_dict()}
					documents.append(document_dict)

				# Retrieving and formatting match date.
				match_date = [
					datetime.strptime(
						documents[count]["data"]["date"], "%Y-%m-%dT%H:%M:%S+00:00"
					)
					.strftime("%B %d{}, %Y - %H:%M")
					.format(
						"th"
						if 4
						<= int(
							datetime.strptime(
								documents[count]["data"]["date"],
								"%Y-%m-%dT%H:%M:%S+00:00",
							).strftime("%d")
						)
						<= 20
						else {1: "st", 2: "nd", 3: "rd"}.get(
							int(
								datetime.strptime(
									documents[count]["data"]["date"],
									"%Y-%m-%dT%H:%M:%S+00:00",
								).strftime("%d")
							)
							% 10,
							"th",
						)
					)
					for count in range(10)
				]

				# Retrieving away and home goals for each match.
				away_goals = [
					documents[count]["data"]["goals"]["away"] for count in range(10)
				]
				home_goals = [
					documents[count]["data"]["goals"]["home"] for count in range(10)
				]

				# Retrieving away and home team for each match.
				away_team = [
					documents[count]["data"]["teams"]["away"]["name"]
					for count in range(10)
				]
				home_team = [
					documents[count]["data"]["teams"]["home"]["name"]
					for count in range(10)
				]

				# Retrieving away and home logo for each team.
				away_logo = [
					documents[count]["data"]["teams"]["away"]["logo"]
					for count in range(10)
				]
				home_logo = [
					documents[count]["data"]["teams"]["home"]["logo"]
					for count in range(10)
				]

				return (
					match_date,
					away_goals,
					home_goals,
					away_team,
					home_team,
					away_logo,
					home_logo,
				)

			# Placing data in an expander.
			with st.expander(f"Round {round_count}"):
				(
					match_date,
					away_goals,
					home_goals,
					away_team,
					home_team,
					away_logo,
					home_logo,
				) = firestore_pull()

				count = 0
				while count < 10:
					# Creating a container for each match.
					with st.container():
						col1, col2, col3, col4, col5 = st.columns(5)

						with col1:
							st.write("")

						# Home teams
						with col2:
							st.markdown(
								f"<h3 style='text-align: center;'>{home_goals[count]}</h3>",
								unsafe_allow_html=True,
							)
							st.markdown(
								f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{home_logo[count]}'/>",
								unsafe_allow_html=True,
							)
							st.write("")
							st.write("")

						# Match date
						with col3:
							st.write("")
							st.markdown(
								"<p style='text-align: center;'><b>Match Date & Time</b></p>",
								unsafe_allow_html=True,
							)
							st.markdown(
								f"<p style='text-align: center;'>{match_date[count]}</p>",
								unsafe_allow_html=True,
							)
							st.markdown(
								f"<p style='text-align: center;'>{home_team[count]} vs. {away_team[count]}</p>",
								unsafe_allow_html=True,
							)

						# Away teams
						with col4:
							st.markdown(
								f"<h3 style='text-align: center;'>{away_goals[count]}</h3>",
								unsafe_allow_html=True,
							)
							st.markdown(
								f"<img style='display: block; margin-left: auto; margin-right: auto; width: 75px;' src='{away_logo[count]}'/>",
								unsafe_allow_html=True,
							)
							st.write("")
							st.write("")

						with col5:
							st.write("")

					count += 1

					st.divider()

			round_count -= 1

		# Social media icons section.
		social_media_section.display()

	# --------- About Tab ---------
	with tab4:
		st.header("Recent News")
		col1, col2, col3, col4 = st.columns(4)

		with col1:
			with st.container():
				try:
					st.image(news_df.iloc[0][2], use_column_width=True)
					st.subheader(news_df.iloc[0][0])
					st.write(f"Publish time: {news_df.iloc[0][3]}")
					st.markdown(
						f"<a href={(news_df.iloc[0][1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col2:
			with st.container():
				try:
					st.image(news_df.iloc[1][2], use_column_width=True)
					st.subheader(news_df.iloc[1][0])
					st.write(f"Publish time: {news_df.iloc[1][3]}")
					st.markdown(
						f"<a href={(news_df.iloc[1][1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col3:
			with st.container():
				try:
					st.image(news_df.iloc[2][2], use_column_width=True)
					st.subheader(news_df.iloc[2][0])
					st.write(f"Publish time: {news_df.iloc[2][3]}")
					st.markdown(
						f"<a href={(news_df.iloc[2][1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col4:
			with st.container():
				try:
					st.image(news_df.iloc[3][2], use_column_width=True)
					st.subheader(news_df.iloc[3][0])
					st.write(f"Publish time: {news_df.iloc[3][3]}")
					st.markdown(
						f"<a href={(news_df.iloc[3][1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		# Social media icons section.
		social_media_section.display()

	with tab5:
		# About section.
		about_section.display()

		# Social media icons section.
		social_media_section.display()


if __name__ == "__main__":
	streamlit_app()
