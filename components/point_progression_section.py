import pandas as pd
import streamlit as st


class PointProgressionSection:
	def __init__(self, teams_df, standings_df):
		self.teams_df = teams_df
		self.standings_df = standings_df

	def calculate_points(self):
		team_forms = [[], [], [], [], []]
		forms = [self.teams_df.iloc[i, 1] for i in range(5)]

		for count, form in enumerate(forms):
			points = 0
			for char in form:
				if char == "W":
					points += 3
				elif char == "D":
					points += 1
				else:
					points += 0

				team_forms[count].append(points)

		return team_forms

	def create_dataframe(self, team_forms):
		headers = [str(self.standings_df.iloc[i, 2]) for i in range(5)]
		zipped = list(zip(*team_forms))  # Transpose the list of lists
		return pd.DataFrame(zipped, columns=headers)

	def display(self):
		team_forms = self.calculate_points()
		df = self.create_dataframe(team_forms)

		st.subheader("Point Progression throughout the Season")
		st.line_chart(data=df)
