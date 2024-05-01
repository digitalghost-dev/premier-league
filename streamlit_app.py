import os
import time

from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# Importing classes from components/ directory.
from components.about_section import AboutSection
from components.fixtures_section import FixturesSection
from components.highlights_section import HighlightsSection
from components.injuries_section import InjuriesSection
from components.league_form_section import LeagueFormsSection
from components.news_section import NewsSection
from components.point_progression_section import PointProgressionSection
from components.point_slider_section import PointSliderSection
from components.social_media_section import SocialMediaSection
from components.squads_section import SquadSection
from components.stadiums_map_section import StadiumMapSection
from components.stock_section import StockSection
from components.top_scorers_section import TopScorersSection
from components.top_teams_section import TopTeamsSection
from components.connections import (
	firestore_connection,
	get_highlights,
	get_injuries,
	get_league_statistics,
	get_max_round,
	get_min_round,
	get_news,
	get_squads,
	get_stadiums,
	get_standings,
	get_stocks,
	get_teams,
	get_top_scorers,
)

import google.auth

project_id = "cloud-data-infrastructure"
os.environ["GCLOUD_PROJECT"] = project_id
credentials, project_id = google.auth.default()

st.set_page_config(page_title="Streamlit: Premier League", layout="wide")


def streamlit_app():
	# Get the dataframes.
	firestore_database = firestore_connection()
	highlights_df = get_highlights()
	injuries_df = get_injuries()
	league_statistics_df = get_league_statistics()
	max_round = get_max_round()
	min_round = get_min_round()
	news_df = get_news()
	squads_df = get_squads()
	standings_df = get_standings()
	stadiums_df = get_stadiums()
	stocks_df = get_stocks()
	teams_df = get_teams()
	top_scorers_df = get_top_scorers()

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
		formatted_date = current_date.strftime("%B ") + formatted_day + suffix + current_date.strftime(", %Y")

		st.write(f"{formatted_date}")

	# Tab menu.
	tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
		[
			"Standings & Overview",
			"Teams Statistics",
			"Players & Injuries",
			"Fixtures",
			"Squads",
			"News & Hightlights",
			"Manchester United Stock (Beta)",
			"About",
		]
	)

	# --------- Overview Tab ---------
	# Tab 1 holds the following sections: [League Statistics, Current Standings, Location of Stadiums].
	with tab1:
		st.subheader("League Statistics")
		col1, col2, col3, col4 = st.columns(4)

		# Average goals scored column.
		with col1:
			teams_df_average_goals = teams_df.sort_values(by=["average_goals"], ascending=False)
			max_average_goals = teams_df_average_goals.iloc[0, 6]

			average_goals_df = pd.DataFrame(
				{
					"Average Goals": [
						max_average_goals,
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
						max_value=int(round(max_average_goals, 2)) * 2,
					),
				},
				hide_index=True,
			)

		with col2:
			teams_df_penalties_scored = teams_df.sort_values(by=["penalties_scored"], ascending=False)
			max_penalties_scored = teams_df_penalties_scored.iloc[0, 4]

			penalties_scored_df = pd.DataFrame(
				{
					"Penalties Scored": [
						max_penalties_scored,
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
						max_value=int(max_penalties_scored) * 2,
					),
				},
				hide_index=True,
			)

		with col3:
			teams_df_win_streak = teams_df.sort_values(by=["win_streak"], ascending=False)
			max_win_streak = teams_df_win_streak.iloc[0, 7]

			win_streak_df = pd.DataFrame(
				{
					"Biggest Win Streak": [
						max_win_streak,
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
						max_value=int(max_win_streak) * 2,
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
				standings_df.style.set_table_styles([{"selector": "th", "props": [("background-color", "yellow")]}]),
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

		# Stadiums
		stadium_map_section = StadiumMapSection()
		stadium_map_section.display(stadiums_df)

	# --------- Team Statistics Tab ---------
	# Tab 2 holds the following sections: [Top Teams, Point Progression, Top Scorers, League Forms].
	with tab2:
		def top_teams_func():
			top_teams_section = TopTeamsSection(teams_df)
			with st.container():
				top_teams_section.display()

		def point_progression_func():
			point_progression_section = PointProgressionSection(teams_df, standings_df)
			with st.container():
				point_progression_section.display()

		@st.experimental_fragment
		def point_slider_func():
			point_slider_section = PointSliderSection(standings_df)
			with st.container():
				point_slider_section.display()

		def league_forms_func():
			league_forms_section = LeagueFormsSection(teams_df)
			with st.container():
				league_forms_section.display()

		top_teams_func()
		point_progression_func()
		point_slider_func()
		league_forms_func()

	# --------- Player Statistics Tab ---------
	# Tab 3 holds the following sections: [Player Statistics].
	with tab3:

		def top_scorers_func():
			top_scorers_section = TopScorersSection(top_scorers_df)
			with st.container():
				top_scorers_section.display()

		@st.experimental_fragment
		def injuries_func():
			injuries_section = InjuriesSection(injuries_df)
			with st.container():
				injuries_section.display()

		top_scorers_func()
		injuries_func()

	# --------- Fixtures Tab ---------
	# Tab 4 holds the following sections: [Fixtures].
	with tab4:
		# Fixtures section.
		fixtures_section.display()

	# --------- Squads Tab ---------
	# Tab 5 holds the following sections: [Squads].
	with tab5:
		st.subheader("Team Squads")
		st.markdown("**Note:** Double click on the player's photo to expand it.")

		@st.experimental_fragment
		def squads_func():
			squads = SquadSection(squads_df)

			col1, _, _ = st.columns(3)
			with col1:
				option = st.selectbox(
					index=None,
					label="Use the dropdown menu to select a team:",
					options=squads.teams,
					placeholder="Please make a selection",
				)
			if option:
				selected_team_logo = teams_df[teams_df["team"] == option]["logo"].iloc[0]
				st.image(selected_team_logo, width=75)
				squads.display(option)

		squads_func()

	# --------- News Tab ---------
	# Tab 6 holds the following sections: [News, Highlights].
	with tab6:
		with st.container():
			NewsSection(news_df).display()

		with st.container():
			HighlightsSection(highlights_df).display_first_row()
			HighlightsSection(highlights_df).display_second_row()

	# --------- Stock Tab ---------
	# Tab 7 holds the following sections: [Stock Price].
	with tab7:
		stock_section = StockSection(stocks_df)
		stock_section.display()

	# --------- About Tab ---------
	# Tab 8 holds the following sections: [About].
	with tab8:
		# About
		about_section = AboutSection()
		about_section.display()

	# Social Media
	social_media_section = SocialMediaSection()
	social_media_section.display()


if __name__ == "__main__":
	streamlit_app()
