from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# Importing classes from components/ directory.
from components.about_section import AboutSection
from components.fixtures_section import FixturesSection
from components.league_form_section import LeagueFormsSection
from components.point_progression_section import PointProgressionSection
from components.stadiums_map_section import StadiumMapSection
from components.social_media_section import SocialMediaSection
from components.top_scorers_section import TopScorersSection
from components.top_teams_section import TopTeamsSection
from components.connections import (
	firestore_connection,
	get_standings,
	get_stadiums,
	get_teams,
	get_top_scorers,
	get_news,
	get_league_statistics,
	get_min_round,
	get_max_round,
)

st.set_page_config(page_title="Streamlit: Premier League", layout="wide")


def streamlit_app():
	# Get the dataframes.
	standings_df = get_standings()
	stadiums_df = get_stadiums()
	teams_df = get_teams()
	top_scorers_df = get_top_scorers()
	news_df = get_news()
	league_statistics_df = get_league_statistics()
	min_round = get_min_round()
	max_round = get_max_round()
	firestore_database = firestore_connection()
	fixtures_section = FixturesSection(firestore_database, max_round, min_round)

	# Image, title, and subheader.
	with st.container():
		st.markdown(
			'<img height="140" width="140" src="https://cdn.simpleicons.org/premierleague/340040"/>',
			unsafe_allow_html=True,
		)
		st.title("Premier League Statistics / 2023-24")
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

	# Tab menu.
	tab1, tab2, tab3, tab4, tab5 = st.tabs(
		["Standings & Overview", "Top Teams & Scorers", "Fixtures", "News", "About"]
	)

	# --------- Overview Tab ---------
	# Tab 1 holds the following sections: [League Statistics, Current Standings, Location of Stadiums].
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
						teams_df_average_goals.iloc[0, 6],
						teams_df_average_goals.iloc[1, 6],
						teams_df_average_goals.iloc[2, 6],
						teams_df_average_goals.iloc[3, 6],
						teams_df_average_goals.iloc[4, 6],
					],
					"Team": [
						teams_df_average_goals.iloc[0, 2],
						teams_df_average_goals.iloc[1, 2],
						teams_df_average_goals.iloc[2, 2],
						teams_df_average_goals.iloc[3, 2],
						teams_df_average_goals.iloc[4, 2],
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
						max_value=8,
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
						teams_df_penalties_scored.iloc[0, 4],
						teams_df_penalties_scored.iloc[1, 4],
						teams_df_penalties_scored.iloc[2, 4],
						teams_df_penalties_scored.iloc[3, 4],
						teams_df_penalties_scored.iloc[4, 4],
					],
					"Team": [
						teams_df_penalties_scored.iloc[0, 2],
						teams_df_penalties_scored.iloc[1, 2],
						teams_df_penalties_scored.iloc[2, 2],
						teams_df_penalties_scored.iloc[3, 2],
						teams_df_penalties_scored.iloc[4, 2],
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
					"Biggest Win Streak": [
						teams_df_win_streak.iloc[0, 7],
						teams_df_win_streak.iloc[1, 7],
						teams_df_win_streak.iloc[2, 7],
						teams_df_win_streak.iloc[3, 7],
						teams_df_win_streak.iloc[4, 7],
					],
					"Team": [
						teams_df_win_streak.iloc[0, 2],
						teams_df_win_streak.iloc[1, 2],
						teams_df_win_streak.iloc[2, 2],
						teams_df_win_streak.iloc[3, 2],
						teams_df_win_streak.iloc[4, 2],
					],
				}
			)

			st.dataframe(
				win_streak_df,
				column_config={
					"Biggest Win Streak": st.column_config.ProgressColumn(
						"Biggest Win Streak",
						help="The Biggest Win Streak by Each Team.",
						format="%d",
						min_value=0,
						max_value=10,
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
							league_statistics_df.iloc[0, 0],
							league_statistics_df.iloc[0, 1],
							league_statistics_df.iloc[0, 2],
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
					"points": "Points",
					"team": "Club",
					"games_played": "Games Played",
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

		# Stadiums.
		stadium_map_section = StadiumMapSection()
		stadium_map_section.display(stadiums_df)

	# --------- Statistics Tab ---------
	# Tab 2 holds the following sections: [Top Teams, Point Progression, Top Scorers, League Forms].
	with tab2:
		with st.container():
			sections = [
				(TopTeamsSection, teams_df, None),
				(PointProgressionSection, teams_df, standings_df),
				(TopScorersSection, top_scorers_df, None),
				(LeagueFormsSection, teams_df, None),
			]

			first_section = True
			for section_class, dataframe_1, dataframe_2 in sections:
				if not first_section:
					st.subheader("")
				else:
					first_section = False

				if dataframe_2 is not None:
					section = section_class(dataframe_1, dataframe_2)
				else:
					section = section_class(dataframe_1)
				section.display()

	# --------- Fixtures Tab ---------
	# Tab 3 holds the following sections: [Fixtures].
	with tab3:
		# Fixtures section.
		fixtures_section.display()

	# --------- News Tab ---------
	# Tab 4 holds the following sections: [News].
	with tab4:
		st.header("Recent News")
		col1, col2, col3, col4 = st.columns(4)

		with col1:
			with st.container():
				try:
					st.image(news_df.iloc[0, 2], use_column_width=True)
					st.subheader(news_df.iloc[0, 0])
					st.write(f"Publish time: {news_df.iloc[0, 3]}")
					st.markdown(
						f"<a href={(news_df.iloc[0, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col2:
			with st.container():
				try:
					st.image(news_df.iloc[1, 2], use_column_width=True)
					st.subheader(news_df.iloc[1, 0])
					st.write(f"Publish time: {news_df.iloc[1, 3]}")
					st.markdown(
						f"<a href={(news_df.iloc[1, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col3:
			with st.container():
				try:
					st.image(news_df.iloc[2, 2], use_column_width=True)
					st.subheader(news_df.iloc[2, 0])
					st.write(f"Publish time: {news_df.iloc[2, 3]}")
					st.markdown(
						f"<a href={(news_df.iloc[2, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

		with col4:
			with st.container():
				try:
					st.image(news_df.iloc[3, 2], use_column_width=True)
					st.subheader(news_df.iloc[3, 0])
					st.write(f"Publish time: {news_df.iloc[3, 3]}")
					st.markdown(
						f"<a href={(news_df.iloc[3, 1])}>Read More</a>",
						unsafe_allow_html=True,
					)
				except IndexError:
					pass

	# --------- About Tab ---------
	# Tab 5 holds the following sections: [About].
	with tab5:
		# About
		about_section = AboutSection()
		about_section.display()

	# Social Media
	social_media_section = SocialMediaSection()
	social_media_section.display()


if __name__ == "__main__":
	streamlit_app()
