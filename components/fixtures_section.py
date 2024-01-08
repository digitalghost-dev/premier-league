import streamlit as st
from firebase_admin import firestore  # type: ignore
from datetime import datetime

from typing import List
from typing import Tuple


class FixturesSection:
	def __init__(self, firestore_database, max_round: int, min_round: int):
		self.firestore_database = firestore_database
		self.max_round = int(max_round)
		self.min_round = int(min_round)

	def firestore_pull(
		self, round_count
	) -> Tuple[List[str], List[int], List[int], List[str], List[str], List[str], List[str]]:
		# Calling each document in the collection in ascending order by date.
		collection_ref = self.firestore_database.collection(f"Regular Season - {round_count}")
		query = collection_ref.order_by("date", direction=firestore.Query.ASCENDING)
		results = query.stream()

		# Setting an empty list. This list will contain each fixture's details that can later be called by referencing its index.
		documents = []

		# Iterating through the query results to get the document ID (e.g., 'Manchester City vs Burnley') and its data.
		for doc in results:
			document_dict = {"id": doc.id, "data": doc.to_dict()}
			documents.append(document_dict)

		# Retrieving and formatting match date.
		match_date = [
			datetime.strptime(documents[count]["data"]["date"], "%Y-%m-%dT%H:%M:%S+00:00")
			.strftime("%B %d{}, %Y - %H:%M")
			.format(
				"th"
				if 4
				<= int(datetime.strptime(documents[count]["data"]["date"], "%Y-%m-%dT%H:%M:%S+00:00").strftime("%d"))
				<= 20
				else {1: "st", 2: "nd", 3: "rd"}.get(
					int(datetime.strptime(documents[count]["data"]["date"], "%Y-%m-%dT%H:%M:%S+00:00").strftime("%d"))
					% 10,
					"th",
				)
			)
			for count in range(10)
		]

		# Retrieving away and home goals for each match.
		away_goals = [documents[count]["data"]["goals"]["away"] for count in range(10)]
		home_goals = [documents[count]["data"]["goals"]["home"] for count in range(10)]

		# Retrieving away and home team for each match.
		away_team = [documents[count]["data"]["teams"]["away"]["name"] for count in range(10)]
		home_team = [documents[count]["data"]["teams"]["home"]["name"] for count in range(10)]

		# Retrieving away and home logo for each team.
		away_logo = [documents[count]["data"]["teams"]["away"]["logo"] for count in range(10)]
		home_logo = [documents[count]["data"]["teams"]["home"]["logo"] for count in range(10)]

		return (
			match_date,
			away_goals,
			home_goals,
			away_team,
			home_team,
			away_logo,
			home_logo,
		)

	def display(self):
		round_count = self.max_round
		st.subheader("Fixtures")

		while round_count >= self.min_round:
			with st.expander(f"Round {round_count}"):
				(
					match_date,
					away_goals,
					home_goals,
					away_team,
					home_team,
					away_logo,
					home_logo,
				) = self.firestore_pull(round_count)

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

			round_count -= 1
