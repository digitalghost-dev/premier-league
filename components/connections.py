import firebase_admin  # type: ignore
import pandas as pd
import streamlit as st
from firebase_admin import firestore  # type: ignore
from google.cloud import bigquery
from google.oauth2 import service_account  # type: ignore


@st.cache_resource
def firestore_connection() -> firestore.Client:
	credentials = service_account.Credentials.from_service_account_info(
		st.secrets["gcp_service_account"]
	)
	if not firebase_admin._apps:
		firebase_admin.initialize_app()

	return firestore.Client(credentials=credentials)


@st.cache_data(ttl=600)
def run_query(query):
	credentials = service_account.Credentials.from_service_account_info(
		st.secrets["gcp_service_account"]
	)
	query_job = bigquery.Client(credentials=credentials).query(query)
	raw_data = query_job.result()
	data = [dict(data) for data in raw_data]
	return data


@st.cache_resource
def get_standings() -> pd.DataFrame:
	standings_data = run_query(
		"""
            SELECT rank, logo, team, points, wins, draws, loses, goals_for, goals_against, goal_difference
            FROM `premier_league_dataset.standings`
			ORDER BY rank ASC;
        """
	)
	return pd.DataFrame(data=standings_data)


@st.cache_resource
def get_stadiums() -> pd.DataFrame:
	stadiums_data = run_query(
		"""
            SELECT team, stadium, latitude, longitude
            FROM `premier_league_dataset.stadiums`;
        """
	)
	return pd.DataFrame(data=stadiums_data)


@st.cache_resource
def get_teams() -> pd.DataFrame:
	teams_data = run_query(
		"""
            SELECT t.logo, form, t.team, clean_sheets, penalties_scored, penalties_missed, average_goals, win_streak
            FROM `premier_league_dataset.teams` AS t
            LEFT JOIN `premier_league_dataset.standings` AS s
            ON t.team = s.Team
            ORDER BY s.rank;
        """
	)
	return pd.DataFrame(data=teams_data)


@st.cache_resource
def get_top_scorers() -> pd.DataFrame:
	top_scorers_data = run_query(
		"""
            SELECT *
            FROM `premier_league_dataset.top_scorers`
            ORDER BY Goals DESC;
        """
	)
	return pd.DataFrame(data=top_scorers_data)


@st.cache_resource
def get_news() -> pd.DataFrame:
	news_data = run_query(
		"""
            SELECT *
            FROM `premier_league_dataset.news`
            ORDER BY published_at DESC;
        """
	)
	return pd.DataFrame(data=news_data)


@st.cache_resource
def get_league_statistics() -> pd.DataFrame:
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
	return pd.DataFrame(data=league_statistics)


@st.cache_resource
def get_min_round() -> int:
	min_round_row = run_query(
		"""
            SELECT MIN(round) AS round
            FROM `premier_league_dataset.current_round`;
        """
	)
	min_round_df = pd.DataFrame(data=min_round_row)
	min_round = min_round_df["round"][0]
	return min_round


@st.cache_resource
def get_max_round() -> int:
	max_round_row = run_query(
		"""
            SELECT MAX(round) AS round 
            FROM `premier_league_dataset.current_round`;
        """
	)
	max_round_row = pd.DataFrame(data=max_round_row)
	max_round = max_round_row["round"][0]
	return max_round
